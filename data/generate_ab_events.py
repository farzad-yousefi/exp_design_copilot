# from future import annotations
import numpy as np, pandas as pd
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--out", type=Path, default=Path("data/events.parquet"))
parser.add_argument("--users", type=int, default=8000)
parser.add_argument("--days", type=int, default=30)
parser.add_argument("--seed", type=int, default=42)
args = parser.parse_args()

rng = np.random.default_rng(args.seed)
users = np.arange(1, args.users+1)
groups = rng.choice(["A","B"], size=len(users), p=[0.5,0.5])
first_seen = pd.Timestamp.today().normalize() - pd.Timedelta(days=args.days)
rows, ab_rows = [], []

for u, g in zip(users, groups):
    # pre-experiment covariate: prior activity score (correlates with outcome)
    x_pre = rng.normal(0.0, 1.0)
    # base activation probability
    p0 = 0.25 + 0.08 * np.tanh(x_pre/2)
    # treatment +3pp on average
    lift = 0.03 if g == "B" else 0.0
    p = np.clip(p0 + lift, 0.01, 0.99)
    activated = rng.random() < p
    # build a few fake events
    day0 = first_seen + pd.Timedelta(days=int(rng.uniform(0, args.days)))
    n_events = rng.integers(1, 6)
for _ in range(n_events):
    ts = day0 + pd.Timedelta(minutes=int(rng.uniform(0,1440)))
    ev = rng.choice(["open","pair","action","action","action","crash"])
    rows.append((u, ts, ev, g, int(ev!="crash"), day0.normalize()))
    ab_rows.append((g, float(activated), float(x_pre)))

    events = pd.DataFrame(rows, columns=["user_id","ts","event_name","group","success","first_seen"])
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    events.to_parquet(args.out, index=False)
    print(f"Wrote events to {args.out} with {len(events)} rows.")

    ab = pd.DataFrame(ab_rows, columns=["group","y","x_pre"])
    ab.to_csv("data/ab_demo.csv", index=False)
print("Wrote A/B demo CSV to data/ab_demo.csv")
