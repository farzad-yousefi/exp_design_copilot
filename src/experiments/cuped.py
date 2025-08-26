from __future__ import annotations
import argparse, pandas as pd, numpy as np

def cuped_adjust(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    theta = np.cov(x, y, bias=True)[0,1] / (np.var(x) + 1e-12)
    return y - theta * (x - x.mean())

def main(csv: str):
    df = pd.read_csv(csv)
    a, b = df[df.group=="A"], df[df.group=="B"]
    ya, yb = a["y"].to_numpy(dtype=float), b["y"].to_numpy(dtype=float)
    xa, xb = a["x_pre"].to_numpy(dtype=float), b["x_pre"].to_numpy(dtype=float)
    na, nb = len(ya), len(yb)

    # --- Naive lift (no adjustment) ---
    diff_naive = float(yb.mean() - ya.mean())
    varA, varB = ya.var(ddof=1), yb.var(ddof=1)
    se_naive = float(np.sqrt(varA/na + varB/nb))
    z = 1.96
    lo_naive, hi_naive = diff_naive - z*se_naive, diff_naive + z*se_naive

    # --- CUPED-adjusted lift ---
    ypa, ypb = cuped_adjust(ya, xa), cuped_adjust(yb, xb)
    diff_cuped = float(ypb.mean() - ypa.mean())
    varA_c, varB_c = ypa.var(ddof=1), ypb.var(ddof=1)
    se_cuped = float(np.sqrt(varA_c/na + varB_c/nb))
    lo_cuped, hi_cuped = diff_cuped - z*se_cuped, diff_cuped + z*se_cuped

    # Variance reduction (info)
    var_naive_sum = varA + varB
    var_cuped_sum = varA_c + varB_c
    red = (1.0 - var_cuped_sum / (var_naive_sum + 1e-12)) * 100.0

    print(f"Naive  lift (B−A): {diff_naive:.4f}  (95% CI: [{lo_naive:.4f}, {hi_naive:.4f}])  SE: {se_naive:.4f}")
    print(f"CUPED  lift (B−A): {diff_cuped:.4f}  (95% CI: [{lo_cuped:.4f}, {hi_cuped:.4f}])  SE: {se_cuped:.4f}")
    print(f"Variance reduction vs naive: {red:.2f}%")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default="data/ab_demo.csv")
    main(p.parse_args().csv)
