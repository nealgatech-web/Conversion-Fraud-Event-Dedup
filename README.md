
# Event Deduplication & Provenance for Attribution (Conversion Fraud)

**One-line**: A reproducible pipeline that detects duplicate / replayed / bot-farmed conversion events and attributes likely sources (IP clusters, device fingerprints, replay windows).

## Why this matters
- Reduces economic waste from fraudulent or accidental duplicate events.
- Transparent, reproducible methodology and code organizations can adopt or extend.
- Ships with a synthetic data generator, baseline heuristics, and an API demo.

## Quick start
```bash
# 1) Create venv and install deps
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) Generate synthetic events (normal + attacks) => data/events.jsonl
python src/synthetic_events/generate.py --n 50000 --attack-rate 0.08 --seed 42

# 3) Run dedupe pipeline (flags duplicates/attacks) => outputs/report.jsonl + outputs/summary.json
python3 -m src.dedupe.pipeline --input data/events.jsonl \
    --window-sec 300 \
    --sig-fields user_id,device_id,ip,campaign_id,amount \
    --out-dir outputs --summary

# 4) (Optional) Serve API demo
uvicorn src.api.main:app --reload
# POST events to /ingest, then browse GET /summary and /suspects
```

## Repo layout
```
event-dedup-provenance/
├── src/
│   ├── synthetic_events/generate.py
│   ├── dedupe/hasher.py
│   ├── dedupe/rules.py
│   ├── dedupe/pipeline.py
│   ├── analytics/graph.py
│   └── api/main.py
├── tests/
├── data/ (gitignored)
├── outputs/ (gitignored)
├── docker/ Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── DATA.md
├── EVALUATION.md
├── IMPACT.md
├── CONTRIBUTING.md
├── CITATION.cff
├── LICENSE
└── docs/whitepaper_event_dedup.pdf
```

## Reproducibility
- `requirements.txt` pins versions for deterministic runs.
- All scripts are CLI-driven and support `--seed`.
- `scripts/run_all.sh` executes the pipeline end-to-end.

## What this repo provides
- **Synthetic generator** for normal + adversarial events (replay, click-farm, slow-drip).
- **Baseline deduper** using normalized fuzzy signatures + temporal windows.
- **Attribution**: grouping by IP / fingerprint to surface sources.
- **API** for triage and quick inspection (FastAPI).

---

© 2025 Apache-2.0. See `LICENSE`.
