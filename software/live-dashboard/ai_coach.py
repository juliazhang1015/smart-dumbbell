"""Live AI coach: turns the dumbbell's BLE packets into short Claude feedback for the dashboard.

The browser never sees the API key. server.py feeds every packet to Coach.add(); a worker thread
calls Claude every INTERVAL_S seconds while a set is running, and once more when the session is
paused or finished. The latest reply is served at /insight.
"""
import base64
import json
import statistics
import struct
import threading
import time
from collections import deque

MODEL = "claude-opus-5-5"
INTERVAL_S = 15          # seconds between updates while running
STATES = ["Ready", "Running", "Paused", "Done"]
LABELS = ["curl", "idle", "other"]

SYSTEM = (
    "You are the live coach panel of a prototype smart dumbbell. Its users are participants of "
    "CCCARE exercise programs at the University of Waterloo who do prescribed bicep curls at home. "
    "Each request gives you the device's current session numbers as JSON: active time, repetitions "
    "counted by the device, cadence, an optical heart-rate estimate with how often it was valid, and "
    "the on-device movement label (curl, idle, other).\n\n"
    "Write feedback the person reads at a glance while exercising: one or two short sentences, at most "
    "40 words, plain text, no lists or emoji. Be specific to the numbers, for example pace compared "
    "with earlier in the set, steady or uneven rhythm, a long pause, or movement the device did not "
    "count as a curl. Use only the numbers given; if something is missing, do not guess it.\n\n"
    "The heart rate is a rough prototype estimate, not a medical measurement. Mention it only as an "
    "estimate, never interpret it clinically, and never suggest changing the prescribed weight, sets "
    "or plan: the person's exercise specialist decides those. If the estimate is above 150 BPM, "
    "suggest a short rest and checking in with their specialist if they feel unwell.\n\n"
    "When the event is 'paused' or 'finished', give a two- or three-sentence summary of the set "
    "instead (at most 60 words)."
)


def decode(b64):
    raw = base64.b64decode(b64)
    if len(raw) not in (16, 17) or raw[0] != 1 or raw[1] >= len(STATES):
        return None
    _, state, session, ms, reps, bpm = struct.unpack_from("<BBIIIH", raw)
    label = LABELS[raw[16]] if len(raw) == 17 and raw[16] < len(LABELS) else None
    return {"state": STATES[state], "session": session, "ms": ms, "reps": reps,
            "bpm": bpm or None, "label": label}


class Coach:
    def __init__(self):
        self.lock = threading.Lock()
        self.samples = deque(maxlen=1200)   # active samples of the current session (~5 min at 4 Hz)
        self.latest = None
        self.rep_times = deque(maxlen=12)   # active ms at which the rep count went up
        self.result = {"status": "waiting", "text": "Waiting for a session to start.", "at": None}
        self.pending_event = None            # "paused" / "finished" summary owed
        self.last_call = 0.0
        self.last_called_on = None           # (session, ms, reps) of the last request
        self.client = None

    # ---- packet side (called from the BLE reader thread) ----
    def add(self, b64):
        p = decode(b64)
        if p is None:
            return
        with self.lock:
            prev = self.latest
            if prev is None or p["session"] != prev["session"] or p["ms"] < prev["ms"]:
                self.samples.clear()
                self.rep_times.clear()
                self.pending_event = None
            if p["state"] == "Running" and (prev is None or p["ms"] > prev["ms"]):
                self.samples.append(p)
            if prev is not None and p["reps"] > prev["reps"]:
                self.rep_times.append(p["ms"])
            if prev is not None and prev["state"] == "Running" and p["state"] in ("Paused", "Done"):
                self.pending_event = "paused" if p["state"] == "Paused" else "finished"
            self.latest = p

    def snapshot(self):
        with self.lock:
            out = dict(self.result)
        out["age_s"] = None if out.get("at") is None else round(time.time() - out["at"])
        return out

    # ---- analysis side ----
    def facts(self, event):
        p, s = self.latest, list(self.samples)
        ms = p["ms"]
        recent = [x for x in s if x["ms"] >= ms - 60000]
        bpms = [x["bpm"] for x in recent if x["bpm"]]
        last30 = [x for x in s if x["ms"] >= ms - 30000 and x["label"]]
        older = [x for x in s if x["ms"] <= ms - 15000]
        reps_15s = p["reps"] - older[-1]["reps"] if older else None
        gaps = [round((b - a) / 1000, 1) for a, b in zip(self.rep_times, list(self.rep_times)[1:])]
        return {
            "event": event,
            "state": p["state"],
            "active_time_s": round(ms / 1000),
            "reps": p["reps"],
            "cadence_whole_set_reps_per_min": round(60000 * p["reps"] / ms, 1) if ms >= 5000 else None,
            "reps_in_last_15_active_s": reps_15s,
            "seconds_between_recent_reps": gaps[-6:],
            "seconds_since_last_rep": round((ms - self.rep_times[-1]) / 1000) if self.rep_times else None,
            "heart_rate_estimate_last_60s": None if not bpms else {
                "median_bpm": round(statistics.median(bpms)), "min_bpm": min(bpms), "max_bpm": max(bpms),
                "valid_share": round(len(bpms) / len(recent), 2)},
            "movement_label_share_last_30s": None if not last30 else {
                k: round(sum(x["label"] == k for x in last30) / len(last30), 2) for k in LABELS},
            "current_label": p["label"],
        }

    def due(self):
        """Return the event to analyse now, or None."""
        p = self.latest
        if p is None:
            return None
        if self.pending_event:
            return self.pending_event
        key = (p["session"], p["ms"], p["reps"])
        if (p["state"] == "Running" and p["ms"] >= 5000 and key != self.last_called_on
                and time.monotonic() - self.last_call >= INTERVAL_S):
            return "update"
        return None

    def ask(self, facts):
        try:
            import anthropic   # imported here so the dashboard still runs without the SDK
        except ImportError:
            return "error", "Anthropic SDK not installed: start the dashboard with start-dashboard.command (needs uv)."
        if self.client is None:
            self.client = anthropic.Anthropic()
        try:
            r = self.client.beta.messages.create(
                model=MODEL,
                max_tokens=2000,
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",          # re-run on a fallback model if this one declines
                output_config={"effort": "low"},
                system=SYSTEM,
                messages=[{"role": "user", "content": json.dumps(facts)}],
            )
        except anthropic.AuthenticationError:
            return "error", "API key missing or invalid. Set ANTHROPIC_API_KEY and restart the dashboard."
        except anthropic.PermissionDeniedError:
            return "error", "This API key may not use " + MODEL + "."
        except anthropic.RateLimitError:
            return "error", "Rate limited by the API; the next update will retry."
        except anthropic.APIStatusError as e:
            return "error", "API error %s; the next update will retry." % e.status_code
        except anthropic.APIConnectionError:
            return "error", "No connection to the Claude API. Check the internet connection."
        except Exception as e:  # e.g. no credentials configured at all
            msg = str(e)
            if "api_key" in msg or "authentication" in msg.lower() or "auth_token" in msg:
                return "error", "No API key found. Set ANTHROPIC_API_KEY and restart the dashboard."
            return "error", "AI analysis failed: " + type(e).__name__
        if r.stop_reason == "refusal":
            return "error", "The model declined this update."
        text = " ".join(b.text for b in r.content if b.type == "text").strip()
        return ("ok", text) if text else ("error", "Empty reply from the model.")

    def run(self):
        while True:
            time.sleep(1)
            with self.lock:
                event = self.due()
                if event is None:
                    continue
                facts = self.facts(event)
                p = self.latest
                self.pending_event = None
                self.last_call = time.monotonic()
                self.last_called_on = (p["session"], p["ms"], p["reps"])
                if self.result.get("status") == "waiting":
                    self.result = {"status": "thinking", "text": "Analysing the set…", "at": None}
            status, text = self.ask(facts)
            with self.lock:
                if status == "ok" or self.result.get("status") != "ok":
                    self.result = {"status": status, "text": text, "at": time.time(),
                                   "event": event, "session": p["session"], "model": MODEL}
                else:   # keep the last good reply visible, flag the failure
                    self.result = dict(self.result, warning=text)
                if status == "ok":
                    self.result.pop("warning", None)

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()
