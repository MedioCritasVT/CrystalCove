#!/usr/bin/env python3
"""CFX-M001-A: unprivileged simulated telemetry service (standard library only)."""
import argparse
import json
import math
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class State:
    def __init__(self):
        self.instance = str(uuid.uuid4())
        self.started = time.monotonic()
        self.lock = threading.Lock()
        self.sequence = 1
        self.payload = self.make_payload()

    def make_payload(self):
        elapsed = time.monotonic() - self.started
        return {
            'schema_version': '0.1',
            'source': 'vos-simulator',
            'service_instance_id': self.instance,
            'sequence': self.sequence,
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'monotonic_elapsed_ms': int(elapsed * 1000),
            'cpu_temperature_c': round(52 + 3 * math.sin(elapsed / 5), 1),
            'fan_speed_rpm': int(1200 + 80 * math.sin(elapsed / 4)),
            'state': 'nominal',
        }

    def generate(self, stop):
        while not stop.wait(0.5):
            with self.lock:
                self.sequence += 1
                self.payload = self.make_payload()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/state':
            with self.server.state.lock:
                body = dict(self.server.state.payload)
        elif self.path == '/health':
            body = {'schema_version': '0.1', 'source': 'vos-simulator',
                    'service_instance_id': self.server.state.instance,
                    'status': 'running'}
        else:
            self.send_error(404, 'Unknown endpoint')
            return
        data = json.dumps(body, separators=(',', ':')).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print('%s %s' % (self.log_date_time_string(), fmt % args), flush=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('port must be between 1 and 65535')
    state = State()
    stop = threading.Event()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    server.state = state
    worker = threading.Thread(target=state.generate, args=(stop,), daemon=True)
    worker.start()
    print(f'CFX-M001-A listening at http://127.0.0.1:{args.port} (Ctrl+C to stop)', flush=True)
    try:
        server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        server.server_close()
        worker.join(timeout=1)

if __name__ == '__main__':
    main()
