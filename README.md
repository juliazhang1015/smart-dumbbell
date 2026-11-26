# Smart Dumbbell

A lightweight dumbbell that counts bicep curls on the device, reads heart rate at the grip, and logs every set to a laptop. Built for CCCARE participants who do prescribed curls at home on their own: no smartwatch, phone app or cloud account needed.

ECE 198 design project, Group 57, University of Waterloo, Fall 2026.

![Smart dumbbell concept](hardware/renders/Smart_Dumbbell_Concept_Render_v01.png)

*Concept render.*

## Features

- **Counts complete curls on the device.** A motion classifier running on the microcontroller tells curls from rest and from other movement, so shaking, raises and putting the dumbbell down are not counted.
- **Heart rate at the grip.** An optical sensor under the finger; the display shows `--` instead of a stale value when the reading is not valid.
- **Feedback on the dumbbell.** OLED with session state, reps, BPM and the current movement label; an LED while a set is running and a beep on each counted rep.
- **One-button control.** Short press to start, pause or resume; hold to end the set.
- **Wireless logging.** The dumbbell hosts its own Wi-Fi network with a live page and CSV download, and sends a Bluetooth packet every 250 ms to a dashboard on a laptop.
- **Self-contained.** Counting and the display keep working when no computer is connected.

## Hardware

| Part | Component |
|---|---|
| Controller | Arduino Nano ESP32 (ESP32-S3) |
| Motion | Adafruit LSM6DSOX accelerometer and gyroscope, 104 Hz |
| Heart rate | MAX30102 optical pulse sensor, 100 Hz |
| Display | SSD1306 OLED, 128×64 |
| Controls and feedback | One push button, LED, buzzer |
| Power | 5000 mAh USB-C power bank |
| Enclosure | 3D-printed hollow shell holding the power bank, a soldered perfboard hub and the sensors |

All three modules share one I2C bus at 400 kHz. See the [wiring and schematic](hardware/wiring/README.md), the [enclosure CAD](hardware/cad/) and the [parts list](docs/hardware.md).

## How it works

```text
Offline:  recordings -> labels -> training -> C header

LSM6DSOX (accel + gyro, 104 Hz) -> 2 s buffer -> angle rule finds a candidate rep
                                              -> model on the last 2 s: curl? -> count + beep
MAX30102 (100 Hz) -> contact check -> plausible beat intervals -> mean of 4 beats, or "--"
                                              |
                               OLED, LED, buzzer on the device
                                              |
                 Wi-Fi access point (live page, CSV)  ·  Bluetooth packet every 250 ms
```

The motion model is a logistic regression on 31 features of a 2 s window, with three classes (`curl`, `idle`, `other`) and 96 weights. It is trained on a laptop from 40 labelled recordings of five participants and exported as a C header, so the Nano runs it in plain C++ without an ML runtime. A rep is counted when the swing is at least 60° and back and the model labels the 2 s ending at that rep as `curl`. Details are in the [model card](ml/model-card.md).

## Performance

| Measure | Result |
|---|---|
| Classification, leave-one-participant-out over five participants | Macro-F1 0.872 |
| Inference time on the Nano ESP32 | About 2.2 ms per window |
| Counting, firmware rule replayed on the recordings | 217 of 223 complete curls counted |
| False reps during other movement, same replay | 26 without the model check, 1 with it |
| Counting on the board, hand-held | 23 of 23 curls counted, 0 false reps |

Test records are in [tests/results](tests/results/).

## Getting started

Build and upload the firmware with `arduino-cli`:

```bash
arduino-cli compile --fqbn arduino:esp32:nano_nora firmware/SmartDumbbell
arduino-cli upload  --fqbn arduino:esp32:nano_nora -p /dev/cu.usbmodem<id> firmware/SmartDumbbell
```

Required libraries, pin assignments and the serial, Wi-Fi and Bluetooth output formats are in the [firmware README](firmware/SmartDumbbell/README.md).

To view a session on a Mac, run the [live dashboard](software/live-dashboard/README.md). It receives the Bluetooth packets and shows reps, cadence, heart rate and movement labels, with short AI feedback on the current set. Without a dashboard, join the dumbbell's Wi-Fi network and open `http://192.168.4.1/` for the live page and CSV download.

To retrain the model from the recordings, see [ml/README.md](ml/README.md).

## Repository structure

| Directory | Contents |
|---|---|
| `firmware/` | `SmartDumbbell/` is the main sketch; `classifier/` holds the model code and weights, `bringup/` the single-module test sketches, `app/` and `demo/` earlier sketches |
| `ml/` | Recording protocol, training and export pipeline, offline replay tools, model card |
| `data/` | Labelled IMU recordings |
| `software/` | Live dashboard, an earlier Web Bluetooth page (for the older 16-byte packet), Python logger |
| `hardware/` | Enclosure CAD, wiring diagrams, schematic, perfboard hub drawings, renders |
| `docs/` | [Specification](docs/specification.md), [decision log](docs/decisions.md), hardware and budget, background research |
| `tests/` | Dated test records |
| `presentation/` | Pitch and progress-update decks |

## Team

| Member | Main work |
|---|---|
| [Hanson He](https://github.com/HansonHe-UW) | Motion classifier (IMU recordings, training pipeline, on-device inference), model-confirmed rep counting in the firmware, board bring-up and testing, perfboard hub layout, macOS live dashboard |
| [Eric Zhu](https://github.com/ericzhu0220) | Enclosure design and 3D printing, fit checks and assembly of the prototype, help with motion data collection and model training |
| [Zoe Wang](https://github.com/ZoeWang0607) | Electronics and wiring, SmartDumbbell firmware with Wi-Fi and Bluetooth, Web Bluetooth dashboard |
| [Julia Zhang](https://github.com/juliazhang1015) | Circuit schematic, first integrated demo firmware, offline rep-counting tools, Python data logger, background research and documentation |

## License

This is a student course project, not an official University of Waterloo or CCCARE product and not a medical device. No open-source license has been selected.
