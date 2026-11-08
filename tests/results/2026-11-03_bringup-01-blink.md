# Bring-up 01: blink on Nano ESP32

## Identification

- Date: 2026-11-03
- Tester: Hanson He
- Related issue: none
- Requirement / acceptance-test ID: none (board bring-up, precondition for everything else)
- Commit SHA: 17ac5fa (sketch `firmware/bringup/01_blink`)
- Firmware and library versions: Arduino ESP32 Boards 2.0.18-arduino.5, arduino-cli 1.5.1, FQBN `arduino:esp32:nano_nora`, no external libraries
- Model version and dataset split, if relevant: n/a
- Hardware/module versions and mounting: Arduino Nano ESP32 ABX00083 (headers factory-soldered), received 2026-11-03, loose on the desk, USB-C to laptop only
- Test level: physical hardware
- Status: Run

## Objective and predefined acceptance criterion

From `firmware/bringup/README.md` step 1: the board enumerates over USB, accepts an upload, the RGB LED cycles red/green/blue with the yellow LED in step, and the serial monitor at 115200 prints one `rgb N on, uptime ...` line every 300 ms.

## Setup and procedure

1. Board plugged in with a data-capable USB-C cable; `arduino-cli board list` showed it as `Arduino Nano ESP32` on DFU port `1-1`.
2. `arduino-cli upload --fqbn arduino:esp32:nano_nora -p 1-1 01_blink`.
3. After re-enumeration the board appeared as `/dev/cu.usbmodemE4B063AED3802`; read the port at 115200 for 4 s.

## Observations and measurements

- Upload: DFU download of 286 736 bytes completed, `Done!`, no errors.
- Serial output (7 consecutive lines captured):

```
rgb 1 on, uptime 23245 ms
rgb 2 on, uptime 23845 ms
rgb 0 on, uptime 24445 ms
rgb 1 on, uptime 25045 ms
rgb 2 on, uptime 25645 ms
rgb 0 on, uptime 26245 ms
rgb 1 on, uptime 26845 ms
```

- Interval between lines 600 ms, matching 300 ms on + 300 ms off. Colour index cycles 0, 1, 2 as written.
- Visual check by Hanson a few minutes after the capture: red, green, blue cycle in turn and the yellow LED blinks with them. Active-low RGB assumption confirmed.

## Result and limitations

- Outcome: Pass
- Evidence: serial capture above plus visual confirmation
- Known limitations: none for this step
- Follow-up task: run `02_wifi_ap`.
