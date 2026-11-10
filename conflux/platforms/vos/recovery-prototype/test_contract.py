import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from state import State
from runtime import read

EVIDENCE = Path(os.environ.get('VOS_EVIDENCE', 'evidence'))
EVIDENCE.mkdir(exist_ok=True, parents=True)

def wait_for(fn, timeout=6):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = fn()
        if value:
            return value
        time.sleep(0.02)
    raise AssertionError('condition timed out')

class Contract(unittest.TestCase):
    def test_01_renderer_loss_and_sensor_uncertainty(self):
        self.integration('renderer')

    def test_02_primary_wedge_independent_watchdog(self):
        self.integration('primary')

    def integration(self, fault):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            supervisor = subprocess.Popen([sys.executable, str(Path(__file__).with_name('runtime.py')), 'watchdog', folder])
            observations = []
            def health():
                return read(root / 'health.json') or {}
            def capture(label):
                observations.append(dict(label=label, health=health(), state=read(root/'state.json')))
            try:
                wait_for(lambda: health().get('data_status') == 'present')
                capture('normal')
                initial = health()
                self.assertEqual(len({supervisor.pid, initial['primary_pid'], initial['renderer_pid']}), 3)
                if fault == 'renderer':
                    (root / 'drop').touch()
                    wait_for(lambda: health().get('data_status') == 'missing')
                    self.assertEqual(health()['renderer_status'], 'running')
                    capture('sensor_missing_renderer_alive')
                    (root / 'drop').unlink()
                    wait_for(lambda: health().get('data_status') == 'present')
                    capture('sensor_recovered')
                    os.kill(initial['renderer_pid'], signal.SIGKILL)
                    wait_for(lambda: health().get('renderer_status') == 'lost')
                    seq = read(root/'state.json')['seq']
                    wait_for(lambda: read(root/'state.json')['seq'] > seq + 2)
                    self.assertTrue(health()['upstream_live'])
                    self.assertEqual(health()['data_status'], 'present')
                    capture('renderer_dead_readings_continue')
                    # Stronger than a surviving file: uncertainty must change while renderer is dead.
                    (root/'drop').touch()
                    wait_for(lambda: health().get('data_status') == 'missing')
                    self.assertEqual(health()['renderer_status'], 'lost')
                    self.assertTrue(health()['upstream_live'])
                    capture('renderer_dead_uncertainty_live')
                else:
                    (root/'wedge').touch()
                    wait_for(lambda: health().get('recoveries') == 1)
                    wait_for(lambda: health().get('data_status') == 'present')
                    self.assertNotEqual(initial['primary_pid'], health()['primary_pid'])
                    self.assertEqual(supervisor.pid, health()['watchdog_pid'])
                    self.assertEqual(initial['renderer_pid'], health()['renderer_pid'])
                    self.assertEqual(health()['renderer_status'], 'running')
                    capture('primary_replaced_and_readable')
            finally:
                (root/'stop').touch()
                try:
                    supervisor.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    supervisor.kill()
                    supervisor.wait()
                    raise
                for path in root.glob('*.json*'):
                    (EVIDENCE/(fault+'-'+path.name)).write_bytes(path.read_bytes())
                (EVIDENCE/(fault+'-observations.json')).write_text(json.dumps(observations, indent=2))
            self.assertEqual(supervisor.returncode, 0)
            events = [json.loads(line) for line in (root/'supervisor.jsonl').read_text().splitlines()]
            names = [x['event'] for x in events]
            if fault == 'renderer':
                lost = next(x for x in events if x['event'] == 'RENDERER_LOST')
                self.assertTrue(lost['upstream_live'])
                self.assertEqual(lost['data_status'], 'present')
                self.assertNotIn('PRIMARY_TIMEOUT', names)
                self.assertIn('missing', [x.get('data_status') for x in events])
            else:
                timeout = next(x for x in events if x['event'] == 'PRIMARY_TIMEOUT')
                self.assertTrue(timeout['process_still_alive'])
                recovered = next(x for x in events if x['event'] == 'RECOVERED')
                self.assertEqual(recovered['surface'], 'primary_path')
                self.assertFalse(recovered['clean_shutdown'])
                self.assertNotIn('RENDERER_LOST', names)

    def test_03_replays_cannot_reset_freshness(self):
        now = [100.0]
        s = State(clock=lambda: now[0], ttl=3)
        rows = []
        self.assertEqual(s.accept('A', 1, 5, 1), 'unknown_session')
        token = s.challenge()
        self.assertFalse(s.handshake('A', 'wrong'))
        self.assertTrue(s.handshake('A', token))
        self.assertEqual(s.accept('A', 10, 42, 1000), 'accepted')
        accepted = s.accepted_at
        now[0] = 105
        for session, seq, expected in [('A',10,'duplicate'), ('A',9,'regression'),
                                       ('B',500,'unknown_session')]:
            before = s.snapshot()
            outcome = s.accept(session, seq, 999, -100000)
            after = s.snapshot()
            self.assertEqual(outcome, expected)
            self.assertEqual(before, after)
            self.assertEqual(s.accepted_at, accepted)
            self.assertEqual(after['data_status'], 'missing')
            rows.append(dict(event='REPLAY_REJECTED', reason=outcome, before=before, after=after))
        self.assertFalse(s.handshake('B', token)) # challenge cannot be replayed
        self.assertTrue(s.handshake('B', s.challenge()))
        self.assertEqual(s.snapshot()['data_status'], 'missing')
        self.assertEqual(s.accept('B', 1, 24, 500), 'accepted')
        now[0] = 110
        before = s.snapshot()
        self.assertEqual(s.accept('A', 999, 777, -999), 'unknown_session')
        self.assertEqual(before, s.snapshot())
        rows.append(dict(event='OLD_SESSION_REJECTED', before=before, after=s.snapshot()))
        self.assertFalse(s.handshake('A', s.challenge()))
        # A new sequence with an old source clock is receipt-fresh, not acquisition-fresh.
        self.assertEqual(s.accept('B', 2, 33, -99999), 'accepted')
        self.assertEqual(s.snapshot()['acquisition_age'], 'unknown')
        rows.append(dict(event='NEW_SEQUENCE_OLD_CLOCK', snapshot=s.snapshot(),
                         limitation='actual acquisition age cannot be inferred'))
        (EVIDENCE/'replay-supervisor.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))

if __name__ == '__main__':
    unittest.main(verbosity=2)
