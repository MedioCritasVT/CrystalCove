"""Local subprocess model; files are atomic IPC, not durable production telemetry."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from state import State

HERE = Path(__file__).resolve()

def write(path, data):
    path = Path(path)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data))
    temp.replace(path)

def read(path):
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def event(root, name, **fields):
    row = dict(event=name, monotonic=time.monotonic(), pid=os.getpid(), **fields)
    with (Path(root) / 'supervisor.jsonl').open('a') as f:
        f.write(json.dumps(row) + '\n')
        f.flush()

def child(role, root):
    return subprocess.Popen([sys.executable, str(HERE), role, str(root)],
                            stdout=subprocess.DEVNULL, stderr=None)

def primary(root):
    s = State()
    nonce = s.challenge()
    assert s.handshake('sensor-' + str(os.getpid()), nonce)
    seq = 0
    while True:
        if (root / 'wedge').exists():
            # Intentionally never checks shutdown again. Only an external owner can recover.
            while True:
                time.sleep(0.1)
        if (root / 'stop').exists():
            return
        if not (root / 'drop').exists():
            seq += 1
            s.accept(s.session, seq, 42, time.time())
        write(root / 'state.json', dict(s.snapshot(), owner_pid=os.getpid()))
        write(root / 'primary-heartbeat.json', dict(at=time.monotonic(), pid=os.getpid()))
        time.sleep(0.03)

def renderer(root):
    while not (root / 'stop').exists():
        state = read(root / 'state.json')
        write(root / 'display.json', dict(state=state, renderer_pid=os.getpid(), at=time.monotonic()))
        time.sleep(0.03)

def watchdog(root):
    p, r = child('primary', root), child('renderer', root)
    started = time.monotonic()
    previous_data = None
    renderer_lost = False
    recoveries = 0
    event(root, 'START', primary_pid=p.pid, renderer_pid=r.pid)
    try:
        while not (root / 'stop').exists():
            now = time.monotonic()
            write(root / 'watchdog-heartbeat.json', dict(at=now, pid=os.getpid()))
            hb = read(root / 'primary-heartbeat.json')
            heartbeat_valid = hb and hb['pid'] == p.pid
            gap = now - hb['at'] if heartbeat_valid else now - started
            upstream_live = bool(heartbeat_valid and gap <= 0.6 and p.poll() is None)
            state = read(root / 'state.json')
            data = state['data_status'] if upstream_live and state else 'unknown'
            if data != previous_data:
                event(root, 'DATA_STATUS', data_status=data, upstream_live=upstream_live)
                previous_data = data
            if r.poll() is not None and not renderer_lost:
                renderer_lost = True
                event(root, 'RENDERER_LOST', upstream_live=upstream_live, data_status=data,
                      renderer_pid=r.pid, exitcode=r.returncode)
            write(root / 'health.json', dict(upstream_live=upstream_live, data_status=data,
                  renderer_status='lost' if renderer_lost else 'running', primary_pid=p.pid,
                  renderer_pid=r.pid, watchdog_pid=os.getpid(), recoveries=recoveries))
            if gap > 0.6 or p.poll() is not None:
                event(root, 'PRIMARY_TIMEOUT', gap=gap, old_pid=p.pid,
                      process_still_alive=p.poll() is None)
                old = p.pid
                p.kill()
                p.wait(timeout=2)
                (root / 'wedge').unlink(missing_ok=True)
                p = child('primary', root)
                started = time.monotonic()
                # Wait for a new-PID heartbeat, not merely successful process creation.
                deadline = started + 3
                while time.monotonic() < deadline:
                    new = read(root / 'primary-heartbeat.json')
                    if new and new['pid'] == p.pid:
                        break
                    time.sleep(0.02)
                else:
                    raise RuntimeError('replacement primary did not become ready')
                recoveries += 1
                event(root, 'RECOVERED', surface='primary_path', old_pid=old, new_pid=p.pid,
                      clean_shutdown=False, ready_heartbeat=new)
            time.sleep(0.02)
    finally:
        for proc in (p, r):
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=2)
        event(root, 'STOP')

if __name__ == '__main__':
    globals()[sys.argv[1]](Path(sys.argv[2]))
