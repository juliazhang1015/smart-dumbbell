# Bring-up 03: I2C scan with the Adafruit 4517 connected

## Identification

- Date: 2026-11-03
- Tester: Hanson He (wiring)
- Related issue: none
- Requirement / acceptance-test ID: precondition for FR-03 (motion acquisition); not an acceptance test
- Commit SHA: sketch `firmware/bringup/03_i2c_scan` at 17ac5fa
- Firmware and library versions: Arduino ESP32 Boards 2.0.18-arduino.5, arduino-cli 1.5.1, FQBN `arduino:esp32:nano_nora`, Wire from the core, bus at 400 kHz
- Hardware/module versions and mounting: Nano ESP32 ABX00083 on the course breadboard; Adafruit 4517 (LSM6DSOX + LIS3MDL) on a 4209 STEMMA QT cable: black GND, red 3V3, blue A4/SDA, yellow A5/SCL. No other I2C device on the bus.
- Test level: physical hardware
- Status: Run

## Objective and predefined acceptance criterion

From `firmware/bringup/README.md` step 3: the scan lists 0x6A (LSM6DSOX) and 0x1C (LIS3MDL), 2 devices, on repeated scans.

## Setup and procedure

Upload over DFU, read the CDC port at 115200 for 8 s (two scan cycles).

## Observations and measurements

```
scanning 0x08..0x77
  0x1C  LIS3MDL
  0x6A  LSM6DSOX
2 device(s)
```

Identical on the second cycle. No stray addresses.

## Result and limitations

- Outcome: Pass
- Evidence: serial capture above
- Known limitations: bus high level not measured yet; that check matters once the GY-MAX30102 (1.8 V pull-ups) joins the bus.
- Follow-up task: `04_imu_stream`.
