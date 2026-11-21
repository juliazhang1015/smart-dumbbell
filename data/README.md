# Data handling

`data/sessions/` holds anonymised IMU recordings for the motion classifier, listed in `data/sessions/sessions.csv`.

| Participant | Recorded | Team member | Agreed to public release |
|---|---|---|---|
| P01 | 2026-11-16 | yes | yes, 2026-11-17 |
| P02 | 2026-11-18 | not recorded | not recorded |
| P03 | 2026-11-20 | yes | yes, 2026-11-20 |
| P04 | 2026-11-20 | **no, an outside volunteer** | not recorded |
| P05 | 2026-11-20 | **no, an outside volunteer** | not recorded |

P04 and P05 are the first outside volunteers. Whether the course sets requirements for recording volunteers has not been confirmed, and their agreement to public release has not been recorded; both should be settled before their files are merged into the public repository.

Raw recordings and session logs are ignored by Git by default. Use anonymous test identifiers, avoid medical histories and identifying video, and keep any participant-to-ID mapping outside this repository. Confirm permission and course requirements before recording volunteers.

A public sample dataset must be deliberately reviewed, appropriately authorized and documented before inclusion. Synthetic samples must be clearly labelled synthetic. An ignored file is not access-controlled or encrypted.
