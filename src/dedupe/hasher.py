import hashlib
from typing import Dict, Iterable

CANON_KEYS = ["user_id", "device_id", "ip", "campaign_id", "amount"]

def normalize(event: Dict, keys: Iterable[str] = CANON_KEYS) -> str:
    parts = []
    for k in keys:
        v = event.get(k, "")
        if isinstance(v, str):
            v = v.strip().lower()
        parts.append(f"{k}={v}")
    return "|".join(parts)

def fuzzy_signature(event: Dict, keys: Iterable[str] = CANON_KEYS) -> str:
    norm = normalize(event, keys)
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()
