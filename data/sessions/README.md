# Recorded motion sessions

Anonymised IMU recordings for the motion classifier and the repetition counter. Format and naming are defined in `ml/workplan.md` section 5 and `ml/data-protocol.md`.

Rules:

- Participants appear only as codes (`P01`, `P02`, ...). The code-to-name list stays outside this repository.
- Files are the raw CSV from `firmware/bringup/record_serial.py`: `t_ms,ax,ay,az,gx,gy,gz` at 104 Hz. Do not edit values; if a take is bad, delete the file and record again.
- Nothing identifying: no video, no audio, no health history. Anything that cannot meet this goes in `data/raw/` or `data/private/`, which Git ignores.

## Files left out of training

`excluded.csv` lists recordings that stay in this folder and in `sessions.csv` but are not used for training by `ml/train/train.py`, one line each with the reason. They are still part of the evaluation. Add a file there instead of deleting it, and give a recording-quality reason, not a classifier result.

## Mount versions

The `notes` column of `sessions.csv` says which mounting each file was recorded with.

- **mount v1** (P01, P02): described in `ml/data-protocol.md` section 3. Flat reference `P01_idle_table_01.csv`, mean acceleration (0.69, 0.11, 10.04) m/s².
- **mount v2** (P03, 2026-11-20): the sensor was taken off the bench dumbbell and re-taped. Flat reference `P03_idle_table_01.csv`, mean acceleration (-0.17, 0.70, 10.03) m/s², 6.0° from the v1 reference. A three-curl check before the session put the rotation axis 10° from sensor X, with raising still giving a negative `gx` angle. During the P03 session the axis measured on the curl files was 33-49° from sensor X and each cycle only about 45°.
- **mount v2, P04** (2026-11-20, same taping): flat reading 2.1° from the v2 reference, and the curl files show about 130° per cycle with the rotation axis 11-14° from sensor X, as good as P01. So the sensor tracks the dumbbell, and P03's small cycles most likely came from the movement itself rather than a loose sensor. After a second drop during P04 the flat reading moved 8.4°, mostly a 5° pitch, with the sensor still firm; the last two P04 files were recorded after it.
- **mount v2, P05** (2026-11-20, same taping): flat reading 3.3° from the v2 reference; curl files about 150° per cycle with the rotation axis 5-8° from sensor X.
