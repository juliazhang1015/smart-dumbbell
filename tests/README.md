# Verification status

No acceptance test has been run or passed. Board bring-up records live in `results/` (2026-11-03: Nano ESP32 blink, Wi-Fi soft AP, I2C scan of the 4517, and LSM6DSOX 104 Hz stream all passed; GY-MAX30102 detects the finger but the on-board heart-rate value is not yet reliable, see the 05 record; kit OLED at 0x3C displays correctly with all three modules on one bus). CAD AUDIT checks documented in the CAD notes validate the drawing database, not mechanical strength or component fit.

Use AT-01 through AT-10 in [the specification](../docs/specification.md#acceptance-tests). Each result should record date, hardware/firmware/model versions, procedure, expected criterion, measured result, limitations and pass/fail/untested status.

First priorities are motion data quality, false counts during handling and heart-rate coverage/error during movement. Use a synchronized reference for the latter. Software simulation cannot establish physical sensor or clinical performance.

`test_data_logger.py` is a unit test for the computer logger (`python3 -m unittest tests.test_data_logger` from the repository root); it is a software check, not an acceptance test.

`test_record_serial.py` runs the IMU recorder `firmware/bringup/record_serial.py` against a scripted stand-in for the serial port (`python3 -m unittest tests.test_record_serial`). It checks that a normal take is saved and that a silent board, frozen values, lost samples, bad timestamps and non-finite values each stop the take without leaving a file. No board is involved, so it says nothing about the hardware.

Use the [test record template](templates/test-record.md) and save completed records under `tests/results/`. Keep private raw recordings outside the public repository.
