# Bring-up 02: Wi-Fi access point on Nano ESP32

## Identification

- Date: 2026-11-03
- Tester: Hanson He
- Related issue: none
- Requirement / acceptance-test ID: precondition for FR-11 (Wi-Fi to computer); not an acceptance test
- Commit SHA: sketch `firmware/bringup/02_wifi_ap` as committed with this record (heartbeat line added today)
- Firmware and library versions: Arduino ESP32 Boards 2.0.18-arduino.5, arduino-cli 1.5.1, FQBN `arduino:esp32:nano_nora`, WiFi library from the core
- Hardware/module versions and mounting: Arduino Nano ESP32 ABX00083, loose on the desk, USB-C to laptop only
- Test level: physical hardware
- Status: Run

## Objective and predefined acceptance criterion

From `firmware/bringup/README.md` step 2: the board starts a soft AP `SmartDumbbell-57` at 192.168.4.1; a phone can see and join it; `http://192.168.4.1` returns a text line; the serial heartbeat shows `stations=1` while the phone is connected.

## Setup and procedure

1. Upload over DFU (`-p 1-1`). First attempt failed with `exit status 74` because a test script had toggled DTR/RTS on the CDC port and put the chip into ROM download mode; recovered with `esptool --after watchdog-reset`, then uploaded again. Documented in the bring-up README.
2. Read the CDC serial port at 115200 with `cat` (no control-line changes).
3. Checked the laptop's Wi-Fi scan list with `system_profiler SPAirPortDataType`.

## Observations and measurements

- Serial heartbeat, 3 consecutive lines:

```
AP SmartDumbbell-57  ip=192.168.4.1  stations=0  uptime=8000 ms
AP SmartDumbbell-57  ip=192.168.4.1  stations=0  uptime=10000 ms
AP SmartDumbbell-57  ip=192.168.4.1  stations=0  uptime=12000 ms
```

- Laptop scan list did not contain `SmartDumbbell-57` in two checks. Inconclusive: that list is not a fresh scan and the laptop was not disconnected from its own network to try joining.
- A few minutes later Hanson joined the AP from a phone and opened http://192.168.4.1; the page returned the uptime text line. Serial heartbeat at that time:

```
AP SmartDumbbell-57  ip=192.168.4.1  stations=3  uptime=222000 ms
AP SmartDumbbell-57  ip=192.168.4.1  stations=3  uptime=224000 ms
```

- `stations=3`, not 1: two other devices also joined (the password is in the public repository and the AP was left running for a few minutes). Not a fault, but a reminder to change the credentials before any demo.

## Result and limitations

- Outcome: Pass
- Evidence: serial captures above and the HTTP response seen on the phone
- Known limitations: no range or throughput measurement; the AP had 3 stations with the default credentials.
- Follow-up task: run `03_i2c_scan` with the 4517 connected. Change AP_SSID/AP_PASS before the demo.
