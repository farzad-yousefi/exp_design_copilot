# from future import annotations
import typer
from .brief_to_design import build_design, save_design

app = typer.Typer(help="Experiment Design Copilot (CLI)")

@app.command()
def design(
    brief: str = typer.Option(..., help="Short description, e.g., 'show new onboarding tooltip'"),
    primary_metric: str = typer.Option("activation_rate"),
    baseline: float = typer.Option(0.25),
    mde: float = typer.Option(0.03),
    power: float = typer.Option(0.80),
    alpha: float = typer.Option(0.05),
    glossary: str = typer.Option("docs/metric_glossary.json"),
    out: str = typer.Option("artifacts/design.json")
    ):
    d = build_design(brief, primary_metric, baseline, mde, power, alpha, glossary)
    save_design(d, out)
    typer.echo(f"Wrote {out}")

if __name__ == "main":
    app()

@app.command()
def powercurve(
    baseline: float = typer.Option(0.25),
    mde_pp: str = typer.Option("1,2,3,4,5,6", help="MDE in percentage points"),
    power: float = typer.Option(0.80),
    alpha: float = typer.Option(0.05),
):
    """Print sample size per group across a range of MDEs (percentage points)."""
    from .power import sample_size_proportions
    mdelist = [int(x.strip()) for x in mde_pp.split(",") if x.strip()]
    print("MDE(pp), n_per_group, total_n")
    for pp in mdelist:
        m = sample_size_proportions(baseline=baseline, mde=pp/100.0, power=power, alpha=alpha)
        print(f"{pp}, {m.n_per_group}, {m.total_n}")
