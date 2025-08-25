# from future import annotations
import numpy as np, pandas as pd
import typer

app = typer.Typer(help="CUPED-adjusted lift for A/B demo CSV (columns: group,y,x_pre).")

def cuped_adjust(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    theta = np.cov(x, y, bias=True)[0,1] / (np.var(x) + 1e-12)
    return y - theta * (x - x.mean())

@app.command()
def main(csv: str = "data/ab_demo.csv"):
    df = pd.read_csv(csv)
    a = df[df["group"]=="A"]; b = df[df["group"]=="B"]
    y_a = cuped_adjust(a["y"].to_numpy(), a["x_pre"].to_numpy())
    y_b = cuped_adjust(b["y"].to_numpy(), b["x_pre"].to_numpy())
    lift = float(y_b.mean() - y_a.mean())
    print(f"CUPED-adjusted lift (B - A): {lift:.6f}")
    var_naive = float(a["y"].var(ddof=1) + b["y"].var(ddof=1))
    var_cuped = float(y_a.var(ddof=1) + y_b.var(ddof=1))
    print(f"Var (naive): {var_naive:.6f} | Var (CUPED): {var_cuped:.6f} | Reduction: {(1 - var_cuped/var_naive)*100:.2f}%")


if __name__ == "main":
    app()
