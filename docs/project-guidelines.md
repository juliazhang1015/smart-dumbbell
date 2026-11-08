# Project contribution guidelines

This is the ECE 198 Group 57 smart dumbbell repository. Read `../README.md`, `specification.md`, `decisions.md`, and the relevant module README before changing project behavior. Follow `../CONTRIBUTING.md` and `team-guide.md` for normal collaboration. Explicit user instructions take precedence over these project defaults.

## Preserve the agreed baseline

- The project is at concept/planning stage until implementation and tests establish otherwise.
- Version 1 uses one exercise (bicep curl), classes `curl`, `idle`, `other`, Nano ESP32, Adafruit LSM6DSOX + LIS3MDL 9-DoF IMU (4517; magnetometer unused in v1), three buttons, local Wi-Fi records and heart-rate measurement during movement.
- Do not silently replace the hardware, add exercises, remove required features, or change acceptance targets. Present proposed scope changes and update the decision record when accepted.
- Update the English working specification (`specification.md`) when changing requirements. Mark affected exports as needing regeneration if not updated in the same task.
- The 80 mm head width is a candidate, not the committed CAD v0.1 geometry.

## Evidence and artifacts

- Distinguish software checks, simulation, sensor measurements, mechanical inspection and clinical claims.
- Label untested behavior and proposed performance targets explicitly.
- Keep generated presentation claims consistent with current requirements and test evidence.
- Do not overwrite CAD or presentation work belonging to another contributor. Use versioned outputs and update links for accepted versions.
- Never commit secrets or identifiable participant recordings. Do not bypass `.gitignore` to upload raw data without explicit authorization.

## Workflow

Use a focused task branch for normal changes and prepare a reviewable PR. Do not change repository access, invite collaborators, enable protection rules or merge without the required user/team authorization. Initial collaboration-document setup is a bootstrap exception.

Only run checks appropriate to the change. For documentation, validate links and requirement consistency. For code, document and run meaningful available checks; do not invent unavailable test results.
