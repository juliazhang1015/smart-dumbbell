# Computer interface and logging

## Live dashboard with AI coach (macOS)

[live-dashboard/](live-dashboard/README.md): the newer dashboard. A small local server receives the dumbbell's Bluetooth packets on a Mac, shows them with cadence, heart-rate and movement-label panels, and asks Claude for short feedback on the current set. Runs against `firmware/SmartDumbbell` from `main`.

## Bluetooth dashboard

Open [web/index.html](web/index.html) from a local checkout in Microsoft Edge or Google Chrome on Windows. Power the Nano ESP32 via USB-C from the power bank. Use the wireless firmware that advertises the SmartDumbbell BLE service (823ef401-1d82-41f6-b689-68aedcbb1960).

Click **Connect dumbbell**, select **SmartDumbbell**, then use the physical button to control the session. The computer can stay on its regular Wi-Fi. Keep the page open while training and click **Export CSV** before closing it. The dashboard shows repetitions, active time and estimated BPM. A dash indicates an unavailable heart-rate sample.

### BLE interface the dashboard expects

`firmware/SmartDumbbell` with `USE_BLE 1` implements it, with one extra byte at offset 16 (classifier label: 0 curl, 1 idle, 2 other, 255 none yet) and a notification every 250 ms. **This page accepts 16-byte packets only, so with the current firmware it connects but shows nothing**; use `live-dashboard/`, which reads both lengths. `firmware/app` v1 uses a Nordic UART service with JSON instead. The interface:

- GATT service `823ef401-1d82-41f6-b689-68aedcbb1960`, advertised so that Web Bluetooth can filter on it.
- Characteristic `823ef402-1d82-41f6-b689-68aedcbb1960`, readable and notifying, one 16-byte little-endian sample about once per second:

| Offset | Type | Field |
|---|---|---|
| 0 | u8 | packet version, must be 1 (other values are ignored) |
| 1 | u8 | state: 0 Ready, 1 Running, 2 Paused, 3 Done |
| 2 | u32 | session number, increments on each start |
| 6 | u32 | active time in ms, pauses excluded |
| 10 | u32 | repetitions in this session |
| 14 | u16 | heart rate in bpm, 0 when no valid value (shown as a dash) |

The HTTP logger below uses a different, richer record (`session_id`, `sequence`, `heart_rate_valid`, `signal_quality`, ...). One of the two is the interface of record; decide and map the fields before AT-08 testing.

## Python HTTP logger (simulation prototype)

**Status: simulated only.** The HTTP endpoints `/status` (GET) and `/target` (POST) are provisional examples for Role ④ to confirm; no real Nano ESP32 integration has been tested.

## macOS setup

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r software/requirements.txt
```

## Run

In **terminal 1** (stay running):

```bash
python3 software/mock_server.py
```

In **terminal 2** (also from repository root):

```bash
source .venv/bin/activate
python3 software/data_logger.py --url http://127.0.0.1:5000 --target 10 --csv data/session_logs/session_log.csv
```

The program displays session state, repetitions and heart rate once per second. Stop with **Ctrl+C**. Open the CSV in VS Code. For a short run, add `--max-polls 10`.

### Test disconnect/reconnect

Stop the server in terminal 1 using Ctrl+C; the client will record one `disconnected` event rather than invent data. Restart the mock server, and the client will log `reconnected` and `new_session` if the session ID changed. The mock server restarts at `mock-001`, so for realistic session-change testing, call `curl -X POST http://127.0.0.1:5000/demo/reset` while it is running (this demo-only endpoint increments the session ID).

## CSV

`event=sample` is a newly accepted measurement. `duplicate_or_out_of_order`, `sequence_gap`, `disconnected`, `reconnected` and `new_session` are diagnostic events, not new sensor measurements. `received_at_utc` is computer receive time; `elapsed_ms` and `sequence` are preserved from the simulated device. Invalid BPM is blank in the CSV, with `heart_rate_valid=False`. The logger appends to the chosen path; choose a fresh path for each test to avoid combining runs inadvertently. Keep logs under `data/session_logs/` (ignored by git); do not write them into `software/`.

## Unit test

From the repository root, with the venv active:

```bash
python3 -m unittest tests.test_data_logger
```

This checks `SessionLogger` only (duplicate/gap detection, invalid heart rate, disconnect/new-session events). It does not exercise the HTTP loop or the mock server.

## Limitations / next actions

- Confirm JSON data types, enum values, clock meaning, endpoint paths and `POST /target` response with firmware owner before hardware testing.
- Current prototype does not verify authentication, time sync, sensor accuracy, session summary or full AT-08 with actual hardware.
- The device's own `connection_state` field is preserved; network reachability is additionally tracked by computer-side events.
- Do not upload private participant data or real health records.
