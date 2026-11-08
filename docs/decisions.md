# Decisions and unresolved questions

Baseline established in team planning on 2026-10-18; hardware baseline revised 2026-10-31. These are design decisions, not validation results.

## Selected baseline

- Focus: Sub-problem 3, remote at-home care.
- Intended users: CCCARE graduates/participants who can independently complete prescribed dumbbell exercises.
- Smart dumbbell is the preferred concept; the guided exercise station remains the second pitch concept.
- Version 1 includes on-device ML, repetition counting, display, Wi-Fi records and heart-rate measurement during movement.
- One exercise, bicep curl, with `curl`, `idle`, `other` classes.
- Final controller baseline: Arduino Nano ESP32 (ABX00083). Motion baseline: Adafruit LSM6DSOX + LIS3MDL 9-DoF IMU (4517), purchased; only the LSM6DSOX accelerometer and gyroscope are used in Version 1. Heart rate: borrowed GY-MAX30102. Three buttons.
- Custom hollow enclosure; total purchase ceiling CAD 100 including taxes and shipping.
- A personal smartwatch is not required. Existing watches may help exploratory comparisons, but are not assumed to be accurate ground truth.

## CAD status

The committed v0.1 DWG has a 280 mm overall shell length, 100 mm maximum head width, 86.603 mm head height, 140 mm exposed grip and 34 mm grip outer diameter. The end depth is 70 mm and nominal walls are 3 mm.

An 80 mm head width (about 69.3 mm height for the regular hexagon) has been proposed but NOT implemented. Simply shrinking the shell creates interference at the existing screw bosses, OLED/button positions and accelerometer location. The current board and power envelopes appear potentially compatible after repacking, but connectors, mounts and actual parts are not verified. A 90 mm width is also only a candidate.

The concept rendering illustrates appearance and is not a dimensional reference. Use CAD notes for dimensions. Do not print the electronics envelopes or exploded duplicate assembly.

## Open decisions and evidence needed

- Can the grip optical sensor meet the during-movement quality targets? Test against a synchronized reference before freezing the handle.
- What exact power module and OLED / GY-MAX30102 board revisions will be used? Check the MAX30102 board for 1.8 V I2C pull-ups before wiring.
- Should FR-07 / AT-04 / AT-05 keep the strict during-movement heart-rate targets (coverage >= 90%, MAE <= 10 bpm during curls), or be relaxed before testing to "valid output during movement when signal quality permits, guaranteed output during rest between sets"? Motion and heart rate share the 1-2 Hz band, so the strict target is at high risk. Decide before the test method is frozen.
- How will the grip, caps, boards and power supply be retained and serviced?
- Budget: spent CAD 119.55 to date (DigiKey 86.00 + power bank 33.55), over the original CAD 100 ceiling. The team said on 2026-11-01 that raising the ceiling is acceptable; agree and record the new figure before the enclosure purchase.
- Should users be able to change and persist targets directly on the dumbbell? Currently targets are set from the computer.
- Should the device store complete offline history for later synchronization? Not included in the current specification.

Record a dated decision, reason, supporting evidence and affected files when any baseline choice changes.

## Decision log

### 2026-11-03: Motion ML work split into two owned lines

- **Decision:** Movement classification (FR-03, FR-04, AT-01) and repetition counting with on-device integration (FR-02, FR-05, FR-06, AT-02, AT-03) are two separately owned lines, each with its own files, branch, issue and documentation. The only shared contract is the classifier output (`t_ms,label,conf`, one result per second over a 2 s window at 104 Hz), recorded as a draft in `ml/workplan.md` section 4 and to be confirmed in the week of 2026-11-04. Anonymised recordings are committed under `data/sessions/` (participant codes only); `data/raw/` and `data/private/` stay ignored for anything that cannot be anonymised.
- **Reason:** Counting can be demonstrated without the classifier but not the other way round, so the counter must not wait for the model. Splitting by task rather than by pipeline stage lets each owner test against their own acceptance targets. One board exists, so recordings must be shared through the repository for the second owner to work offline.
- **Inference approach (classification line, 2026-11-03):** hand features + logistic regression or small MLP, exported by `ml/train/export_c.py` to a C header and run by plain C++ in `firmware/classifier/`. TensorFlow Lite Micro stays the fallback if a window-based network becomes necessary.
- **Owners:** classification Hanson He; counting and integration Julia Zhang. Other areas recorded the same day in `docs/handoff.md`: enclosure Eric Zhu, hardware Zoe Wang, computer logger Julia Zhang (issue #2). Heart-rate algorithm unassigned.
- **Open:** IMU mounting orientation (must be fixed before the first recording), and how `curl_partial` recordings are labelled for training.
- **Affected files:** `ml/workplan.md` (new), `data/sessions/README.md` (new), `ml/README.md`, `docs/handoff.md`, `README.md`.

### 2026-11-01: Power supply selected and purchased

- **Decision:** INIU SnapGo P81 power bank (5000 mAh, built-in USB-C cable, 80 x 38 x 29 mm, 115 g) bought on amazon.ca for CAD 29.69 before tax. It powers the Nano ESP32 through its built-in cable.
- **Reason:** A bank with a built-in flexible cable keeps mechanical load off the Nano's USB-C socket, unlike banks with a rigid male plug. Available next day. Capacity far exceeds the 30-minute runtime target.
- **Not yet verified:** low-load auto shut-off behaviour, built-in cable length, and enclosure fit. Checks are listed in `docs/hardware.md`.
- **Consequence:** total spend CAD 119.55, over the original ceiling. Budget ceiling to be re-agreed.
- **Affected files:** `docs/hardware.md`, the former translated specification (removed after English consolidation).

### 2026-10-31 (evening): DigiKey order placed; 9-DoF board kept

- **Decision:** The order (Salesorder 102617982) was placed with Adafruit 4517 (LSM6DSOX + LIS3MDL 9-DoF, CAD 29.63) instead of the recommended 4438, plus two 4209 cables (one spare) and the Nano ESP32. Shipping was FedEx International Priority at CAD 15.00, the only option shown at guest checkout. Total invoiced CAD 86.00. The team chose to keep 4517 rather than change the order; the magnetometer is unused in Version 1 and may be useful later.
- **Reason:** Changing a submitted DigiKey order is usually not possible and a return would cost more in shipping and time than the CAD 12 difference.
- **Consequence:** CAD 14 remains under the budget ceiling for power and enclosure. Recorded above as an open decision.
- **Affected files:** `docs/hardware.md`, the former translated specification (removed after English consolidation), `docs/project-guidelines.md`, `Hardware Datasheets/README.md`.

### 2026-10-31: IMU changed from borrowed ADXL335 to purchased LSM6DSOX; controller confirmed

- **Decision:** Buy Arduino Nano ESP32 with headers (DigiKey 1050-ABX00083-ND, CAD 28.66), Adafruit LSM6DSOX 6-DoF IMU (1528-4438-ND, CAD 17.75) and a STEMMA QT to male-header cable (1528-4209-ND, CAD 1.41). Borrow GY-MAX30102, OLED and buttons. ADXL335 becomes an optional backup only.
- **Reason:** A bicep curl is mainly forearm rotation, so angular rate from a gyroscope gives a cleaner repetition signal than acceleration alone. The course loan list and the Grove Starter Kit Plus contain no gyroscope and no wireless controller, so these two items must be purchased. The 9-DoF version (4517, CAD 29.63) was rejected because the magnetometer does not help curl counting and costs CAD 12 more. R4 Minima plus an external Wi-Fi module was rejected because the R4 3.3 V pin is fed by the RA4M1 internal USB LDO (R4 Minima datasheet section 9.2) and cannot power a Wi-Fi module, its 5 V logic needs level shifting, and 32 kB SRAM is tight for ML plus Wi-Fi buffers.
- **Evidence:** DigiKey Canada prices and stock on 2026-10-31; Grove Starter Kit Plus wiki parts list; Arduino UNO R4 Minima datasheet. No hardware has been received or tested.
- **Affected files:** `docs/hardware.md`, `docs/specification.md`, the former translated specification (removed after English consolidation), `README.md`, `docs/project-guidelines.md`, `docs/team-guide.md`. Not yet updated: the pitch deck and speaker script (delivered snapshots still name ADXL335), the PDF specification export, and the CAD accelerometer placeholder dimensions.
