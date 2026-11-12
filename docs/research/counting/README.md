# Smart Dumbbell — Repetition Counting and On-Board Integration Research

**Project:** ECE 198 Smart Dumbbell  
**Workstream:** B — Counting Logic + On-Board Integration  
**Prepared:** 2026-11-11  
**Status:** Literature review and proposed engineering design; **not a completed validation report**

## Executive summary

Version 1 recognizes bicep curls with an LSM6DSOX IMU and Arduino Nano ESP32. Workstream A classifies overlapping 2-second windows as `curl`, `idle`, or `other`. Workstream B must count **one complete upward-and-return movement**, not one classification window.

**Recommendation:** retain the existing filtered-gyro phase detector as a baseline. Prototype a bias-corrected integrated-angle finite-state-machine (FSM) counter offline. Require sufficient angular excursion, a valid return to the calibrated lower pose, timing constraints, classifier gating, and safe session transitions. Compare algorithms using the **same** held-out observer-counted recordings.

The current gyro-rate counter can theoretically accept small shakes with opposite velocity peaks because it does not independently verify movement amplitude. This is a **risk to test, not an observed failure**.

## 1. Requirements and interface

| Requirement | Description |
|---|---|
| FR-02 | Start, pause/resume, end; no increments while paused |
| FR-05 | One count per complete curl cycle |
| FR-06 | Reject pickup, put-down, stationary and unrelated motion |
| AT-02 | At least 18 of 20 ten-repetition sets have error within ±1 |
| AT-03 | At least 18 of 20 unrelated-motion trials produce zero false counts |

These are acceptance **targets**, not verified results.

**Hardware/data:** LSM6DSOX, 104 Hz, ±4 g, ±500 dps; CSV `t_ms,ax,ay,az,gx,gy,gz`; acceleration in m/s² and gyro in deg/s. Classifier windows contain 208 samples with a 104-sample hop (50% overlap); outputs are `label` and `conf`. Confirm the dominant gyro axis experimentally; `gx` is a mounting-dependent proposal.

An IMU on the dumbbell measures the **dumbbell**, not elbow joint angle directly. Wrist rotation, grip, and sensor mounting are confounders.

## 2. Literature findings

**Smart dumbbell IMU recognition [R1].** Shiao et al. study exercise-mode identification using a dumbbell-mounted IMU and motion features. Their classification findings motivate examining gyro and acceleration traces, but cannot establish our own counting accuracy.

**RecoFit [R2].** Morris et al. separate segmentation, recognition and counting, using acceleration-derived periodicity and peaks. They reported ±1 repetition accuracy in 93% of evaluated cases under their experimental conditions. This is not a performance prediction for our device. Their accelerometer-based method is a useful comparator to our gyro-based approach.

**LSM6DSOX documentation [R3–R4].** ST describes sensor ranges, filtering and FIFO support. At 104 Hz the nominal period is 9.615 ms. Application polling can still be late due to shared I²C traffic, OLED refresh, and inference. Record actual sample intervals; consider FIFO only if measurements justify it.

**Orientation fusion [R5].** Madgwick's filter is a candidate if simple gyro integration exhibits unacceptable drift; it adds complexity and does not eliminate mounting ambiguity or acceleration disturbances.

## 3. Counting algorithm comparison

| Candidate | Method | Advantages | Risks |
|---|---|---|---|
| A — Gyro-rate baseline | Detect positive/negative rate excursions, then settle | Fast, already prototyped | Shakes and slow movement may fool thresholds |
| B — Angle + FSM | Integrate bias-corrected rate, require full excursion and return | Explicit full-cycle criterion | Bias drift, wrist rotation |
| C — Acceleration peaks | Filter acceleration, detect repeated cycles | Independent RecoFit-inspired baseline | Gravity and linear acceleration mix |
| D — Fused orientation + FSM | Fuse acceleration and gyro, then track pose | Potential drift reduction | Complexity and dynamic-motion error |

**Existing prototype settings** in `firmware/app/app.ino`: `REP_TH=60 deg/s`, `REP_REST_TH=25 deg/s`, `REP_MIN_MS=600`, `REP_MAX_MS=5000`, `REP_LPF=0.2`. These are initial settings, **not experimentally optimized thresholds**.

### Angle estimation

With gyro reading ω in deg/s, stationary bias b and actual timestamp difference Δt in seconds:

```text
omega_corrected[k] = omega[k] - bias
theta[k] = theta[k-1] + omega_corrected[k] * delta_t[k]
omega_filtered[k] = alpha * omega_corrected[k] + (1-alpha) * omega_filtered[k-1]
```

Estimate bias during a confirmed stationary interval. Use measured timestamps rather than assuming constant intervals. Do not reset angle merely because rate approaches zero: the user may be holding the dumbbell at the top. Log drift during longer sessions.

### Proposed movement FSM

1. `WAIT_LOWER`: verified lower pose, stable and ready.
2. `ASCENDING`: motion in the expected lift direction.
3. `UPPER_REACHED`: sufficient displacement, top hold permitted.
4. `DESCENDING`: return motion toward the lower pose.
5. `COMPLETE`: return-to-lower condition and timing checks pass; increment **once** and rearm.
6. `REJECT_RESET`: invalid excursion, wrong sequence, timeout, interruption or incompatible classification.

Tune minimum excursion, end-position tolerance, velocity hysteresis, and minimum/maximum duration using pilot recordings. **No universal angle threshold is claimed.** Require a fresh lower-pose start after interruption.

## 4. False-count prevention

| Failure mode | Proposed control | Required test |
|---|---|---|
| Short shaking | Minimum angular excursion + full pose return | Small repeated oscillations |
| Half curl | Upper threshold + lower return | Half-up and interrupted movement |
| Repeated noise peaks | Hysteresis + single completion event + rearm | Rapid oscillations |
| Pickup / put-down | Classifier gate + complete-cycle FSM | Handling trials |
| Slow curls | Angle-based detection rather than rate alone | Slow, normal, fast |
| Pause mid-rep | Invalidate pending movement on pause and resume | Pause at top/bottom |
| Wrist rotation | Mounting protocol, multi-axis checks | Wrist twist and grip changes |

Do not optimize only for fewer false positives; report missed true repetitions too.

## 5. Classifier gating and shared interface

The model predicts once per 104-sample hop (~1 s), whereas the counter consumes 104 Hz IMU samples. A current label may describe a window ending up to ~1 s ago. Agree whether `t_ms` denotes the **last sample** of each window and what makes a prediction stale.

- **G1 baseline:** allow a completed count when the latest label is `curl`.
- **G2 candidate:** require time-aligned `curl` evidence over the candidate repetition, with a maximum prediction age.

Measure false rejection of true curls and false acceptance of other movements. Do not impose an arbitrary confidence threshold without held-out calibration. Keep ungated and gated performance separately reported while model weights are synthetic or unvalidated.

## 6. Session state machine

| Event | Session transition | Counting rule |
|---|---|---|
| Start | IDLE → RUNNING | Clear count and pending phase |
| Pause | RUNNING → PAUSED | No increment; invalidate partial movement |
| Resume | PAUSED → RUNNING | Require a fresh lower-pose start |
| End | RUNNING/PAUSED → IDLE | Preserve final record, clear phase |
| Target reached | Stay RUNNING | Notify; keep counting further valid reps |

Session state and movement phase are **separate state machines**. Merely blocking `countRep()` while paused does not prevent a pre-pause partial movement from being counted after resume.

## 7. Embedded timing and integration

At 104 Hz, nominal sample period = **9.615 ms**. A 50 ms classifier inference budget (proposed in `ml/workplan.md`) does not guarantee no dropped reads: blocking for 50 ms spans multiple sample periods.

Log `sample_count`, late reads, maximum and distribution of Δt, inference duration, OLED update duration, counter events and reject reasons. Keep the counter non-blocking. The current application already chunks OLED transfers to reduce long I²C bus occupation.

**Integration order:** (1) offline CSV playback without classifier; (2) board IMU counting without classifier; (3) classifier gate; (4) session controls; (5) full OLED/HR/network load; (6) repeat AT-02/03 on hardware and log timing.

## 8. Experimental plan

Use the shared `ml/data-protocol.md` and frozen sensor mounting. Obtain appropriate volunteer permission and use anonymous IDs. Record manually observed ground-truth cycles, participant code, hand, speed, firmware revision and mounting version.

Collect: slow/normal/fast complete curls, top holds, half curls, small oscillations, wrist rotation, pickup/put-down, walking, lateral/front raises, and pause/resume midway through a rep.

Compare algorithms on **identical recordings**. Tune only on development recordings, freeze parameters, then evaluate held-out participants or sessions. Never split overlapping windows from the same recording across training and test.

```csv
test_id,participant_id,algorithm,ground_truth_reps,predicted_reps,absolute_error,false_reps,firmware_version,notes
```

For AT-02, report number of sets with `abs(predicted - actual) <= 1`, mean and worst error. For AT-03, report number of trials with exactly **zero** false counts. Store dated evidence in `tests/results/`; never mark an unperformed test passed.

| Test | Target | Status |
|---|---|---|
| AT-02 | ≥18/20 ten-rep sets within ±1 | Not yet verified |
| AT-03 | ≥18/20 unrelated-motion trials with 0 false counts | Not yet verified |
| Pause/resume | No paused or carry-over counts | Not yet verified |
| AT-07 concurrent operation | 10 minutes, no reset/freeze; record losses | Not yet verified |

## 9. Risk register

| Risk | Mitigation |
|---|---|
| Gyro bias drift | Stationary calibration; longer-session drift measurement |
| Wrist rotation or mount variation | Freeze mounting; evaluate both hands/grips |
| Slow movement | Compare rate and angle-based counters |
| Small shakes | Minimum excursion + return-to-lower validation |
| Model lag | Timestamped gating and label-age limit |
| Pause carry-over | Clear pending movement phase |
| OLED/inference blocking | Time instrumentation, chunking, buffering if necessary |
| Synthetic classifier weights | Report gated/ungated results separately until validated |

## 10. Deliverables

```text
docs/research/counting/README.md        # research and proposed design
docs/research/counting/algorithm-comparison.md  # measured comparison later
docs/research/counting/parameter-study.md       # threshold evidence later
firmware/counting/README.md             # algorithm and parameters
ml/tools/offline_counter.py             # replay CSV and compare
tests/results/AT-02-*.md                # dated count test results
tests/results/AT-03-*.md                # dated interference tests
```

Confirm naming against `ml/workplan.md` (which currently proposes `firmware/counter/`) before implementing code.

## 11. Next actions

1. Confirm dominant axis and collect stationary bias plus complete-curl recordings.
2. Plot `gx,gy,gz`, estimated angle and annotated cycle boundaries.
3. Replay the current velocity-FSM counter offline as a baseline.
4. Add minimum excursion, return-to-lower and debug rejection reasons.
5. Compare methods on held-out data, freeze parameters, execute AT-02/03.
6. Integrate model gate and session controls; test full on-board load.

## References

- **[R1]** Shiao, Y., Hoang, T., & Chang, P.-Y. (2021). *Real-Time Exercise Mode Identification with an Inertial Measurement Unit for Smart Dumbbells.* Applied Sciences, 11(23), 11521. https://doi.org/10.3390/app112311521
- **[R2]** Morris, D., Saponas, T. S., Guillory, A., & Kelner, I. (2014). *RecoFit: Using a Wearable Sensor to Find, Recognize, and Count Repetitive Exercises.* CHI 2014. https://www.microsoft.com/en-us/research/publication/recofit-using-wearable-sensor-find-recognize-count-repetitive-exercises/
- **[R3]** STMicroelectronics. *LSM6DSOX product overview.* https://www.st.com/en/mems-and-sensors/lsm6dsox.html
- **[R4]** STMicroelectronics. *LSM6DSOX datasheet.* https://www.st.com/resource/en/datasheet/lsm6dsox.pdf
- **[R5]** Madgwick, S. O. H. (2010). *An Efficient Orientation Filter for Inertial and Inertial/Magnetic Sensor Arrays.* https://www.samba.org/tridge/UAV/madgwick_internal_report.pdf
- **[R6]** Microsoft Research. *Exercise Recognition from Wearable Sensors dataset.* https://github.com/microsoft/Exercise-Recognition-from-Wearable-Sensors
- **[R7]** STMicroelectronics STM32duino. *LSM6DSOX FIFO polling example.* https://github.com/stm32duino/LSM6DSOX/blob/main/examples/LSM6DSOX_FIFO_Polling/LSM6DSOX_FIFO_Polling.ino

### Project files reviewed

`docs/specification.md`, `ml/workplan.md`, `ml/data-protocol.md`, `firmware/bringup/04_imu_stream/04_imu_stream.ino`, `firmware/app/app.ino`, `firmware/classifier/classifier.h`, `tests/README.md`.

**Evidence policy:** Literature claims belong to their original studies; proposed parameters remain hypotheses. No AT-02/AT-03 pass is claimed without test records.
