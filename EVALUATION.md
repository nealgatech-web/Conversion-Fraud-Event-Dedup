
# EVALUATION.md

We evaluate deduplication with precision/recall against synthetic labels.
- TP: flagged and label ∈ {replay,farm,slowdrip}
- FP: flagged but label == normal
- TN: not flagged and normal
- FN: not flagged but label ∈ {replay,farm,slowdrip}

The pipeline writes `outputs/summary.json` with:
- precision, recall, f1
- duplicate ratio
- top sources by IP / fingerprint
