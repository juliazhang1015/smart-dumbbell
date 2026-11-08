# Demo plan and schedule to 25 November (draft, 2026-11-08)

Status date: 2026-11-08. This file answers two questions: **what has to work on the final-symposium day**, and **what each week between now and then is for**. Sources: the course material (`LAB 3/F26 ECE 198 Project Overview.pdf` and the saved course page, both outside this repository), `docs/handoff.md`, `ml/workplan.md` and `tests/results/`. The "status" table is a snapshot and will age.

## 1. What the course asks for

From the project overview PDF and the course page:

| Date | Event | Course wording, summarised |
|---|---|---|
| **9–11 Nov (time to be announced; ours is Tue 10 Nov 09:10)** | In-person project update presentation | 7 minutes of progress plus 8 minutes of Q&A with the teaching team per the instructor announcement (the project overview PDF said 5 + 5). **Bring the prototype**; a laptop or tablet may be used. "The teaching team will be looking for progress, but we aren't expecting a finished project." Also a chance to ask questions. |
| **23 Nov (8-stream) / 25 Nov (4-stream)** | Final project symposium | Demonstrate the prototype to stakeholders, the teaching team and the other groups, in the Ideas Clinic (PSE-1427). "More details will be available as we get closer." We plan for 25 Nov. |
| 8 Dec | Individual term reflection | Individual, outside this file. |

The course page says there is no defined grading scheme; late deliverables lose 10 % per day, a late presenter loses 50 % at once, an unexcused absence scores 0. So the update presentation must have **everyone present and on time**; incomplete content is acceptable.

No rubric for the symposium was found. The likely format is a table session: visitors walk up, watch one complete run of the device and ask a few questions. The demo therefore has to be **short, repeatable and recoverable**, not a one-shot stage performance.

## 2. What must work on 25 November

Three tiers. **Tier 1 is the floor**; without it there is nothing to show. Tier 2 is the goal, tier 3 is extra.

### Tier 1: required (no demo without it)

One complete table-side run, under 90 seconds, repeatable back to back:

1. The dumbbell is an **assembled physical device** that can be picked up and curled without parts coming loose (the 100-rep check of AT-10 done at least once).
2. One button press starts a session; the display shows `RUN 0/10`.
3. Ten curls; the count follows; at 10 the display inverts (FR-10) and keeps counting.
4. A shake, or picking the dumbbell up and putting it down, **does not count** (FR-06). If this is not reliable, leave it out of the live run but be ready to explain it.
5. A finger on the grip sensor produces a heart-rate value within a few seconds; removing it shows `HR --` within 2 s (FR-08, AT-06). The app firmware currently clears after 3 s (`HR_STALE_MS 3000`); set it to 2000 ms before running AT-06.
6. A long press ends the session; the laptop next to the device shows the set's count and duration and a CSV is written (FR-11, FR-12).

Technical floor behind that: enclosure printed and assembled; the rep counter in `firmware/app` reliable on real curls (10 ± 1); Wi-Fi access point + `/status` endpoint + `software/data_logger.py` working together (or the BLE path once device-side firmware exists); the power bank runs the device for 10 minutes without switching itself off.

### Tier 2: goal (most of the MUST requirements in place)

- Classifier trained on real recordings and evaluated by person (AT-01), gating the counter on the device (FR-05): "a swing does not count" because of the model, not only thresholds.
- AT-02 (20 sets × 10 reps) and AT-03 (20 interference trials) run on the device and reported, pass or fail.
- AT-07 ten minutes without a reset; AT-08 thirty seconds offline and a consistent count after reconnecting.
- Target reps set from the computer and synced to the device (FR-01).

### Tier 3: extra

- Second-by-second comparison of in-motion heart rate against a reference device (AT-04, AT-05). Current judgement: unlikely to pass; **showing the comparison data honestly is worth more than pretending it passed.**
- Session summary and history view.
- Enclosure details: balance, charge-port opening in the end cap.

### What to bring on the day

The assembled dumbbell; a spare power bank or a USB cable as the fallback for power-bank auto-shutdown; the laptop (runs the logger; the dumbbell provides the hotspot); one poster page or slides (problem, approach, block diagram, test-result table, what is not done and why); a spare Nano ESP32 flashed with the same firmware (the board once stopped answering on USB on 6 Nov); a small screwdriver.

## 3. Status (2026-11-08)

| Item | State | Evidence |
|---|---|---|
| Electronics bring-up | Four I2C devices on one bus; IMU 104 Hz; OLED working | `tests/results/2026-11-03_*` |
| Integrated firmware `firmware/app` | Ran once on the board: button state machine, no lost IMU samples, 100 Hz pulse sampling, 2.3 ms inference | `tests/results/2026-11-06_app-v0-first-run.md` |
| Rep counting | Placeholder implementation, thresholds guessed, **not tested on a real curl** | same record, "not tested" |
| Classifier | Pipeline runs on synthetic data; **zero real recordings**; IMU mounting orientation not frozen | `data/sessions/sessions.csv` is empty |
| Heart rate | Module produces a signal; at rest the estimate is 9–14 bpm high; validity logic exists in firmware; in-motion untested | `docs/handoff.md`, known issues |
| Wi-Fi + logger | Access-point bring-up passed; `data_logger.py` tested against the mock only; firmware has **no** `/status` endpoint yet | `software/README.md` |
| Bluetooth dashboard | Web dashboard merged (8 Nov); no device-side firmware for its service yet | `software/web/index.html`, `software/README.md` |
| Enclosure | Concept CAD v0.1; layout proposal v0.2 (8 Nov); **no printed part** | `hardware/cad/`, `hardware/layout/` |
| Bench | Full-size breadboard failed; being rewired on a half-size board (8 Nov) | `hardware/wiring/halfboard-v1.png` |
| Acceptance tests | **No result for any of AT-01 to AT-10** | `tests/results/` |

In one sentence: every module works on its own and the integrated firmware ran once, but **everything that depends on real-person data (recordings, model, counter parameters, heart-rate accuracy) is still at zero**, and so is the enclosure. 17 days remain to 25 Nov.

## 4. Schedule, working backwards

Hard constraint from `ml/workplan.md`: **no model or parameter changes after 24 Nov.** The real development window therefore ends on 21 Nov; 22–24 Nov are for re-testing and rehearsal only.

### 8–11 Nov: revive the bench, prepare the update presentation

| Who | What | Done when |
|---|---|---|
| Hanson | Rewire the half-size breadboard; `bus_check` reports `rc=0` on all four addresses; flash `firmware/app` again | Serial header shows `oled 1 hr 1`, display is on |
| Hanson + Julia | **Freeze the IMU mounting orientation** (X along the grip, photo into `ml/data-protocol.md`), fix the 4517 to a dumbbell per `ml/figures/recording-rig-v1.png`, record the first 2–3 people with `04_imu_stream` | Files in `data/sessions/` |
| Julia | `ml/tools/offline_counter.py` counts reps from the recorded CSVs | Within ±1 on three curl recordings |
| Zoe | Run the power bank with Wi-Fi + OLED for 10 minutes and watch for auto-shutdown; borrow a heart-rate reference device | Record in `tests/results/` |
| Eric | First print from `hardware/layout/layout-v0.2.png` (right head and grip first) | Printed part in hand |
| All | **Update presentation, 7 minutes + 8 minutes Q&A**: `presentation/Smart_Dumbbell_Update_2026-11-10.pptx`, script in `docs/update-presentation-2026-11-10.md` | Rehearsed once |

Three questions for the teaching team at the update: (1) can the in-motion heart-rate requirement (FR-07 / AT-04 / AT-05) be restated as "in-motion readings when signal quality allows, guaranteed readings between sets"; (2) symposium format, time per visitor, table and power; (3) is a budget ceiling of CAD 200 acceptable.

### 12–16 Nov: first version of everything

| Who | What | Done when |
|---|---|---|
| Hanson | Record ≥ 4 people; first model from `train.py`, evaluated by person; `model-card.md` | A macro-F1 number exists, whatever it is |
| Julia | Counter parameters frozen; AT-02 (20 sets) and AT-03 (20 trials) offline; parameters moved into `firmware/app`'s `counterSample()` | Offline result table |
| Zoe | Replace the heart-rate detector (band-pass + peak picking or spectral), compare at rest against the reference; move the electronics from breadboard to perfboard with female headers (a breadboard does not fit the enclosure) | MAE at rest measured; perfboard hub soldered |
| Eric | Fit check of the printed parts: power bank, hub board, OLED window, button, grip sensor recess; second revision | Every module fits |
| Julia | Device-side interface for the computer: Wi-Fi hotspot + `/status`, `/target` per `software/README.md`, or the BLE service the dashboard expects; `data_logger.py` or the dashboard against real firmware | Real counts visible on the laptop |

### 17–21 Nov: integration and on-device tests

| Who | What | Done when |
|---|---|---|
| Hanson | Model header into `firmware/app`, `COUNT_GATE 1`; AT-01 record | On-device classification matches offline |
| Julia | AT-02, AT-03 repeated on the device; AT-08 disconnect/reconnect | Records in `tests/results/` |
| Zoe + Eric | Full assembly; the 100-rep check of AT-10; AT-07 ten-minute run | Device survives intact |
| All | Fix the demo script (the six steps of tier 1); everyone can run it | Script written into section 5 |

### 22–24 Nov: freeze, rehearse, materials

- Tag the firmware; flash two boards (main + spare).
- Rehearse the demo three times, timed; note every failure cause.
- Poster or slides: problem, approach, block diagram, schematic, test-result table (pass / fail / not tested with numbers for AT-01 to AT-10), what is not done and why.
- Charge the power bank; prepare USB power as fallback; spare cables.

### 25 Nov: symposium

Power up and run the full loop once before the visitors arrive.

## 5. Demo script (to be finalised by 21 Nov)

Placeholder. The six tier-1 steps are the draft. The final version states who operates, what is said, what the display should show, and what to do when a step fails.

## 6. Risks and fallbacks

| Risk | Likelihood | Fallback |
|---|---|---|
| Enclosure not printed or does not fit | Medium | Demo on the half-breadboard rig strapped to an ordinary dumbbell; show the CAD and the half-finished print on the table |
| Model does not train well | Medium | `COUNT_GATE 0`, demo with the counter only, and say the model is still being evaluated |
| In-motion heart rate inaccurate | High | Demonstrate the FR-08 behaviour (insufficient signal while moving, readings between sets); put the at-rest comparison data and the decision record on the poster |
| Wi-Fi fails on site | Low | The dumbbell is its own hotspot, independent of campus Wi-Fi; last resort is the USB serial link to the laptop |
| Power bank switches off under low load | Medium | Test before 11 Nov; otherwise power the device over USB from the laptop |
| Board stops answering on USB (happened once on 6 Nov) | Low | Spare board with the same firmware; know the RST / replug procedure |
| Parameters still changing after 24 Nov | High (from experience) | The workplan forbids it; the team holds each other to it |

## 7. Decisions still needed (most urgent first)

1. Who presents which slide on 10 Nov, and whether the bench rig comes along (depends on the rewiring being finished).
2. Whether FR-07 (in-motion heart rate) is restated, after asking the teaching team.
3. Buzzer or no buzzer, one button confirmed: the firmware is single-button, the specification and READMEs still say three.
4. Enclosure per layout v0.2 (110 mm heads, 360 mm overall) or the v0.1 size; how many balance washers fit under the 1 kg limit (see `hardware/layout/layout-v0.2.png`, note 4).
