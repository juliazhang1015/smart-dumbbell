# 2026-11-21 — model-confirmed rep counting, hand-held board (first hardware check)

## Identification

- Date: 2026-11-21, about 23:45–24:00
- Related work: PR #16, `firmware/SmartDumbbell` at `27750ae` (`COUNT_GATE 1`, `USE_BLE 1`, `SWING_MIN_DEG` 60°, five-participant weights)
- Hardware: the soldered bench board (Nano ESP32, LSM6DSOX, MAX30102, OLED) on USB, **not mounted on a dumbbell and not in the enclosure**; held in the hand
- Tester: Hanson He, one person, who also counted the repetitions; no second observer
- Test level: hardware, informal. Not an AT-02 or AT-03 run.

## Objective

Check on the board that the sketch built from the PR runs, and that the model confirmation counts complete curls and rejects other movement as in the offline replay (`firmware/SmartDumbbell/README.md`, "Model confirmation of reps"). No pass threshold was set beforehand.

## Setup and procedure

Uploaded with `arduino-cli upload` (DFU). Confirmed the new sketch was running from its own output: the `?` report includes `imu_samples=` and `t_ms=`, which only this version prints (the boot `SELFTEST` line was missed because the serial port was opened after it). Serial output was logged with `cat` on the CDC port for the whole test. Short press = start / pause, long press = end.

Two runs were scored. A run in between (session 3) was a false start and is not scored, at the tester's request.

## Observations and measurements

Module flags `IMU=1 MAX30102=1 OLED=1`, I2C addresses 0x1C, 0x3C, 0x57, 0x6A. Periodic inference 2191–2209 µs.

**Run A (session 2).** 10 complete curls, then about 20 s of shaking, lateral raises, picking up and putting down. During two curls the tester's hand hit the laptop.

| Event | Swing | Result |
|---|---|---|
| curls 1–4 | 98–118° | counted, p_curl 0.98–1.00 |
| curl with hand hitting the laptop | 129° | `rejected=other`, p_curl 0.04 |
| curl with hand hitting the laptop | 113° | `rejected=other`, p_curl 0.36 |
| curls 7–10 | 122–134° | counted, p_curl 1.00 |
| other movement | one 146° candidate; one candidate ran past 8 s; 18 candidates under 60° | `rejected=other` (p_curl 0.00); `timeout`; `small` |

Board count 8. The two rejected curls: the periodic label 0.2 s earlier was `curl 1.00`, the next two were `other 1.00`.

**Run B (session 4).** 15 complete curls, 2 front raises, then the board put down on the table.

| Event | Swing | Result |
|---|---|---|
| curls 1–15 | 97–118° | all counted, p_curl 1.00 each |
| front raises | one 46° candidate | `small` |
| put down on the table | — | no candidate |

Board count 15. The session was later resumed and six more reps were counted (130–101°, p_curl 1.00); that activity was not described by the tester and is not scored.

**Totals over A and B:** 23 of 23 curls without contact counted; 2 curls with contact rejected; 0 reps counted during other movement. All rejections came from the model on large swings or from `SWING_MIN_DEG` on small ones; front raises were stopped by the swing gate alone.

**Static label, same day.** Board lying flat on the table: `idle 1.00` for 9 of 9 inferences. In two other resting poses (not recorded in detail) the label was `curl` 0.65–0.99; this does not change the count, which needs a swing first.

**IMU read rate.** Two `?` reports 10 s apart: 964 samples in 10.01 s = 96.3 per second, `imu_late` +32 (about 3 gaps per second). Over the first 125 s: 11967 samples, `imu_late` 390. The sensor runs at 104 Hz, so about 7 % of samples are lost to loop stalls; the counter integrates over the real interval, and the classifier window then spans about 2.16 s. The source of the stalls has not been identified. The planned 50 ms stall comparison (README, "IMU sampling after a loop stall") has not been run.

## Result and limitations

- Outcome: on this informal check the board behaved as the replay predicts: complete curls counted, other movement not counted, curls with an impact rejected.
- One person, hand-held board, self-counted repetitions, 25 curls in total. The assembled dumbbell (enclosure orientation, weight) is not tested; the training data was recorded on taped mounts.
- Half curls were not tested; the model does not reject them by design (`partial` is trained as `curl`).
- A curl with an impact (here, hitting a laptop) is lost. A rule that accepts a rejected rep between two confirmed reps would recover it; not implemented.
- Not AT-02 / AT-03 evidence: those need 20 sets / 20 interference cases with an independent count.
