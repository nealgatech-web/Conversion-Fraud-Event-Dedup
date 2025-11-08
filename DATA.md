
# DATA.md

This repository uses **synthetic** data. Regenerate with:

```bash
python src/synthetic_events/generate.py --n 50000 --attack-rate 0.08 --seed 42
```

Event schema (JSON Lines):
```json
{
  "id": "evt_xxx",
  "ts": 1710000000.0,
  "user_id": "u_123",
  "device_id": "d_abcd",
  "ip": "203.0.113.5",
  "user_agent": "Mozilla/5.0 ...",
  "campaign_id": "cmp_42",
  "amount": 19.99,
  "fingerprint": "fp_…",
  "label": "normal|replay|farm|slowdrip"
}
```
