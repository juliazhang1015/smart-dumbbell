# Motion classification recording protocol

Version v0.4, 2026-11-21 (v0.1: 2026-11-03; v0.2, 2026-11-16, records the mounting used from P01 onward; v0.3, 2026-11-19, set the target at the four team members; v0.4 records the five participants actually recorded, two of them outside volunteers, see `docs/decisions.md`). Owner: Hanson He. Resolve **TBD** items before recording the first participant. **Proposed** items require team agreement.

## 1. Purpose

The same recordings support classification of two-second motion windows and offline tuning of complete-cycle counting. Record both the motion label and the observer's ground-truth count for each relevant file.

## 2. Equipment and acquisition

- Nano ESP32 and Adafruit 4517 connected through a 4209 cable to A4/A5; see [wiring](../hardware/wiring/README.md).
- `firmware/bringup/04_imu_stream`: 104 Hz, ±4 g, ±500 dps. Freeze these settings for a dataset; changes can invalidate compatibility with earlier recordings.
- Record over USB using `firmware/bringup/record_serial.py`; Wi-Fi is not used for v1 collection.
- CSV: `t_ms,ax,ay,az,gx,gy,gz`. Acceleration is m/s² and angular rate deg/s. Axes follow the 4517 markings: +X/+Y arrows and +Z out of the component face, checked on 2026-11-03.

## 3. Recording fixture and mounting (mount v1, frozen 2026-11-16)

Fixture: a neoprene dumbbell, shown in [the mounting photo](figures/mounting-v1.jpg), used while the enclosure is unavailable. **TBD:** its mass has not been weighed; weigh it and record the value here before the second participant. The fixture is a recording aid and does not change the working specification's mass limit.

Mounting, as used for P01:

- The 4517 is taped to the top of one head, component face up when the dumbbell lies on a table with the sensor on top. Its long axis (STEMMA QT socket to STEMMA QT socket) is parallel to the handle.
- Sensor X is the curl axis. Measured on the P01 curl files, the principal rotation axis is 3–7° from sensor X and carries 94–96 % of the gyro energy. Raising the dumbbell gives a negative `gx` angle.
- Orientation reference: `data/sessions/P01_idle_table_01.csv`, mean acceleration (0.69, 0.11, 10.04) m/s², so X is 3.9° from horizontal. **TBD:** which head +X points toward has not been read from the silkscreen (it is under the tape); the sign convention above is the record until it is.
- The Nano hangs from the USB cable and is joined to the 4209 cable by loose jumper leads. This is the weak point: a lead came off during one fast-curl take. Secure the Nano and the joints to the head before the next participant; this does not change the sensor orientation.

Do not move the 4517. Before and after each participant, lay the dumbbell flat with the sensor on top, record 5 s, and compare the mean acceleration with the reference: the gravity direction should be within 5° (it was 1.7° after P01). A larger difference, or any re-taping of the sensor, needs a new mount version here and that version in the `sessions.csv` notes.

An earlier attempt on 2026-11-16 had the sensor about 40° off the handle axis; those takes were discarded and are not in the repository.

**Mount v2 (from P03, 2026-11-20).** The sensor was re-taped before P03. Orientation reference: `data/sessions/P03_idle_table_01.csv`, mean acceleration (-0.17, 0.70, 10.03) m/s². P03, P04 and P05 are recorded with mount v2; the details are in the "Mount versions" section of `data/sessions/README.md` (added with the P03-P05 data, PR #19).

Route USB behind the hand with at least 1 m of slack.

## 4. Participants

Use `P01`, `P02`, etc. Hanson keeps any identity mapping outside the repository. Record only hand (L/R) and regular strength-training experience (Y/N), not age, height or medical history. Explain what is recorded, storage and the option to stop; confirm course volunteer requirements before collection (pending). Recorded (v0.4, 2026-11-21): **five participants, P01-P05**, 2026-11-16 to 2026-11-20. P01 and P03 are team members, P04 and P05 are outside volunteers, P02's team membership is not recorded; all five agreed to public release (`data/README.md`). Outside volunteers may be recorded when they agree to the public release of their recordings before the files are committed; write the agreement and its date into `data/README.md`. Whether the course sets further requirements for volunteers is still unconfirmed. The v0.2 target of six with both hands and both training-experience groups is not reached (all five are right-handed; one does strength training); every report of the model states the actual count and composition.

## 5. Labels

Four recording labels map to three training classes:

| Label | Procedure |
|---|---|
| `curl` | Continuous complete curls: arm naturally down, raise until forearm is near vertical and dumbbell near shoulder, return down. No pauses or half-repetitions; observer counts cycles. |
| `idle` | Separate files for standing with dumbbell at side, dumbbell on table without contact, and seated with dumbbell on lap. |
| `other` | In one continuous file: five pickup/put-down cycles, walking 20 s, ten lateral raises, ten front raises, random shaking 20 s. |
| `curl_partial` | Ten half raises, five raises with a 3 s hold at the top, then three complete curls followed by 5 s rest repeated three times. Record actual complete cycles. |

Record curls at approximately 3 s (slow), 2 s (normal) and 1.2 s (fast) per cycle, paced verbally or with a metronome.

**Proposed training mapping:** map `curl_partial` to `curl`. Classification identifies the motion family; the counter decides completeness. A two-second window may not distinguish half-range movement from the ascending phase of a normal curl. Use these files to check overcounting in AT-02.

## 6. Per-participant checklist

Allow roughly seven minutes of data and thirty minutes including setup.

| File | Duration | Ground-truth count |
|---|---|---|
| `Pxx_idle_stand_01.csv` | 30 s | Not applicable |
| `Pxx_idle_table_01.csv` | 30 s | Not applicable |
| `Pxx_idle_lap_01.csv` | 30 s | Not applicable |
| `Pxx_curl_slow_01.csv` | 40 s | Record |
| `Pxx_curl_normal_01.csv` | 40 s | Record |
| `Pxx_curl_fast_01.csv` | 40 s | Record |
| `Pxx_other_mixed_01.csv` | 120 s | Not applicable |
| `Pxx_partial_mixed_01.csv` | 60 s | Record complete cycles |

Discard failed recordings (disconnect, cable tug or incorrect movement) and repeat with the next attempt number, such as `_02`.

## 7. Naming

Use `P01_curl_slow_01.csv`: participant, recording label, variant and attempt number starting at 01. Keep the `P` participant prefix as shown and use lowercase labels/variants separated by underscores. Variants are `slow`, `normal`, `fast`, `stand`, `table`, `lap`, `mixed`; filename labels are `curl`, `idle`, `other`, `partial`. Save in `data/sessions/`. Training derives identity and labels from filenames, so names must be accurate.

## 8. Recording procedure

1. Upload `04_imu_stream`, connect the 4517 and computer, and verify seven-column serial output at about 104 rows/s. Avoid DTR/RTS toggling; see the [bring-up notes](../firmware/bringup/README.md).
2. Position the participant and record, replacing the port:

   ```bash
   python3 firmware/bringup/record_serial.py /dev/cu.usbmodemXXXX data/sessions/P01_curl_slow_01.csv 40
   ```

   The recorder stops with an error if the samples freeze, stall, stop arriving or carry an invalid timestamp or value, which is what a loose wire, a sensor power glitch or a board restart looks like. A failed take saves nothing: the recorder writes to `<file>.part` and renames it only when the take completes. Fix the wire, press RST on the Nano, wait 3 s and record the take again.

3. Give the start cue when recording begins. Continue until automatic stop; the observer counts repetitions. Only a repetition that is raised and lowered before the recorder prints its final line counts. Have the participant stop at that line, and note any repetition that was cut off or finished after it.
4. Check each recording:

   ```bash
   python3 ml/train/check_recording.py data/sessions/P01_curl_slow_01.csv
   ```

   Require row count within ±3% of 104 × duration, no adjacent timestamp gap above 15 ms, and dominant `gx` peaks for curls under the proposed mounting. Inspect axis dominance as well as the script output. Repeat failed recordings.
5. Add one row per file to `data/sessions/sessions.csv`: `file`, `participant`, `record_label`, `variant`, `true_reps`, `observer_reps`, `reps_source`, `date`, `recorder`, `notes`.
   - `true_reps` is the number of complete cycles inside the file. It is the value a correct counter should report for that file, so it never includes a repetition that was cut off by the end of the recording or done after it. Empty for idle and other files.
   - `observer_reps` is the live count exactly as the observer reported it. Empty if nobody counted.
   - `reps_source` says where `true_reps` comes from: `observer` (the live count, nothing cut off), `observer_adjusted` (the live count minus repetitions the recording shows were not completed inside the file; say which in the notes), or `imu_inferred` (no live count; read from the `gx` angle afterwards). An `imu_inferred` value comes from the same signal a counter uses, so it is a provisional label and must not be used as ground truth for counting accuracy.
   - When reporting counting accuracy, use only rows whose `reps_source` is `observer`. An `observer_adjusted` count was corrected by looking at the recording and an `imu_inferred` count comes from it entirely; both are for developing and tuning the counter, not for evaluating it. To get `observer` rows, the participant stops at the recorder's final line and the observer says at once whether the last repetition was finished in time.
6. Submit approved anonymized recordings and metadata together on the same day through the team workflow. Example commit: `data: add P01 session (8 files)`. Do not force-add ignored raw data without authorization.

## 9. Excluded material

Do not commit video, audio, names, identity mappings or non-anonymous notes. Do not collect them unless needed; keep private material outside the public repository or in ignored `data/private/`.

## 10. Volume and progress

| Category | Per participant | Five participants (recorded) | v0.2 target (six) |
|---|---|---|---|
| curl | 2 min | 10 min nominal | >=10 min |
| idle | 1.5 min | 7.5 min | >=10 min, not reached |
| other | 2 min | 10 min | >=10 min |
| partial | 1 min | 5 min | Counter checks; no minimum |

Nominal figures; five files are not used for training (`data/sessions/excluded.csv`), four of them P03 curl and partial files, so the curl volume actually trained on is lower.

Track progress in `sessions.csv`.

## 11. Protocol changes

Changes to equipment/settings, mounting, labels or naming may make earlier data incompatible. Update the version/date here and record each dataset's protocol version in metadata notes.

- v0.4 (2026-11-21): section 4 records the five participants actually recorded, including two outside volunteers, and how volunteers are handled; section 3 points to mount v2; section 10 recomputed for five. Procedure, labels and naming unchanged.
- v0.3 (2026-11-19): participant target four team members instead of six; section 10 volumes recomputed. Recording procedure, mounting, labels and naming unchanged, so v0.2 recordings stay compatible. A step-by-step checklist for one participant is in `recording-checklist.md`.
