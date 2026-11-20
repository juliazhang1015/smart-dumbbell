# SmartDumbbell bench firmware

Zoe Wang's sketch for the soldered board (PR #15, 2026-11-18), tidied on 2026-11-19 by Hanson He: the plain and BLE copies were merged into one file behind `USE_BLE`, the backup `.txt` was dropped (git history is the backup), and the fixes listed below were applied. It descends from `firmware/demo/smart_dumbbell_demo.ino` (Julia Zhang, 2026-11-08).

Status 2026-11-19: both builds compile for `arduino:esp32:nano_nora` (`USE_BLE 0`: Flash 778 kB / 24 %, static RAM 57.5 kB / 17 %; `USE_BLE 1`: 1368 kB / 43 %, 78.5 kB / 23 %). The rep rule was replayed offline on the P01/P02 recordings (table below). **Not yet run on hardware since these edits** — flash, press `?` on the serial monitor, and check the three module flags before trusting anything else.

## Build

`#define USE_BLE 1` at the top of the sketch. `0` gives the Wi-Fi AP + HTTP build only (the interface in `docs/specification.md`, FR-11/12); `1` adds a BLE GATT notify characteristic. Both radios run at once in the BLE build.

```bash
arduino-cli compile --fqbn arduino:esp32:nano_nora firmware/SmartDumbbell
arduino-cli upload  --fqbn arduino:esp32:nano_nora -p /dev/cu.usbmodem<id> firmware/SmartDumbbell
```

Libraries: Adafruit LSM6DS, Adafruit SSD1306 / GFX / BusIO, SparkFun MAX3010x (`MAX30105.h`, `heartRate.h`); BLE comes with the ESP32 core.

## Wiring assumed by the code

| Device | Pin | Notes |
|---|---|---|
| LSM6DSOX, MAX30102, OLED | A4 SDA, A5 SCL, 3V3, GND | I2C 0x6A / 0x57 / 0x3C, bus at 400 kHz |
| Button | D2 → button → GND | internal pull-up |
| Buzzer | D5 | 80 ms pulse on every state change and counted rep |
| LED | D7 | on while RUNNING |

Button: short press = start / pause / resume, hold ≥ 1.2 s = end. A new session resets reps and active time.

## Outputs

- Serial 115200: `session,state,active_ms,reps,bpm` every 250 ms; send `?` to print module flags and an I2C scan.
- Wi-Fi AP `SmartDumbbell` / `curl198demo`: `http://192.168.4.1/` shows the live row and offers a CSV download; `/sample` returns the raw row.
- BLE (`USE_BLE 1`): device `SmartDumbbell`, service `823ef401-…`, characteristic `823ef402-…` (read + notify), 16-byte little-endian packet: `u8 version=1, u8 state (0 Ready 1 Running 2 Paused 3 Done), u32 session, u32 active_ms, u32 reps, u16 bpm (0 = unavailable)`, updated every 250 ms. No receiver exists in this repo yet.

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

So: clean curls within ±2, unrelated movement mostly rejected, **half-range reps are still counted** (P02's half curls swing 90–100°, more than P01's full curls at 105–120°, so a fixed angle cannot separate them without per-user calibration or the classifier in `firmware/classifier`). AT-02/AT-03 are not met by this rule alone; it is a bench baseline, as the comment in the sketch says.

## Other changes on 2026-11-19

- OLED constructor `(128,64,&Wire,-1,400000UL,400000UL)`: the library default `clkAfter=100000` left the shared bus at 100 kHz for the IMU and MAX30102 after every refresh (measured 2026-11-06 in `firmware/app`). `display()` still blocks ~30 ms every 250 ms; the chunked transfer in `firmware/app/app.ino` is the next step if IMU samples turn out to be missed.
- BPM is the mean of the last 4 valid beat intervals (shown after 2), reset on finger loss or state change, instead of a single interval.
- BLE packet fields are copied through explicit `uint32_t` / `uint16_t` locals.

## Known limits

- No classifier: `curl` / `idle` / `other` is not evaluated, so counting while walking or shaking is only reduced, not prevented.
- Heart rate has no validity flag beyond "0 = none"; the earlier static test read 9–14 bpm high with this library (`docs/handoff.md`).
- The AP password is in the source. It is a demo credential, not a secret, but change it before any public demo.
- BLE is not in `docs/specification.md`; see the open item in `docs/decisions.md`.
