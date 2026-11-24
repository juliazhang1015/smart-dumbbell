# Live dashboard (macOS) with AI coach

Status 2026-11-24: runs on a Mac against `firmware/SmartDumbbell` from `main` (`USE_BLE 1`). Checked on the bench board: the Mac connects over Bluetooth, receives a 17-byte packet every 250 ms, and the AI coach panel shows Claude feedback. Not tested on Windows or Linux (the Bluetooth bridge is macOS only).

The page shows repetitions, active time, cadence, the estimated heart rate with its trend, the share of on-device movement labels (curl / idle / other), and an **AI coach** panel with short feedback on the current set. It is a successor to [`../web/index.html`](../web/index.html), which uses Web Bluetooth in Chrome or Edge and does not need this server.

## How it works

```text
dumbbell --BLE notify, 17 bytes / 250 ms--> SmartDumbbellBLE (Swift, CoreBluetooth)
                                                |  stdout "PACKET:<base64>"
                                                v
                                           server.py (127.0.0.1:8001)
                                             /live     latest packet     <-- index.html polls every 250 ms
                                             /insight  latest AI reply   <-- index.html polls every 2 s
                                                |
                                           ai_coach.py --> Claude API (claude-opus-5-5)
```

- `SmartDumbbellBLE.swift` scans for a device that advertises service `823ef401-1d82-41f6-b689-68aedcbb1960` or is named `SmartDumbbell`, subscribes to characteristic `823ef402-…` and prints each packet. It also prints every step (scanning, seen, connected, subscribed, errors); `server.py` shows those lines in the terminal and appends them to `bridge.log` in this folder (ignored by git).
- `server.py` compiles the Swift bridge at start-up, serves the page and the two JSON endpoints, and listens on the loopback interface only.
- `ai_coach.py` keeps the active samples of the current session, and every 15 s while a set is running (and once when it is paused or finished) sends a summary to Claude: active time, repetitions, cadence, reps in the last 15 s, seconds between recent reps, heart-rate estimate (median, range, share of valid readings) and label shares. Nothing else is sent: no names, participant codes or raw sensor data.

The packet layout is the one in `firmware/SmartDumbbell/SmartDumbbell.ino` (`publishBluetooth`): u8 version 1, u8 state, u32 session, u32 active ms, u32 reps, u16 bpm (0 = none), u8 label (0 curl, 1 idle, 2 other, 255 none yet).

## Run

1. Put the Claude API key in `~/.zshrc` (never in this folder or the repository):

   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

   Without a key the dashboard still runs; the AI panel says "AI unavailable".
2. Double-click `start-dashboard.command` (or run it from Terminal). It reads the key from `~/.zshrc`, starts `server.py` with Python 3.12 and the `anthropic` package through `uv` (the system `python3` is 3.9, too old for the SDK; without `uv` it falls back to `python3` and the AI panel stays off), and opens `http://127.0.0.1:8001/`.
3. The first time, allow Terminal to use Bluetooth. If the terminal prints `Bluetooth state: 3`, enable Terminal under System Settings → Privacy & Security → Bluetooth.
4. Keep the terminal window open. Closing it stops the server.

Requirements: macOS with Xcode command line tools (`swiftc`), `uv` (`brew install uv`), internet access for the AI coach.

## Things that go wrong

- **"No SmartDumbbell after 15 s" in the terminal**: the board accepts one Bluetooth connection at a time and stops advertising while connected. Close any other phone, browser tab or computer connected to it, or reset the board.
- **AI panel "AI unavailable"**: the line under it gives the reason (no key, rate limit, network). The dashboard keeps working; the last good reply stays on screen.

## AI coach: model, cost, limits

- Model `claude-opus-5-5` at `effort: low`, with server-side refusal fallback (`fallbacks: "default"`), so a declined request is re-run on a fallback model instead of failing. Change `MODEL` or `INTERVAL_S` at the top of `ai_coach.py`.
- About 1–2 k input tokens per update, one update per 15 s of running: roughly USD 0.01 per update, a few dollars per hour of continuous sets.
- The system prompt treats heart rate as a rough prototype estimate: no medical interpretation, no advice to change weight, sets or plan (that stays with the exercise specialist). Above an estimated 150 BPM it suggests a short rest. This is prototype feedback, not a clinical tool, and its advice has not been evaluated with users.
