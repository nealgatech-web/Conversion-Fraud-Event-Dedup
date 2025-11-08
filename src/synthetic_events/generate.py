import argparse, os, json, random, time, hashlib

UA = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X)",
    "Mozilla/5.0 (Linux; Android 13)"
]

def rand_ip():
    base = random.choice([(203,0,113), (198,51,100)])
    return f"{base[0]}.{base[1]}.{base[2]}.{random.randint(1,254)}"

def fp(user_id, device_id, ua):
    s = f"{user_id}|{device_id}|{ua}".lower()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

def gen_normal(campaign_id):
    user_id = f"u_{random.randint(1,8000)}"
    device_id = f"d_{random.randint(1,10000)}"
    ua = random.choice(UA)
    return {
        "user_id": user_id,
        "device_id": device_id,
        "ip": rand_ip(),
        "user_agent": ua,
        "campaign_id": campaign_id,
        "amount": round(random.choice([9.99, 19.99, 29.99, 49.00, 99.00]) * (1.0 + random.uniform(-0.05, 0.05)), 2),
        "fingerprint": fp(user_id, device_id, ua),
        "label": "normal"
    }

def gen_farm(campaign_id):
    farm_ip = rand_ip()
    ua = random.choice(UA)
    user_id = f"u_{random.randint(8001,12000)}"
    device_id = f"d_{random.randint(10001,16000)}"
    return {
        "user_id": user_id,
        "device_id": device_id,
        "ip": farm_ip,
        "user_agent": ua,
        "campaign_id": campaign_id,
        "amount": round(random.choice([9.99, 19.99, 29.99]) * (1.0 + random.uniform(-0.05, 0.05)), 2),
        "fingerprint": fp(user_id, device_id, ua),
        "label": "farm"
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--attack-rate", type=float, default=0.08)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="data/events.jsonl")
    args = ap.parse_args()
    random.seed(args.seed)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    start_ts = time.time()
    events = []
    for i in range(args.n):
        ts = start_ts + i
        campaign_id = f"cmp_{random.randint(1,50)}"
        e = gen_normal(campaign_id)

        # inject adversaries
        if random.random() < args.attack_rate:
            mode = random.choice(["replay", "farm", "slowdrip"])
            if mode == "replay":
                e["label"] = "replay"
            elif mode == "farm":
                e = gen_farm(campaign_id)
            else:
                e["label"] = "slowdrip"

        e["id"] = f"evt_{i:08d}"
        e["ts"] = ts
        events.append(e)

        # amplification for replay: add duplicates
        if e["label"] == "replay":
            copies = random.randint(1,3)
            for c in range(copies):
                dup = dict(e)
                dup["id"] = f"{e['id']}_r{c+1}"
                dup["ts"] = ts + random.randint(1,120)
                events.append(dup)

    with open(args.out, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
    print(f"Wrote {len(events)} events to {args.out}")

if __name__ == "__main__":
    main()
