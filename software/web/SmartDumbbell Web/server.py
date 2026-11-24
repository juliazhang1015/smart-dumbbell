"""Serve the dashboard and locally received BLE packets on the loopback interface."""
import json
import subprocess
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOCK = threading.Lock()
latest = {"packet": None, "sequence": 0, "received": 0}


def receive(scanner):
    for line in scanner.stdout:
        if not line.startswith("PACKET:"):
            continue
        with LOCK:
            latest.update(packet=line[7:].strip(), received=time.monotonic(),
                          sequence=latest["sequence"] + 1)


class Dashboard(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/live":
            with LOCK:
                body = json.dumps({"packet": latest["packet"], "sequence": latest["sequence"],
                                   "age": round((time.monotonic() - latest["received"]) * 1000)}).encode()
            content_type = "application/json"
        elif self.path in ("/", "/index.html"):
            body = (ROOT / "index.html").read_bytes()
            content_type = "text/html; charset=utf-8"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="smartdumbbell-") as directory:
        executable = Path(directory) / "SmartDumbbellBLE"
        subprocess.run(["swiftc", str(ROOT / "SmartDumbbellBLE.swift"), "-o", str(executable)], check=True)
        with ThreadingHTTPServer(("127.0.0.1", 8001), Dashboard) as server:
            with subprocess.Popen([str(executable)], stdout=subprocess.PIPE, text=True) as scanner:
                threading.Thread(target=receive, args=(scanner,), daemon=True).start()
                print("SmartDumbbell dashboard: http://127.0.0.1:8001/", flush=True)
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    pass
                finally:
                    scanner.terminate()
