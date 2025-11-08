from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..dedupe.hasher import fuzzy_signature
from ..dedupe.rules import ReplayWindowDetector, ClusterAttribution
import os, json

app = FastAPI(title="Event Dedup & Provenance API")

class Event(BaseModel):
    id: str
    ts: float
    user_id: Optional[str] = ""
    device_id: Optional[str] = ""
    ip: Optional[str] = ""
    user_agent: Optional[str] = ""
    campaign_id: Optional[str] = ""
    amount: Optional[float] = 0.0
    fingerprint: Optional[str] = ""
    label: Optional[str] = "unknown"

# Initialize detectors and memory
detector = ReplayWindowDetector(window_sec=300)
attrib = ClusterAttribution()
flagged: List[Dict] = []
seen_total = 0

# === Preload results from batch pipeline if available ===
SUMMARY_PATH = "outputs/summary.json"
REPORT_PATH = "outputs/report.jsonl"

if os.path.exists(SUMMARY_PATH):
    with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
        cached_summary = json.load(f)
    seen_total = cached_summary.get("total_events", 0)
    for ip, count in cached_summary.get("top_sources", {}).get("ip", []):
        attrib.by_ip[ip] = count
    for fp, count in cached_summary.get("top_sources", {}).get("fingerprint", []):
        attrib.by_fp[fp] = count

if os.path.exists(REPORT_PATH):
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                flagged.append(json.loads(line))
            except Exception:
                pass

# === REST Endpoints ===

@app.post("/ingest")
def ingest(events: List[Event]):
    global seen_total
    res = []
    for e in events:
        d = e.model_dump()
        sig = fuzzy_signature(d)
        hit, reason = detector.observe(sig, d.get("ts", 0.0))
        attrib.add(d.get("ip", ""), d.get("fingerprint", ""))
        seen_total += 1
        if hit:
            item = {"id": d["id"], "reason": reason, "label": d.get("label")}
            flagged.append(item)
            res.append(item)
    return {"flagged": res, "ingested": len(events)}

@app.get("/summary")
def summary():
    return {
        "seen_total": seen_total,
        "flagged": len(flagged),
        "top_sources": attrib.top_sources(10)
    }

@app.get("/suspects")
def suspects(n: int = 100):
    return {"suspects": flagged[-n:]}
