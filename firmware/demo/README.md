# Wi-Fi demo: pulse acquisition revision

This demo uses the existing Nano ESP32, MAX30102, LSM6DSOX and OLED wiring.
The rep counter and session controls are unchanged. This is a prototype pulse
estimator; accuracy during curls is **not yet measured**. Regular motion can
look like a pulse even when the interval checks pass. `Tracking` means the
heuristic accepted the signal, not that accuracy has been verified.

## Upload

Download/check out this branch. Keep `smart_dumbbell_demo.ino` and
`PulseTracker.h` together. Arduino IDE may ask to move the sketch into a folder
called `smart_dumbbell_demo`; copy the header into that folder too.
Select **Arduino Nano ESP32** and install these libraries using Library Manager:

- SparkFun MAX3010x Pulse and Proximity Sensor Library
- Adafruit LSM6DS (with dependencies)
- Adafruit SSD1306 (with dependencies)

Upload, open Serial Monitor at 115200 baud, and start a session with the button.
Connect to the SmartDumbbell Wi-Fi AP using the new password printed in Serial
Monitor at startup. The password changes on each restart; press reset with Serial
Monitor open if you missed it. This removes the shared password from the sketch.
The existing `/sample` response and downloaded five-column CSV are unchanged.
A new `/pulse-status` text endpoint reports acquisition status independently of
session state. Numerical session BPM is still blank outside Running.

## What changed

- Direct, checked FIFO reads in batches of up to five red/IR records avoid the
  SparkFun library's four-entry software ring. Do not use `ppg.check()`,
  `getIR()` or library FIFO getters alongside this acquisition path.
- Sample counting at 100 Hz measures beat intervals independently of loop,
  display and HTTP timing. Keep setup at 400 Hz with averaging of four.
- Baseline removal, low-pass filtering and an adaptive amplitude threshold
  replace the fixed-amplitude beat detector. Contact thresholds have separate
  on/off values to avoid flicker around one cutoff.
- Two consistent intervals are required for the first BPM, followed by a rolling
  three-interval mean. Accepted range is 40–200 BPM. Intervals differing by more
  than 25% suppress the estimate until consistency returns. This trades some
  response speed for fewer unstable readings; it is not an arrhythmia detector.
- No extra 1.5-second wait per session. Filtering runs continuously; first
  acquisition still needs 0.8 seconds of settling plus enough beats. At 60 BPM,
  allow approximately 3–5 seconds under a clean signal; verify on hardware.
- Contact loss, saturation, stale data, I2C errors and FIFO gaps clear the result.
  A loop gap of 300 ms resets acquisition before trusting buffered samples.
  Long HTTP stalls can still interrupt sensing; these are detected, not hidden.
- Red LED drive is disabled because only IR is used. IR current and ADC range
  retain their original settings; no untested automatic LED adjustment is used.

## Tune using measurements

Send `p` in Serial Monitor to toggle a diagnostic line every 250 ms:
`# HR <status> IR=<raw> AC=<filtered> envelope=<amplitude> gaps=<count>`.
Send `?` for the existing I2C scan (the scan can intentionally cause a sample gap).
Diagnostic lines are opt-in; ordinary serial CSV is unchanged.

1. Record IR with no finger, then with a still finger gently covering the optical
   window. Avoid pressing hard or letting room light directly reach the sensor.
2. `Place finger`: the default contact-on threshold is 10000 counts (off: 7000),
   instead of the old 50000. In `PulseTracker.h`, choose CONTACT_ON above the
   observed no-finger range and below the covered range; keep CONTACT_OFF lower.
   Defaults are starting values, not universal calibration. If the ranges overlap,
   improve mounting/light shielding before lowering thresholds further.
3. `Weak signal`: inspect the pulse envelope. MIN_AMPLITUDE defaults to 20 counts.
   Lower it only if recorded pulses are distinguishable from no-finger noise;
   lowering a threshold alone can create false readings.
4. `IR saturated`: raw IR is near the 18-bit limit. Reduce the setup LED power
   (currently 0x1F) and repeat the no-finger/contact checks.
5. `Hold steady`: the algorithm is collecting intervals or rejecting irregular
   ones. Check the optical contact during grip changes. It does not automatically
   reject all exercise, nor can it reliably distinguish periodic motion from pulse.
6. `I2C error`, `No samples`, `Sample gap` or `FIFO overflow`: check wiring and
   power, and compare operation with/without a browser connected. The `gaps`
   counter counts reset events, not the number of missing samples.

## Verification

Run the host checks from the repository root:

```sh
g++ -std=c++11 -Wall -Wextra -Werror tests/test_pulse_tracker.cpp -o /tmp/test_pulse_tracker
/tmp/test_pulse_tracker
```

The test uses synthetic waveforms, including a baseline below the old cutoff,
low amplitude with noise, 40–200 BPM, rate changes, contact loss, saturation,
constant input, stale pulse clearing, reset and batch-processing invariance.
These are algorithm tests, not sensor or clinical accuracy results.

On the board, compare old/new firmware using the same placement and synchronized
reference: 60 seconds still, then 60 seconds curling. Record first-reading delay,
valid-output coverage, BPM error and gap counts. Repeat with the OLED and browser
active; remove the finger, pause/resume, and reconnect the sensor. Confirm that
invalid readings become blank and reacquisition does not reuse old intervals.
Use the existing AT-04–AT-07 criteria; no acceptance target has changed.

### Revision checks (2026-11-11)

Host C++11 tests passed with `-Wall -Wextra -Werror` and AddressSanitizer /
UndefinedBehaviorSanitizer (leak detection disabled because the host environment
does not support it). `git diff --check` passed. Arduino CLI was installed, but
board/library index downloads failed due to network access, so the full Nano
ESP32 sketch build and upload remain unverified. No physical sensor test was run.

Acquisition register layout and library buffering were checked against the
[upstream SparkFun implementation](https://github.com/sparkfun/SparkFun_MAX3010x_Sensor_Library/blob/master/src/MAX30105.cpp)
and [header](https://github.com/sparkfun/SparkFun_MAX3010x_Sensor_Library/blob/master/src/MAX30105.h).
