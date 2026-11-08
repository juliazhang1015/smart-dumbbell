# Project handoff

For teammates. This is a snapshot begun on 2026-11-03 with updates through Nov 6, translated and reorganized on Nov 8. Consult dated [decisions](decisions.md) and actual test records when statements conflict; this brief is not a replacement for the working specification.

## Project and owners

University of Waterloo ECE 198 Group 57: Hanson He, Eric Zhu, Zoe Wang and Julia Zhang. The proposed smart dumbbell supports CCCARE home exercise through on-device bicep-curl classification and counting, optical heart rate during movement, OLED feedback and Wi-Fi computer logging. Version 1 has one exercise and three classes: `curl`, `idle`, `other`.

The recorded demonstration date is 2026-11-25, reported verbally and not yet checked against LEARN.

| Area | Recorded owner |
|---|---|
| Motion classification | Hanson He |
| Counting and on-board integration | Julia Zhang |
| Computer logger | Julia Zhang |
| Electronics, power, wiring, heart-rate module | Zoe Wang |
| Enclosure CAD and printing | Eric Zhu |
| Heart-rate algorithm, FR-07/08 | Unassigned in the recorded plan |

## Available work and limitations

- Working requirements, AT-01–10 targets, decisions, hardware/budget documents and collaboration guidance.
- Concept CAD v0.1 (DWG and generator) and a concept appearance study.
- Delivered pitch and narration snapshots still referring to the older ADXL335 design.
- [Wiring artifacts](../hardware/wiring/README.md), including a schematic redrawn from physical modules on Nov 4. Initial I2C breadboard tests are recorded.
- Nano ESP32, Adafruit 4517, two 4209 cables, borrowed GY-MAX30102, kit OLED and a purchased power bank.
- [ML workplan](../ml/workplan.md), recording protocol and training pipeline: windows, 31 features, participant split and C-header export. The pipeline ran on synthetic data; host classifier checks matched Python within 1e-6. Current weights are synthetic, not a validated motion model.
- Julia's `software/data_logger.py` prototype (Nov 6; PR #4 in the previous repository): HTTP status polling, terminal display, CSV output, duplicate/out-of-order handling, reconnects and blank invalid heart rates, with mock server and three unit tests. Tested against the mock only; `/status` and `/target` remain interface proposals requiring firmware agreement.
- Seven bring-up sketches and six Nov 3 records covering upload, Wi-Fi AP, I2C, 104 Hz IMU/axes, optical module and OLED.
- `firmware/app/` is a Nov 6 integration draft with one button, IMU, classifier, placeholder counter, heart rate and OLED, but no Wi-Fi. Initial hardware checks found four I2C devices, 104 Hz sampling without reported late samples and working button transitions. Counting, LED and finger heart rate were not tested in that run; see [the record](../tests/results/2026-11-06_app-v0-first-run.md).

No full AT-01–10 acceptance results are present. Static optical readings on Nov 3 overestimated the watch reference by 9–14 bpm. Physical dimensions, low-load power-bank shutdown and the full Grove kit inventory remain to be checked.

## Hardware snapshot

| Role | Component | Recorded source/status |
|---|---|---|
| Controller | Nano ESP32 ABX00083, ESP32-S3, 3.3 V logic | DigiKey CAD 28.66; received, headers soldered, upload/Wi-Fi checked |
| IMU | Adafruit 4517 LSM6DSOX + LIS3MDL | DigiKey CAD 29.63; 104 Hz and axes checked; magnetometer unused in v1 |
| IMU cable | Adafruit 4209, 150 mm, two cables | Received; one in use, one spare |
| Optical sensor | Borrowed GY-MAX30102 | Address 0x57 and contact detection work; BPM processing needs improvement |
| Display | Kit SSD1306 128×64, I2C 0x3C | Display checked |
| Controls | Three kit buttons in baseline | Integrated app currently experiments with one button |
| Feedback | Borrowed Grove buzzer; optional vibration motor if available | Nov 2 photo showed buzzer/LED holder, no confirmed vibration motor |
| Power | INIU SnapGo P81, 5000 mAh, integrated USB-C cable | Purchased from amazon.ca; CAD 29.69 before tax; listed 80×38×29 mm, 115 g |
| Enclosure | Custom hollow removable housing | Not yet fabricated; UW RPC E5-2002 self-service printing was estimated at CAD 0.08/g |

Borrowed UNO R4 Minima and Dragino Yun Shield v1.1 are not final-device components. The recorded rationale was R4 memory limits and the shield's size/power; R4 remains a bench option.

Recorded spending: CAD 119.55 (DigiKey 86.00 including tax/shipping, power bank 33.55). This exceeds the original CAD 100 ceiling. The team verbally agreed on Nov 1 to increase it, but a replacement ceiling is unresolved. This brief previously estimated CAD 60–80 for enclosure/hardware and CAD 180–200 total; these are estimates, not approved spending limits.

## Dated decisions

- Oct 18: smart dumbbell, one exercise/three classes, on-device ML, counting, display, Wi-Fi and during-motion heart rate.
- Oct 31: choose Nano ESP32 and purchased LSM6DSOX instead of borrowed ADXL335; reject R4 plus external Wi-Fi. Retain the ordered 4517 rather than exchange for 4438.
- Nov 1: select INIU P81 rather than a bare lithium cell.
- Nov 2: add wiring draft and proposed pins.
- Nov 3: bring-up found 0x1C, 0x3C, 0x57 and 0x6A on one bus, verified axes, and achieved communication despite the optical module's possible 1.8 V pull-ups. Split classification and counting workstreams.

See the decision log for authority and unresolved scope changes.

## Decisions still required

1. During-motion heart-rate feasibility and test method. The original brief identifies overlapping curl/motion and pulse frequencies as a concern. Static pulse amplitude was only 0.1–0.4% of DC and estimates were 9–14 bpm high. A proposal to show motion readings only when quality permits and rely on between-set readings is **not an accepted change** to FR-07 or AT-04/05.
2. A new budget ceiling; CAD 200 was proposed, not confirmed.
3. Enclosure dimensions/layout. The original brief proposed starting fresh rather than treating concept CAD as a constraint, a power-bank cavity of at least 86×44×35 mm, possibly mounting electronics/power on one side, 2–3 mm walls and steel-washer ballast. Its 1–1.5 kg proposal conflicts with the working specification's <=1 kg/no-added-ballast baseline. Resolve before changing CAD; none of these proposals silently supersedes the specification.
4. Actual Grove kit contents and choice of feedback hardware.
5. A synchronized heart-rate reference device for AT-04.

## Known issues

- GY-MAX30102 pull-ups may connect to 1.8 V. Shared-bus communication worked, but the high level has not been measured with a meter.
- Do not toggle serial DTR/RTS; it can enter ROM download mode and cause upload status 74. See [bring-up recovery](../firmware/bringup/README.md).
- SparkFun `checkForBeat` has not established adequate accuracy. Band-pass/peak or spectral processing was proposed; preserve invalid/stale reporting under FR-08.
- Check power-bank low-load auto-shutdown with a ten-minute run. Estimated load is tens to slightly over one hundred milliamps, not a measurement.
- Nano logic is 3.3 V; the original bench setup recommends red/yellow LEDs with 220 ohm resistance.
- Nano does not directly fit the Grove Base Shield. Use an appropriate Grove-to-Dupont adapter (recorded candidate Seeed 110990210).
- Pitch, narration, PDF and CAD placeholders are dated snapshots with old sensor/dimension assumptions. Replace them in coordinated versions.
- Polished formatting is not validation; distinguish proposals from recorded evidence.

## Reading order

1. [Decisions](decisions.md).
2. [Hardware and budget](hardware.md).
3. [Working specification](specification.md), FR-01–13 and AT-01–10.
4. [Wiring](../hardware/wiring/README.md).
5. [Overview](../README.md).
6. [Team guide](team-guide.md) and [contributing](../CONTRIBUTING.md).
7. [Project guidelines](project-guidelines.md).

Presentation, CAD, renders and specification exports are versioned snapshots. Hanson also has a local `Hardware Datasheets/` collection outside this repository.

## Next checks and handoff outputs

- Measure Nano/4517 dimensions and update hardware/enclosure inputs.
- Inspect MAX30102 pull-up selection and INT availability.
- Verify OLED pin order and address; confirm bus devices 0x6A, 0x57 and 0x3C.
- Measure the power-bank cable and test ten minutes with Wi-Fi/OLED active.
- Keep actual firmware pins and wiring notes synchronized.

| Workstream | Next action | Output |
|---|---|---|
| Sensor firmware | Maintain separate IMU, raw optical and OLED checks | `firmware/` |
| Classification | Freeze mounting, record initial participants, train | `ml/`, `firmware/classifier/`, approved session data |
| Counting | Tune offline before model integration, then gate and add states | Planned `firmware/counter/`, `ml/tools/`, test records |
| Computer logger | Receive Wi-Fi data, display and export records/summary | `software/` |
| Enclosure | Resolve cavity/layout; original target was a first print by Nov 10 | Versioned `hardware/cad/` |
| Heart-rate feasibility | Obtain reference and define the 60 s synchronized comparison | `tests/results/` |

Follow the project guidelines: do not silently change hardware, exercises, features or acceptance numbers. Update the English working specification and flag stale exports. Separate simulation, software checks, measurements, mechanical evidence and clinical claims. Date prices/dimensions and cite sources. Do not commit private order details or identifiable recordings. Use focused branches, English commit messages and PR review; preserve others' binary artifacts with new version names.
