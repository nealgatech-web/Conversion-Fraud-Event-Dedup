from dataclasses import dataclass
from typing import Dict, Tuple
from collections import defaultdict

@dataclass
class Detection:
    event_id: str
    reason: str
    score: float

class ReplayWindowDetector:
    def __init__(self, window_sec: int = 300):
        self.window = window_sec
        self.sig_last_ts: Dict[str, float] = {}
        self.sig_counts: Dict[str, int] = defaultdict(int)

    def observe(self, sig: str, ts: float) -> Tuple[bool, str]:
        prev = self.sig_last_ts.get(sig)
        self.sig_last_ts[sig] = ts
        self.sig_counts[sig] += 1
        if prev is None:
            return False, ""
        if ts - prev <= self.window:
            return True, f"replay_within_{self.window}s(count={self.sig_counts[sig]})"
        return False, ""

class ClusterAttribution:
    def __init__(self):
        self.by_ip = defaultdict(int)
        self.by_fp = defaultdict(int)

    def add(self, ip: str, fingerprint: str):
        if ip:
            self.by_ip[ip] += 1
        if fingerprint:
            self.by_fp[fingerprint] += 1

    def top_sources(self, k: int = 10):
        ips = sorted(self.by_ip.items(), key=lambda x: x[1], reverse=True)[:k]
        fps = sorted(self.by_fp.items(), key=lambda x: x[1], reverse=True)[:k]
        return {"ip": ips, "fingerprint": fps}
