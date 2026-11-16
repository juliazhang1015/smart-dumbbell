#!/usr/bin/env python3
"""Save the CSV stream from 04_imu_stream to a file.

usage: python3 record_serial.py PORT OUTFILE [seconds]
  PORT     e.g. /dev/cu.usbmodem1101 (macOS) or COM5 (Windows)
  OUTFILE  e.g. data/sessions/P01_curl_slow_01.csv
needs: pip install pyserial   (or: uv run --with pyserial python record_serial.py ...)
Stops after `seconds` (default 30) or Ctrl-C.

The sketch prints its header only once at boot, so the recorder does not wait for it:
it writes the header itself and keeps every line that has seven numeric fields.
The first line after opening the port is dropped because it may be cut in half.

If a jumper comes loose the sketch keeps printing, but the rows are useless: all zeros after
a power glitch (the sensor wakes up in power-down), or the same values repeated about once a
second while I2C reads time out. The recorder stops with an error in both cases, because such
a file can look fine at a glance. It also stops if the board goes silent after the take has
started; that is timed on the computer's clock, so it works when no rows arrive at all.
Fix the wire, press RST on the Nano (or re-plug USB) and record again.
"""
import sys, time
import serial

HEADER = "t_ms,ax,ay,az,gx,gy,gz"
port, out = sys.argv[1], sys.argv[2]
seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0


def is_sample(line):
    parts = line.split(",")
    if len(parts) != 7:
        return False
    try:
        [float(p) for p in parts]
    except ValueError:
        return False
    return True


FROZEN_LIMIT = 10                       # identical consecutive rows (about 0.1 s) before giving up
STALL_MS = 100                          # gap between board timestamps that means samples were lost
HOST_STALL_S = 0.5                      # computer-clock time without a valid row before giving up
READ_TIMEOUT_S = 0.2                    # serial read timeout; must be shorter than HOST_STALL_S


def fail(why, n, out):
    sys.exit(f"ERROR: {why} after {n} rows. A wire is loose or the sensor lost power. Check the four "
             f"wires, press RST on the Nano, wait 3 s, then record again. Delete {out}.")


with serial.Serial(port, 115200, timeout=READ_TIMEOUT_S) as ser, open(out, "w") as f:
    f.write(HEADER + "\n")
    ser.readline()                      # possibly partial line
    opened = time.monotonic()
    started = None                      # computer time of the first valid row
    last_good = None                    # computer time of the latest valid row
    n = 0
    frozen = 0
    last_values = None
    t_first = t_last = None
    try:
        while True:
            line = ser.readline().decode("ascii", "ignore").strip()
            now = time.monotonic()
            if not is_sample(line):         # read timed out, or the line is not a sample
                if started is None:
                    if now - opened > 5:
                        sys.exit(f"ERROR: no samples from {port} in 5 s. Is 04_imu_stream flashed?")
                elif now - last_good > HOST_STALL_S:
                    fail(f"no samples from the board for {now - last_good:.1f} s", n, out)
                continue
            t_ms, values = line.split(",", 1)
            frozen = frozen + 1 if values == last_values else 0
            last_values = values
            if frozen >= FROZEN_LIMIT:
                fail("IMU values are frozen (" + values + ")", n, out)
            if t_last is not None and float(t_ms) - t_last > STALL_MS:
                fail(f"sample stream stalled for {float(t_ms) - t_last:.0f} ms", n, out)
            if started is None:
                started = now
            last_good = now
            f.write(line + "\n")
            n += 1
            t_last = float(t_ms)
            if t_first is None:
                t_first = t_last
            if now - started >= seconds:
                break
    except KeyboardInterrupt:
        pass
if n > 1 and t_last > t_first:
    span = (t_last - t_first) / 1000.0
    print(f"wrote {n} samples to {out}: {span:.1f} s, {(n - 1) / span:.1f} Hz")
else:
    print(f"wrote {n} samples to {out}")
