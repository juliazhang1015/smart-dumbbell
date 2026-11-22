# Recording checklist — one participant, 8 files

Companion to [data-protocol.md](data-protocol.md) (v0.4). Print or keep open while recording. Written 2026-11-19 after P01 and P02; the notes in *italics* are the mistakes those two sessions made.

Budget: about 7 min of data, 30 min including setup. Two people: participant and recorder. The recorder counts and types.

## A. Before the participant arrives

- [ ] Decide which dumbbell: the assembled one (preferred, it is what we deploy) or the bench dumbbell with the taped sensor (mount v2 since 2026-11-20).
- [ ] Sensor not moved since the last participant. If it was re-taped or the enclosure was opened, that is a new mount version — note it in `data-protocol.md` section 3 and in every `sessions.csv` row.
- [ ] Flash `firmware/bringup/04_imu_stream` (SmartDumbbell does not output raw samples). Re-flash SmartDumbbell when done.
- [ ] Terminal shows seven columns `t_ms,ax,ay,az,gx,gy,gz` at about 104 rows/s. Do not toggle DTR/RTS (drops the board into bootloader mode).
- [ ] Orientation check: dumbbell flat on the table, sensor on top, record 5 s, compare the mean acceleration with the mount v2 reference (-0.17, 0.70, 10.03) m/s² (mount v1, P01-P02: 0.69, 0.11, 10.04). Within 5°: same mount. Larger: new mount version — send the file to Hanson before recording anyone.

  ```bash
  python3 firmware/bringup/record_serial.py /dev/cu.usbmodemXXXX /tmp/flat_check.csv 5
  ```

- [ ] Next participant code: P0x (check `data/sessions/sessions.csv` for the last one used). The code-to-name list stays outside the repository.
- [ ] Metronome app ready: 20 / 30 / 50 bpm for slow / normal / fast (3 s / 2 s / 1.2 s per cycle). *P02's "normal" was 4–5 s per cycle, slower than slow — that file is useless as a normal-pace sample.*

## B. With the participant (2 min)

- [ ] Explain: what is recorded (motion only, no video, no name), where it is stored (public repository under a code), that they can stop at any time.
- [ ] Ask and note: hand (L/R), regular strength training (Y/N). Nothing else (no age, height, medical history).
- [ ] Agreement to public release of the recordings — write the date into `data/README.md` afterwards.
- [ ] Show the curl: arm down at the side, raise until the forearm is near vertical and the dumbbell near the shoulder, lower fully. Full range every time; no pauses in the `curl` files.

## C. The eight files

Command pattern (replace port, code, file, seconds):

```bash
python3 firmware/bringup/record_serial.py /dev/cu.usbmodemXXXX data/sessions/P0x_idle_stand_01.csv 30
```

The recorder prints a final line when the time is up. **Call "stop" at that line.** Only a repetition raised *and* lowered before that line counts.

| # | File | s | What the participant does | Recorder writes down |
|---|---|---|---|---|
| 1 | `P0x_idle_stand_01.csv` | 30 | Standing, dumbbell hanging at the side, still | — |
| 2 | `P0x_idle_table_01.csv` | 30 | Dumbbell on the table, nobody touching it | — |
| 3 | `P0x_idle_lap_01.csv` | 30 | Seated, dumbbell resting on the lap | — |
| 4 | `P0x_curl_slow_01.csv` | 40 | Continuous full curls, 3 s per cycle (metronome 20) | live count; was the last one lowered before the final line? |
| 5 | `P0x_curl_normal_01.csv` | 40 | Continuous full curls, 2 s per cycle (metronome 30) | same |
| 6 | `P0x_curl_fast_01.csv` | 40 | Continuous full curls, 1.2 s per cycle (metronome 50) | same |
| 7 | `P0x_other_mixed_01.csv` | 120 | 5 × pick up / put down, walk 20 s, 10 lateral raises, 10 front raises, random shaking 20 s | — |
| 8 | `P0x_partial_mixed_01.csv` | 60 | 10 half raises, 5 raises with a 3 s hold at the top, then (3 full curls + 5 s rest) × 3 | count of **full-range** cycles (holds count, half raises do not); which sets were completed |

After **each** file, before the next one:

```bash
python3 ml/train/check_recording.py data/sessions/P0x_curl_slow_01.csv
```

- [ ] `PASS`. On `FAIL` (gap, rate, wrong axis) or a wire tug / wrong movement: keep the file out of the repo, redo as `_02`, and write in the notes why `_01` was discarded.
- [ ] For curl files: the live count and whether the last rep was finished in time are written down **now**, not reconstructed later. *P01 and P02 together produced six curl files and only one clean `observer` count; the rest had to be corrected from the signal, which disqualifies them for AT-02.*

## D. After the participant leaves (10 min)

- [ ] One row per file in `data/sessions/sessions.csv`, columns `file,participant,record_label,variant,true_reps,observer_reps,reps_source,date,recorder,notes`.
  - `true_reps`: complete reps inside the file. `observer_reps`: the live count. `reps_source`: `observer` when they are equal and nothing was cut off; `observer_adjusted` when a cut-off rep was removed (say which in the notes); `imu_inferred` only if no live count exists.
  - `recorder`: a name, not "team".
  - `notes` start with `protocol v0.2; mount v2` (or the new version), then `hand R/L; strength training Y/N`, then anything unusual (discarded takes, pace actually achieved, wire issues).
- [ ] `data/README.md`: add the participant code and the date of their agreement to public release.
- [ ] Commit the CSVs and `sessions.csv` together the same day, e.g. `data: add P03 session (8 files)`, open a PR, ask for review. Never `git add -f` anything that `.gitignore` excludes.
- [ ] Tell Hanson: he re-runs `train.py` (leave-one-participant-out), the feature ablation and the counter replay, and regenerates `model_weights.h` if the result holds.

## E. Participants

P01-P05 are recorded (2026-11-16 to 2026-11-20): P01, P02 and P03 are team members, P04 and P05 outside volunteers. The next participant is P06. An outside volunteer is fine when they agree to public release before the files are committed (section B, and the table in `data/README.md`). All five so far are right-handed and only P04 does regular strength training, so a left-handed or strength-training participant adds the most. Any AT-01 statement gives the actual count and composition, not "all team members".
