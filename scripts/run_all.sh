#!/usr/bin/env bash
set -euo pipefail

python src/synthetic_events/generate.py --n 20000 --attack-rate 0.1 --seed 7
python src/dedupe/pipeline.py --input data/events.jsonl --window-sec 300 --sig-fields user_id,device_id,ip,campaign_id,amount --out-dir outputs --summary
