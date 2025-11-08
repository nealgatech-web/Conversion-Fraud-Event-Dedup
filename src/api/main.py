from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..dedupe.hasher import fuzzy_signature
from ..dedupe.rules import ReplayWindowDetector, ClusterAttribution

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

detector = ReplayWindowDetector(window_sec=300)
attrib = ClusterAttribution()
flagged: List[Dict] = []
seen_total = 0

@app.post("/ingest")
def ingest(events: List[Event]):
    global seen_total
    res = []
    for e in events:
        d = e.model_dump()
        sig = fuzzy_signature(d)
        hit, reason = detector.observe(sig, d.get("ts", 0.0))
        attrib.add(d.get("ip",""), d.get("fingerprint",""))
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
