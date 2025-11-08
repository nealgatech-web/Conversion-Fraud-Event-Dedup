import argparse, json, os
from typing import List, Dict
from .hasher import fuzzy_signature
from .rules import ReplayWindowDetector, ClusterAttribution

def load_events(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--window-sec", type=int, default=300)
    ap.add_argument("--sig-fields", type=str, default="user_id,device_id,ip,campaign_id,amount")
    ap.add_argument("--out-dir", default="outputs")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    events = load_events(args.input)
    detector = ReplayWindowDetector(window_sec=args.window_sec)
    attrib = ClusterAttribution()

    flagged = []
    total = 0
    tp = fp = fn = tn = 0

    fields = [s.strip() for s in args.sig_fields.split(",") if s.strip()]

    with open(os.path.join(args.out_dir, "report.jsonl"), "w", encoding="utf-8") as out:
        for e in events:
            total += 1
            sig = fuzzy_signature(e, keys=fields)
            hit, reason = detector.observe(sig, e.get("ts", 0.0))
            attrib.add(e.get("ip",""), e.get("fingerprint",""))
            if hit:
                flagged.append({"id": e["id"], "reason": reason, "label": e.get("label")})
                out.write(json.dumps(flagged[-1]) + "\n")

                if e.get("label") in {"replay","farm","slowdrip"}:
                    tp += 1
                else:
                    fp += 1
            else:
                if e.get("label") in {"replay","farm","slowdrip"}:
                    fn += 1
                else:
                    tn += 1

    if args.summary:
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2*precision*recall)/(precision+recall) if (precision+recall) else 0.0
        summary = {
            "total_events": total,
            "flagged": len(flagged),
            "precision": round(precision,4),
            "recall": round(recall,4),
            "f1": round(f1,4),
            "top_sources": attrib.top_sources(10)
        }
        with open(os.path.join(args.out_dir, "summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
