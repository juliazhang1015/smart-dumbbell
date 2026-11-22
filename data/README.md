# Data handling

`data/sessions/` holds anonymised IMU recordings for the motion classifier, listed in `data/sessions/sessions.csv`.

| Participant | Recorded | Team member | Agreed to public release |
|---|---|---|---|
| P01 | 2026-11-16 | yes | yes, 2026-11-17 |
| P02 | 2026-11-18 | not recorded | yes, confirmed to Hanson He on 2026-11-21 (date of agreement not recorded) |
| P03 | 2026-11-20 | yes | yes, 2026-11-20 |
| P04 | 2026-11-20 | no, an outside volunteer | yes, 2026-11-20 |
| P05 | 2026-11-20 | no, an outside volunteer | yes, 2026-11-20 |

P04 and P05 are the first outside volunteers. Both agreed to the public release of their recordings. Whether the course sets requirements for recording volunteers has not been confirmed.

Raw recordings and session logs are ignored by Git by default. Use anonymous test identifiers, avoid medical histories and identifying video, and keep any participant-to-ID mapping outside this repository. Confirm permission and course requirements before recording volunteers.

A public sample dataset must be deliberately reviewed, appropriately authorized and documented before inclusion. Synthetic samples must be clearly labelled synthetic. An ignored file is not access-controlled or encrypted.
