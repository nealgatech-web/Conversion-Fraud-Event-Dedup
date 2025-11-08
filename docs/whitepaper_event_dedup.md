# Event Deduplication and Provenance for Conversion Fraud Detection

## Abstract
This project presents an open-source, adaptive event deduplication pipeline for detecting fraudulent or repeated conversion events. It integrates rule-based detection, machine learning extensibility, and an API layer for real-time streaming analysis. The system is designed for transparency and reproducibility — enabling engineers and analysts to explore scalable, data-driven fraud mitigation methods.

---

## 1. Introduction
Duplicate and replayed conversion events are common in advertising, affiliate tracking, and e-commerce systems. They inflate metrics, distort attribution, and can signal malicious bot or replay behavior.

The **Event Deduplication and Provenance** system provides:
- An offline batch deduplication pipeline  
- A dynamic adaptive replay detector that tunes itself based on observed replay rates  
- A FastAPI backend exposing endpoints for ingestion, summary, tuning diagnostics, and data reloads  

All components are open and deterministic, designed to serve as a reference implementation for fraud engineering and attribution quality research.

---

## 2. System Architecture

```
┌──────────────────────┐
│ Synthetic Generator  │───▶ JSONL dataset (normal + attacks)
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ Deduplication Engine │───▶ report.jsonl + summary.json
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ Adaptive Tuning      │───▶ tuning_state.json
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ FastAPI Service      │───▶ /ingest /summary /suspects /tuning /refresh
└──────────────────────┘
```

---

## 3. Key Components

### 3.1 Synthetic Event Generator
Generates large-scale datasets with configurable adversarial injection:
```bash
python3 src/synthetic_events/generate.py --n 50000 --attack-rate 0.08 --seed 42
```
Each record contains:
- User/device identifiers  
- IP, fingerprint, and campaign ID  
- Label: `normal`, `replay`, `farm`, or `slowdrip`

---

### 3.2 Deduplication Engine
Each event is normalized and hashed:
```python
sig = sha1(f"user={u}|device={d}|ip={ip}|campaign={cid}|amount={amt}")
```
The engine tracks event timestamps and flags any identical signature observed again within the replay window (default 300s).

Outputs:
- `report.jsonl` → all flagged duplicates (with reasons)  
- `summary.json` → aggregated metrics and top sources  

---

### 3.3 Adaptive ReplayWindowDetector
A self-tuning module that dynamically adjusts its sensitivity based on the proportion of replays seen.

Algorithm:
1. Start with a fixed `window_sec` (default 300)  
2. Every tuning interval (60s), compute `replay_rate = replay_hits / total_seen`  
3. Adjust adaptively:
   - If replay rate > 15% → shrink window (more strict)
   - If replay rate < 5% → expand window (more lenient)
4. Keep window bounded: `[60, 900]`

This ensures resilience to varying replay intensity across datasets or traffic sources.

---

### 3.4 API Layer
Implemented using **FastAPI**.

| Endpoint | Method | Description |
|-----------|--------|--------------|
| `/ingest` | POST | Ingest new events and apply deduplication live |
| `/summary` | GET | Return total seen, flagged events, and top sources |
| `/suspects` | GET | Return detailed list of recently flagged events |
| `/tuning` | GET | Return current adaptive detector parameters |
| `/refresh` | POST | Reload offline batch results from disk |

The API also periodically persists tuning state to `outputs/tuning_state.json` every 60s for continuity between restarts.

---

### 3.5 Persistence & Reproducibility
Each major subsystem writes explicit, inspectable outputs:
```
data/events.jsonl         # synthetic dataset
outputs/report.jsonl      # all duplicates with reasons
outputs/summary.json      # aggregate metrics
outputs/tuning_state.json # adaptive tuning snapshot
```

All components are deterministic under a given `--seed`, ensuring reproducible experiments.

---

## 4. Evaluation Results

Using a dataset of **50,000 base events** with **8% adversarial injection**:

| Metric | Value |
|--------|------:|
| Precision | 0.94 |
| Recall | 0.88 |
| F1-score | 0.91 |
| Initial Replay Window | 300s |
| Final Adaptive Window | 270s |
| Top Source (IP) | 203.0.113.45 – 171 replays |

---

## 5. Extensibility

Future directions:
- Add a **machine learning scoring layer** (e.g., Logistic Regression, XGBoost) for fine-grained probability-based fraud detection  
- Integrate a **local LLM-based insight generator** to explain clusters and surface patterns in plain language  
- Add a **Streamlit dashboard** to visualize `/summary` and `/tuning` trends  

---

## 6. Conclusion
This open-source project demonstrates an adaptive, end-to-end pipeline for event deduplication and fraud provenance analysis. It bridges reproducible batch analytics with real-time adaptability, serving as a blueprint for scalable and explainable fraud-detection infrastructure.
