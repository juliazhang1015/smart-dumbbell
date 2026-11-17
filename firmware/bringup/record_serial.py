#!/usr/bin/env python3
"""Save the CSV stream from 04_imu_stream to a file.

usage: python3 record_serial.py PORT OUTFILE [seconds]
  PORT     e.g. /dev/cu.usbmodem1101 (macOS) or COM5 (Windows)
  OUTFILE  e.g. data/sessions/P01_curl_slow_01.csv
needs: pip install pyserial   (or: uv run --with pyserial python record_serial.py ...)
Stops after `seconds` (default 30) or Ctrl-C.

The sketch prints its header only once at boot, so the recorder does not wait for it:
it writes the header itself and keeps every row of seven finite numbers.
The first line after opening the port is dropped because it may be cut in half.

A take is written to OUTFILE.part and renamed to OUTFILE only when it completes, so a
failed take never leaves a file under the final name and never replaces an earlier good
file of that name. The partial file is removed on failure.

The recorder stops with an error, exit status 1, when the data cannot be trusted:
- the same six sensor values repeat (all zeros after a power glitch, when the sensor wakes
  up in power-down, or stale values while I2C reads time out);
- board timestamps jump forward by more than 100 ms (samples were lost);
- a timestamp is negative, repeats or goes backwards (the board restarted);
- a value is NaN or infinite;
- no valid row arrives for 0.5 s after the take has started, timed on the computer's
  clock so that it works when nothing arrives at all;
- no valid row arrives in the first 5 s.
A loose jumper is the usual cause. Fix the wire, press RST on the Nano (or re-plug USB),
wait 3 s and record again.
"""
import math
import os
import sys
import time

import serial

HEADER = "t_ms,ax,ay,az,gx,gy,gz"
FROZEN_LIMIT = 10                       # identical consecutive rows (about 0.1 s) before giving up
STALL_MS = 100                          # gap between board timestamps that means samples were lost
HOST_STALL_S = 0.5                      # computer-clock time without a valid row before giving up
READ_TIMEOUT_S = 0.2                    # serial read timeout; must be shorter than HOST_STALL_S
START_TIMEOUT_S = 5.0                   # time allowed for the first valid row


class TakeFailed(Exception):
    pass


def parse_row(line):
    """Seven comma-separated numbers -> list of floats; anything else -> None."""
    parts = line.split(",")
    if len(parts) != 7:
        return None
    try:
        return [float(p) for p in parts]
    except ValueError:
        return None


def record(ser, f, seconds):
    """Copy valid rows from ser to f. Returns (rows, first t_ms, last t_ms)."""
    f.write(HEADER + "\n")
    ser.readline()                      # possibly partial line
    opened = time.monotonic()
    started = None                      # computer time of the first valid row
    last_good = None                    # computer time of the latest valid row
    n = 0
    frozen = 0
    last_values = None
    t_first = t_last = None
    while True:
        line = ser.readline().decode("ascii", "ignore").strip()
        now = time.monotonic()
        row = parse_row(line)
        if row is None:                 # read timed out, or the line is not a sample
            if started is None:
                if now - opened > START_TIMEOUT_S:
                    raise TakeFailed(f"no samples in {START_TIMEOUT_S:.0f} s. Is 04_imu_stream flashed?")
            elif now - last_good > HOST_STALL_S:
                raise TakeFailed(f"no samples from the board for {now - last_good:.1f} s after {n} rows")
            continue
        if not all(math.isfinite(v) for v in row):
            raise TakeFailed(f"non-finite value in row '{line}' after {n} rows")
        t = row[0]
        if t < 0:
            raise TakeFailed(f"negative timestamp {t:.0f} ms after {n} rows")
        if t_last is not None:
            if t <= t_last:
                raise TakeFailed(f"timestamp went from {t_last:.0f} to {t:.0f} ms after {n} rows "
                                 f"(repeated or backwards; the board may have restarted)")
            if t - t_last > STALL_MS:
                raise TakeFailed(f"sample stream stalled for {t - t_last:.0f} ms after {n} rows")
        values = line.split(",", 1)[1]
        frozen = frozen + 1 if values == last_values else 0
        last_values = values
        if frozen >= FROZEN_LIMIT:
            raise TakeFailed(f"IMU values are frozen ({values}) after {n} rows")
        if started is None:
            started = now
        last_good = now
        f.write(line + "\n")
        n += 1
        t_last = t
        if t_first is None:
            t_first = t
        if now - started >= seconds:
            return n, t_first, t_last


def main(argv):
    port, out = argv[1], argv[2]
    seconds = float(argv[3]) if len(argv) > 3 else 30.0
    part = out + ".part"
    result = None
    interrupted = False
    try:
        with serial.Serial(port, 115200, timeout=READ_TIMEOUT_S) as ser, open(part, "w") as f:
            try:
                result = record(ser, f, seconds)
            except KeyboardInterrupt:   # stopping by hand keeps what was recorded
                interrupted = True
    except TakeFailed as e:
        if os.path.exists(part):
            os.remove(part)
        print(f"ERROR: {e}. Nothing was saved to {out}. A wire is loose or the sensor lost power: check the "
              f"four wires, press RST on the Nano, wait 3 s, then record again.", file=sys.stderr)
        return 1
    except BaseException:               # unplugged port, disk error: do not leave a partial file
        if os.path.exists(part):
            os.remove(part)
        raise
    if interrupted:
        rows = max(0, sum(1 for _ in open(part)) - 1)
        if rows == 0:                   # nothing recorded: keep any earlier file of that name
            os.remove(part)
            print(f"stopped by Ctrl-C before any sample arrived. Nothing was saved to {out}.", file=sys.stderr)
            return 1
        os.replace(part, out)
        print(f"stopped by Ctrl-C: wrote {rows} samples to {out}")
        return 0
    os.replace(part, out)
    n, t_first, t_last = result
    span = (t_last - t_first) / 1000.0
    if n > 1 and span > 0:
        print(f"wrote {n} samples to {out}: {span:.1f} s, {(n - 1) / span:.1f} Hz")
    else:
        print(f"wrote {n} samples to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
