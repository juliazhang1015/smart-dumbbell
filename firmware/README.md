# Firmware

Status 2026-11-19: [SmartDumbbell/](SmartDumbbell/README.md) is Zoe Wang's sketch for the soldered board (one button, Wi-Fi AP + HTTP, optional BLE behind `USE_BLE`, rule-based counter with a swing gate, averaged BPM). Hanson He chose it on 2026-11-19 as the sketch to run on that board; it compiles in both builds but has not been run on hardware since the 2026-11-19 edits. [app/](app/README.md) keeps the classifier integration and the chunked OLED transfer; [demo/](demo/) is the 2026-11-08 ancestor of SmartDumbbell.

Status 2026-11-06: first integrated sketch in [app/](app/README.md): one button (short = start / pause / resume, long = end), LSM6DSOX at 104 Hz into the classifier, a placeholder rep counter, MAX30102 heart rate with a validity flag, OLED, LED, optional buzzer. Compiles (Flash 10 %, RAM 12 %) and ran on the board on 2026-11-06: all four I2C modules found, IMU at 104 Hz with no late samples while the OLED refreshes, button state machine works; rep counting, LED and finger heart rate not yet exercised (see `tests/results/2026-11-06_app-v0-first-run.md`). No Wi-Fi yet. Board bring-up sketches and the test procedure are in [bringup/](bringup/README.md); the on-device model lives in [classifier/](classifier/README.md).

Planned target: Arduino Nano ESP32. Implement sensor acquisition, non-blocking scheduling, local ML inference, complete-cycle counting, OLED/button interaction, heart-rate validity handling and a local Wi-Fi/HTTP interface.

Begin with separate sensor readout sketches and a rule-based counting baseline. Record actual module versions and pin assignments before integrating. The baseline is a development aid; it does not replace the required ML feature without a recorded scope change.

See [functional requirements](../docs/specification.md#functional-requirements).
