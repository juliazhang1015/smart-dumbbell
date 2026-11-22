# SmartDumbbell bench firmware

Zoe Wang's sketch for the soldered board (PR #15, 2026-11-18), tidied on 2026-11-19 by Hanson He: the plain and BLE copies were merged into one file behind `USE_BLE`, the backup `.txt` was dropped (git history is the backup), and the fixes listed below were applied. It descends from `firmware/demo/smart_dumbbell_demo.ino` (Julia Zhang, 2026-11-08).

Status 2026-11-21: with `COUNT_GATE 1` (the default) the classifier now confirms every rep before it is counted (section "Model confirmation of reps"). Compiles in all four builds (`USE_BLE` 0/1 × `COUNT_GATE` 0/1). First board check the same day, board held in the hand, not on a dumbbell (`tests/results/2026-11-21_count-gate-handheld.md`): 23 of 23 complete curls counted, 2 curls during which the hand hit a laptop rejected, 0 reps during shaking, lateral and front raises. Not yet tested on the assembled dumbbell.

Status 2026-11-19 (second revision): the curl/idle/other classifier now runs on the board in shadow mode and the counter prints every swing for per-user calibration. Both builds compile for `arduino:esp32:nano_nora` (`USE_BLE 0`: Flash 788 kB / 25 %, static RAM 67.7 kB / 20 %; `USE_BLE 1`: 1378 kB / 43 %, 88.6 kB / 27 %); `firmware/classifier` and `firmware/app` still compile with the new weights. The rep rule was replayed offline on the P01/P02 recordings (table below). **Not yet run on hardware since these edits** — flash, press `?` on the serial monitor, and check the three module flags before trusting anything else.

## Build

`#define USE_BLE 1` at the top of the sketch. `0` gives the Wi-Fi AP + HTTP build only (the interface in `docs/specification.md`, FR-11/12); `1` adds a BLE GATT notify characteristic. Both radios run at once in the BLE build.

```bash
arduino-cli compile --fqbn arduino:esp32:nano_nora firmware/SmartDumbbell
arduino-cli upload  --fqbn arduino:esp32:nano_nora -p /dev/cu.usbmodem<id> firmware/SmartDumbbell
```

Libraries: Adafruit LSM6DS, Adafruit SSD1306 / GFX / BusIO, SparkFun MAX3010x (`MAX30105.h`, `heartRate.h`); BLE comes with the ESP32 core. `classifier.h`, `model_weights.h` and `selftest.h` are copies of `firmware/classifier/` — regenerate there (see `ml/model-card.md`) and copy, do not edit here.

## Wiring assumed by the code

| Device | Pin | Notes |
|---|---|---|
| LSM6DSOX, MAX30102, OLED | A4 SDA, A5 SCL, 3V3, GND | I2C 0x6A / 0x57 / 0x3C, bus at 400 kHz |
| Button | D2 → button → GND | internal pull-up |
| Buzzer | D5 | 80 ms pulse on every state change and counted rep |
| LED | D7 | on while RUNNING |

Button: short press = start / pause / resume, hold ≥ 1.2 s = end. A new session resets reps and active time.

## Outputs

- Serial 115200: `session,state,active_ms,reps,bpm,label` every 250 ms; `C,<t_ms>,<label>,<conf>,<inference_us>` once per second (classifier, `ml/workplan.md` section 4); `SWING,<t_ms>,<deg>,rep=N,p_curl=P | rejected=<label>,p_curl=P | small | timeout` every time the counter settles a candidate (`p_curl` is the model's curl probability for the 2 s ending at that rep, −1 when not computed); `SELFTEST,PASS|FAIL,...` once at boot; send `?` to print module flags, the late-sample count and an I2C scan.
- Wi-Fi AP `SmartDumbbell` / `curl198demo`: `http://192.168.4.1/` shows the live row and offers a CSV download (columns `session,state,active_ms,reps,bpm,label`); `/sample` returns the raw row.
- BLE (`USE_BLE 1`): device `SmartDumbbell`, service `823ef401-…`, characteristic `823ef402-…` (read + notify), 17-byte little-endian packet: `u8 version=1, u8 state (0 Ready 1 Running 2 Paused 3 Done), u32 session, u32 active_ms, u32 reps, u16 bpm (0 = unavailable), u8 label (0 curl 1 idle 2 other, 255 none yet)`, updated every 250 ms. No receiver exists in this repo yet.

## Classifier

The IMU is now read on a 104 Hz schedule (`±4 g`, `±500 dps`, the recording settings) into a 2 s ring buffer; once per second `clf_features` + `clf_infer` from `classifier.h` produce a label and confidence. The label is shown on the OLED's last line (`ML: curl 93%`), appended to the serial / CSV row and the BLE packet, and printed as a `C,...` line. This periodic label does not change the count; with `COUNT_GATE 1` a separate inference at each rep does (next section). At boot the sketch runs the same self-test as `firmware/classifier` and prints `SELFTEST,PASS,...,features+inference_us=N`; a build with these weights printed PASS and about 2.2 ms on 2026-11-21 (`ml/model-card.md`). The model, its data (5 participants, mount v1 and v2) and its known failures are described in `ml/model-card.md` — read the Limits section before claiming anything about it.

## Model confirmation of reps (`COUNT_GATE`, 2026-11-21)

With `COUNT_GATE 1`, when the counter finds a complete swing (swing ≥ `SWING_MIN_DEG`, back within `RETURN_FRAC`), `gateAccept()` classifies the 2 s ending at that sample and the rep counts only if the label is `curl`; otherwise the sketch prints `SWING,...,rejected=other|idle,...` and the count stays. If fewer than 2 s have been buffered since boot, the rep is accepted. The extra inference takes about the same 2.2 ms as the periodic one. `COUNT_GATE 0` restores the previous behaviour exactly (label shown, never changes the count).

Why at the rep and not the last once-per-second label: that label is up to 1 s old, so its window can end before the rep does. Replay with `ml/tools/replay_count_gate.py` (Python port of this counter at 104 Hz, `SWING_MIN_DEG` 60°, each file classified by the leave-one-participant-out model that has not seen its participant):

| Files (reference reps) | Swing gate only | + last periodic label | + model at the rep (`COUNT_GATE 1`) |
|---|---|---|---|
| 12 curl files with a reference (223) | 218 | 212 | **217** |
| 5 other_mixed (0) | 26 | 4 | **1** |
| 3 partial_mixed with a reference (27 complete) | 53 | 50 | 52 |

- Reps counted during other movement (lifting, carrying, lateral and front raises, shaking) drop from 26 to 1 (the 1 is in `P05_other_mixed_01`); one complete curl is lost (`P02_curl_fast_01`, p_curl 0.06).
- **Half curls are not rejected by the model**: `partial` recordings are labelled `curl` for training (`ml/data-protocol.md` section 3). They are still the job of `SWING_MIN_DEG`, calibrated per user (next section).
- The P03 curl files (listed in `data/sessions/excluded.csv`) are hardly counted in any mode; their swings of about 45° are below the 60° gate before the model is asked.
- Limits: offline replay of recordings on two mount versions, not the enclosure; reference counts are partly observer-adjusted or IMU-inferred (`sessions.csv`); the exclusion list was chosen after a first evaluation on the same participants. On the board, the 2 s before the first rep of a session include whatever happened before the button press.

## Calibrating the swing threshold for a user

`SWING_MIN_DEG` is per user. Flash, start a session, have the user do ten full-range curls at their normal pace, and read the `SWING,<t>,<deg>,rep=N` lines: take the median swing and set `SWING_MIN_DEG` to about 0.7 × that value, re-flash, then do ten half curls and check they print `small`. Write the value and the user code in the test record. The default 60° counts every complete curl but also half curls.

## Rep rule and what it does on the recordings

Gyro X (the handle axis) in rad/s, polled every 10 ms. A rep starts when |gx| > 0.9, needs an opposite stroke (gx·sign < −0.9 after 200 ms), then speed < 0.35 after 450 ms. Added on 2026-11-19: the angle is integrated from the start of the rep; a rep counts only if the swing reached `SWING_MIN_DEG` (60°) and the angle is back within `RETURN_FRAC` (0.5) of that swing — otherwise the sketch keeps waiting for the real return (an overshoot bounce at the top no longer ends the rep) or, if the swing was small, drops it. The abandon timeout went from 5 s to 8 s because P02 slow curls already take 5.0 s per cycle.

Replay of exactly this state machine on `data/sessions` (scratch script, 104 Hz CSV → 10 ms polling, gx in dps → rad/s):

| File | Labelled complete reps | PR #15 rule | With swing gate |
|---|---|---|---|
| P01 curl fast / normal / slow | 26 / 17 / 13 | 26 / 17 / 13 | 26 / 17 / 13 |
| P02 curl fast / normal / slow | 23 / 9 / 8 | 22 / 9 / 9 | 21 / 9 / 7 |
| P01 partial_mixed | 11 | 20 | 18 |
| P02 partial_mixed | 8 | 19 | 17 |
| P01 other_mixed | 0 | 47 | 9 |
| P02 other_mixed | 0 | 85 | 3 |

So with the 60° default: clean curls within ±2, unrelated movement mostly rejected, **half-range reps are still counted** (P02's half curls swing 90–100°, more than P01's full curls at 105–120°, so one fixed angle cannot separate them). With a per-user threshold of 0.7 × the full swing the same replay gives:

| File | Labelled | 60° | per user (P01 80°, P02 105°) |
|---|---|---|---|
| P01 curl fast / normal / slow | 26 / 17 / 13 | 26 / 17 / 13 | 26 / 17 / 13 |
| P01 partial_mixed | 11 | 18 | 10 |
| P01 other_mixed | 0 | 9 | 2 |
| P02 curl fast / normal / slow | 23 / 9 / 8 | 21 / 9 / 7 | 21 / 9 / 7 |
| P02 partial_mixed | 8 | 17 | 8 |
| P02 other_mixed | 0 | 3 | 0 |

Above about 0.75 × the full swing, fast complete curls start to be dropped. A calibrated threshold is a single-user result and must be reported as such; it is not the general AT-02/AT-03 evidence.

## Other changes on 2026-11-19

- OLED constructor `(128,64,&Wire,-1,400000UL,400000UL)`: the library default `clkAfter=100000` left the shared bus at 100 kHz for the IMU and MAX30102 after every refresh (measured 2026-11-06 in `firmware/app`). `display()` still blocks ~30 ms every 250 ms; the chunked transfer in `firmware/app/app.ino` is the next step if IMU samples turn out to be missed.
- BPM is the mean of the last 4 valid beat intervals (shown after 2), reset on finger loss or state change, instead of a single interval.
- BLE packet fields are copied through explicit `uint32_t` / `uint16_t` locals.

## IMU sampling after a loop stall (2026-11-21)

Review on PR #16: the IMU was read on a fixed 104 Hz timer. After the loop stalled (Wi-Fi, BLE, an OLED refresh), the timer was behind and `serviceIMU` read the sensor several times back to back. The sensor only updates every 9.6 ms, so those reads returned the same sample: duplicate rows in the classifier window, and the rep counter integrated the same rotation once per read at a fixed `1/104 s`.

Now `serviceIMU` reads only when the gyro data-ready flag is set (`imu.gyroscopeAvailable()`), polling every 0.3 ms from 1 ms before a sample is due, and the counter integrates over the real time since the previous sample (capped at 0.1 s). A stall now loses samples instead of duplicating them; `imu_late` counts each gap longer than 1.5 sample periods. `?` prints `imu_late`, `imu_samples` and `t_ms`, so two reports give the actual read rate.

Measured on the board on 2026-11-21 (`tests/results/2026-11-21_count-gate-handheld.md`): 96.3 reads per second and about 3 `imu_late` gaps per second, so about 7 % of samples are still lost to loop stalls (source not identified). The stall comparison below has not been run. The planned check: a test-only copy of the old and the new sketch, each with a 50 ms stall once per second and a counter of exactly repeated samples; expected duplicates > 0 for the old code, 0 for the new, about 99 reads/s and one `imu_late` per second for the new.

## Known limits

- The model confirmation is validated offline and in one hand-held check (`tests/results/2026-11-21_count-gate-handheld.md`), not on the assembled dumbbell. A rep the model wrongly calls `other` or `idle` is lost; watch the `rejected=` lines when testing on the assembled dumbbell, and set `COUNT_GATE 0` if they reject real curls.
- Samples lost in a stall are not filled in: the classifier window then covers slightly more than 2 s. `imu_late` shows how often this happens.
- Heart rate has no validity flag beyond "0 = none"; the earlier static test read 9–14 bpm high with this library (`docs/handoff.md`).
- The AP password is in the source. It is a demo credential, not a secret, but change it before any public demo.
- BLE is not in `docs/specification.md`; see the open item in `docs/decisions.md`.
