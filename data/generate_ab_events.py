from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("data/events.parquet"))
    ap.add_argument("--ab_csv", type=Path, default=Path("data/ab_demo.csv"))
    ap.add_argument("--users", type=int, default=8000)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--baseline", type=float, default=0.25, help="baseline activation prob for average user")
    ap.add_argument("--lift", type=float, default=0.03, help="absolute lift for group B (pp)")
    ap.add_argument("--max_events", type=int, default=5, help="max events per user in the 7d window")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)

    # Cohort window
    end = pd.Timestamp.today().normalize()
    start = end - pd.Timedelta(days=args.days - 1)

    # Users
    U = args.users
    user_ids = np.arange(1, U + 1, dtype=np.int64)
    groups = rng.choice(np.array(["A", "B"]), size=U, p=[0.5, 0.5])

    # Pre-treatment covariate (for CUPED)
    x_pre = rng.normal(0.0, 1.0, size=U)

    # Activation probability
    p0 = args.baseline + 0.08 * np.tanh(x_pre / 2.0)
    lift = np.where(groups == "B", args.lift, 0.0)
    p = np.clip(p0 + lift, 0.01, 0.99)
    y = (rng.random(U) < p).astype(int)  # Bernoulli outcome

    # First-seen day in the window
    first_seen = start + pd.to_timedelta(rng.integers(0, args.days, size=U), unit="D")
    first_seen_date = first_seen.normalize()

    # Event generation (within 7 days of first_seen)
    names = np.array(["open", "pair", "action", "action", "action", "crash"])
    rows = []
    for uid, g, d0 in zip(user_ids, groups, first_seen):
        n = int(rng.integers(1, args.max_events + 1))
        # spread events over first 7 days
        day_offsets = rng.integers(0, 7, size=n)
        minute_offsets = rng.integers(0, 24*60, size=n)
        es = names[rng.integers(0, len(names), size=n)]
        for do, mo, ev in zip(day_offsets, minute_offsets, es):
            ts = d0 + pd.Timedelta(days=int(do)) + pd.Timedelta(minutes=int(mo))
            success = 0 if ev == "crash" else 1
            rows.append((uid, ts, ev, g, success, d0.normalize()))

    events = pd.DataFrame(
        rows, columns=["user_id", "ts", "event_name", "group", "success", "first_seen"]
    ).sort_values("ts", kind="stable")

    # AB table for CUPED
    ab_demo = pd.DataFrame({"group": groups, "y": y.astype(float), "x_pre": x_pre})

    # Ensure dirs, write files
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.ab_csv.parent.mkdir(parents=True, exist_ok=True)
    # pandas needs a parquet engine; if you ever hit an error, install pyarrow (pip install pyarrow)
    events.to_parquet(args.out, index=False)
    ab_demo.to_csv(args.ab_csv, index=False)

    # Summary
    print(f"Wrote events → {args.out.resolve()}")
    print(f"Wrote ab_demo → {args.ab_csv.resolve()}")
    print(f"users           : {U:,}")
    print(f"events rows     : {len(events):,}  (expected between {U:,} and {U*args.max_events:,})")
    print(f"ab_demo rows    : {len(ab_demo):,} (expected exactly {U:,})")
    if not events.empty:
        print(f"event ts span   : {events['ts'].min()} → {events['ts'].max()}")
        print("A/B users       :")
        print(ab_demo.groupby('group').size().to_string())

if __name__ == "__main__":
    main()

