"""Serve prototypes/ to the local network and collect benchmark results.

Run:  python tools/bench-server.py [port]
Open: http://<this PC's LAN address>:<port>/05-painted-diorama.html?bench   (on the phone)

A prototype in bench mode POSTs its results to /bench. Each run is saved as
bench-results/<timestamp>.json at the repo root, and a summary is printed here.
"""
import json
import sys
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVE = ROOT / "prototypes"
OUT = ROOT / "bench-results"


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Always serve the latest file: phones cache hard.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_POST(self):
        if self.path.rstrip("/") != "/bench":
            self.send_error(404)
            return
        size = int(self.headers.get("Content-Length", 0))
        if size > 2_000_000:
            self.send_error(413)
            return
        try:
            data = json.loads(self.rfile.read(size))
        except ValueError:
            self.send_error(400)
            return
        OUT.mkdir(exist_ok=True)
        path = OUT / time.strftime("%Y%m%d-%H%M%S.json")
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"\nSaved {path.relative_to(ROOT)}\n{data.get('ua', '')}")
        for s in data.get("scenarios", []):
            print(f"  {s['name']:<40} {s['fps']:>5} fps  p95 {s['gap_p95']:>6} ms  "
                  f"cpu {s['cpu_avg']:>6} ms  {s['draws']:>5} draws  dpr {s['dpr']}")
        sys.stdout.flush()
        self.send_response(204)
        self.end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("0.0.0.0", port), partial(Handler, directory=str(SERVE)))
    print(f"Serving {SERVE} on port {port}. Results go to {OUT}.")
    sys.stdout.flush()
    server.serve_forever()
