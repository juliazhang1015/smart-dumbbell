# Bring-up 07: kit OLED on the shared I2C bus

## Identification

- Date: 2026-11-03 (late evening)
- Tester: Hanson He (wiring, visual check)
- Related issue: none
- Requirement / acceptance-test ID: precondition for FR-09 (display); not an acceptance test
- Commit SHA: sketch `firmware/bringup/07_oled_buttons` at d896bd5
- Firmware and library versions: Arduino ESP32 Boards 2.0.18-arduino.5, Adafruit SSD1306 + Adafruit GFX (versions as installed in Hanson's IDE)
- Hardware/module versions and mounting: course-kit 0.96" OLED, SSD1306, I2C address 0x3C, 128x64; on the breadboard bus together with the Adafruit 4517 and the GY-MAX30102 (4 devices total). Buttons, LED and buzzer NOT connected in this run.
- Test level: physical hardware
- Status: Run

## Objective and predefined acceptance criterion

From `firmware/bringup/README.md` step 7, display part only: the scan shows 0x3C; on power-up the screen shows `IDLE`, `HR --`, a large `0` with `/10`, and the key hint line, sharp and not flickering.

## Setup and procedure

1. `03_i2c_scan` with all three modules attached.
2. Upload `07_oled_buttons`; look at the screen.

## Observations and measurements

- Scan: 0x1C, 0x3C, 0x57, 0x6A, 4 devices. No address conflict.
- Screen: Hanson reports the IDLE layout displayed normally (full 128x64 used, text legible, no garbage).
- Button, LED and buzzer behaviour untested (not wired).

## Result and limitations

- Outcome: Pass (display only)
- Evidence: scan output; visual confirmation
- Known limitations: readability at arm's length and refresh behaviour under the full UI loop not assessed; buttons/LED/buzzer part of step 7 still to run.
- Follow-up task: wire the three pushbuttons and the LED and complete step 7; then `06_imu_hr_combined`.
