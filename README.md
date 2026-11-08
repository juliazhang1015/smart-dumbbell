# Smart Dumbbell

ECE 198 student design project, Group 57, University of Waterloo.

A proposed lightweight smart dumbbell for CCCARE participants who can independently perform prescribed bicep curls at home. The device is intended to count complete repetitions, show progress, measure heart rate during movement, and send session records to a computer.

**Status: early prototype development.** Specifications, concept CAD and pitch materials are available, along with bring-up firmware, an integrated application draft, a synthetic-data classifier and a computer logger tested against a mock server. Initial bench checks are recorded in [tests/results](tests/results/); full-system integration and AT-01–AT-10 acceptance remain unverified.

![Smart dumbbell concept](hardware/renders/Smart_Dumbbell_Concept_Render_v01.png)

*Concept appearance study. This is not a photograph of a built prototype or a dimensionally exact CAD rendering.*

## Start here

- [Bluetooth training dashboard](software/web/) and [connection instructions](software/README.md#bluetooth-dashboard)
- **[Team repository guide](docs/team-guide.md)**
- [Handoff brief for teammates](docs/handoff.md)
- [Working specification](docs/specification.md)
- [Specification PDF snapshot](docs/exports/Smart_Dumbbell_Preliminary_Specification_v01.pdf)
- [Decisions and open questions](docs/decisions.md)
- [Hardware and budget](docs/hardware.md)
- [Research assignments](docs/research-plan.md)
- [Pitch deck](presentation/Smart_Dumbbell_Pitch_Waterloo_v02.pptx), [speaker script](presentation/speaker_script.txt), and [editable script](presentation/Smart_Dumbbell_Speaker_Script_v02.docx)
- [CAD model](hardware/cad/Smart_Dumbbell_Concept_v01.dwg) and [model notes](hardware/cad/MODEL_NOTES.txt)
- [Schematic, wiring diagram and net list, v1](hardware/wiring/README.md)

## Version 1 scope

- One exercise: bicep curl. Model classes: `curl`, `idle`, `other`.
- On-device inference and complete-cycle counting.
- OLED feedback and three session-control buttons.
- Heart-rate measurement during movement, with unreliable readings marked invalid.
- Local Wi-Fi communication and computer logging.
- Internal power and a custom hollow enclosure; no personal smartwatch required.
- Team purchase budget target: CAD 100 including taxes and shipping, subject to the borrowing assumptions in the specification.

The main feasibility risk is obtaining reliable optical heart-rate signals while gripping and moving the dumbbell. All acceptance numbers are proposed targets, not results.

## Proposed architecture

```text
Development: motion recordings -> labels -> computer training/testing -> deployed model

LSM6DSOX (accel + gyro) -> on-device model -> movement-cycle logic -> repetition count
MAX30102 -> signal processing / quality checks -> heart rate or invalid status
                                      |
                            OLED + local Wi-Fi
                                      |
                            computer view + CSV
```

Counting, sensing, and the display are intended to continue when the computer disconnects. The current specification uses the computer to set targets. Persistent offline history and later backfill are not yet part of the agreed baseline.

## Repository structure

| Directory | Contents |
|---|---|
| `docs/` | Specification, handoff, team guide, research, decisions and exported snapshot |
| `hardware/` | Native CAD, model generator, rendering, assumptions, and the wiring draft |
| `presentation/` | Current pitch and matching narration |
| `firmware/` | Nano ESP32 bring-up sketches, classifier and integrated application draft |
| `software/` | Bluetooth dashboard, computer data logger, mock server and usage instructions |
| `ml/` | Recording protocol, workplan and training/export pipeline; current weights use synthetic data |
| `tests/` | Test templates, initial bench records and host software checks |
| `data/` | Data-handling guidance; no participant recordings |

## Next milestones

- [x] Write preliminary requirements and acceptance targets.
- [x] Create a concept CAD model and appearance render.
- [x] Prepare a pitch deck and narration.
- [x] Select the controller and IMU and record prices (2026-10-31).
- [x] Nano ESP32 and 4517 received and brought up: upload, Wi-Fi AP, I2C, 104 Hz IMU stream (2026-11-03).
- [ ] Confirm loan modules, dimensions, connector clearances, and budget.
- [ ] Test grip heart-rate feasibility against a synchronized reference.
- [ ] Build a rule-based counting baseline and collect labelled motion recordings.
- [ ] Train and evaluate a compact classifier on held-out sessions.
- [ ] Integrate local control, display, Wi-Fi and recording.
- [ ] Revise and test the enclosure before fabrication.

## Collaboration

Follow the [team guide](docs/team-guide.md) and [contribution workflow](CONTRIBUTING.md). Task, PR and test-record templates are included. These are workflow conventions, not automatically enforced branch-protection rules.

Use short branches such as `docs/hardware-check`, `firmware/sensor-readout`, and `ml/data-protocol`. Open a pull request for changes, explain what changed and what evidence supports it, and ask a teammate to review before merging. Keep requirements, hardware choices, CAD notes and presentation claims consistent.

Update the Markdown specification first. Treat dated PDF/PPTX exports as snapshots and regenerate them when needed. Do not record planned tests as passed.

## Project context

This is a student course project, not an official University of Waterloo or CCCARE product. The pitch uses the supplied University of Waterloo Faculty of Engineering presentation template. Team review and physical validation remain necessary.

The repository contains project-authored artifacts. Course handouts and the original university template remain in the course workspace. No open-source license has been selected; public visibility does not itself grant a license to reuse all material.
