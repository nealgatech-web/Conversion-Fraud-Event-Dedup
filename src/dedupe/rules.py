from dataclasses import dataclass
from typing import Dict, Tuple
from collections import defaultdict

@dataclass
class Detection:
    event_id: str
    reason: str
    score: float

from dataclasses import dataclass
from typing import Dict, Tuple
from collections import defaultdict
import time


@dataclass
class Detection:
    event_id: str
    reason: str
    score: float


class ReplayWindowDetector:
    """
    Adaptive replay detector.  Starts with a fixed window, then
    self-tunes based on observed replay frequency.
    """
    def __init__(self, window_sec: int = 300, min_window: int = 60, max_window: int = 900):
        self.window = window_sec
        self.min_window = min_window
        self.max_window = max_window
        self.sig_last_ts: Dict[str, float] = {}
        self.sig_counts: Dict[str, int] = defaultdict(int)

        # metrics for online tuning
        self._total_seen = 0
        self._replay_hits = 0
        self._last_tune = time.time()
        self._tune_interval = 60  # seconds between window adjustments

    def observe(self, sig: str, ts: float) -> Tuple[bool, str]:
        """Observe a single event, possibly flag as replay."""
        self._total_seen += 1
        prev = self.sig_last_ts.get(sig)
        self.sig_last_ts[sig] = ts
        self.sig_counts[sig] += 1

        hit = False
        reason = ""
        if prev is not None and ts - prev <= self.window:
            hit = True
            self._replay_hits += 1
            reason = f"replay_within_{self.window}s(count={self.sig_counts[sig]})"

        # periodic tuning
        if time.time() - self._last_tune > self._tune_interval and self._total_seen > 50:
            self._auto_tune()
            self._last_tune = time.time()

        return hit, reason

    def _auto_tune(self):
        """Adjust window length dynamically."""
        rate = self._replay_hits / max(self._total_seen, 1)
        # heuristic: if replay rate high → shrink window, else relax it
        if rate > 0.15:
            self.window = max(int(self.window * 0.9), self.min_window)
        elif rate < 0.05:
            self.window = min(int(self.window * 1.1), self.max_window)
        # reset counters for next cycle
        self._total_seen = 0
        self._replay_hits = 0

    def diagnostics(self) -> Dict[str, float]:
        """Return current tuning state."""
        return {
            "window_sec": self.window,
            "total_seen": self._total_seen,
            "replay_hits": self._replay_hits,
        }


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
