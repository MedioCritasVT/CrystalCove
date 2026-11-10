"""Upstream truth. Source timestamps are metadata, never freshness authority."""
import time
import secrets

class State:
    def __init__(self, clock=time.monotonic, ttl=0.3):
        self.clock, self.ttl = clock, ttl
        self.session = None
        self.pending = None
        self.used = set()
        self.seq = -1
        self.accepted_at = None
        self.value = None

    def challenge(self):
        self.pending = secrets.token_hex(16)
        return self.pending

    def handshake(self, session, challenge):
        if not session or session in self.used or self.pending is None or challenge != self.pending:
            return False
        self.session = session
        self.used.add(session)
        self.pending = None
        self.seq = -1
        # Session change does not certify a sample or reset any freshness timer.
        self.accepted_at = None
        self.value = None
        return True

    def accept(self, session, seq, value, source_time):
        if session != self.session or self.session is None:
            return 'unknown_session'
        if type(seq) is not int or seq < 0:
            return 'invalid_sequence'
        if seq <= self.seq:
            return 'duplicate' if seq == self.seq else 'regression'
        self.seq, self.value = seq, value
        self.accepted_at = self.clock()
        return 'accepted'

    def snapshot(self):
        age = None if self.accepted_at is None else self.clock() - self.accepted_at
        return dict(session=self.session, seq=self.seq, value=self.value,
                    accepted_at=self.accepted_at, age=age,
                    data_status='missing' if age is None or age > self.ttl else 'present',
                    acquisition_age='unknown')
