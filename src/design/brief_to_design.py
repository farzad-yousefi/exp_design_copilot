# from future import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from .power import sample_size_proportions, PowerResult

@dataclass
class Metric:
    name: str
    role: str # "primary" | "guardrail"
    definition: str
    sql_snippet: str

@dataclass
class Design:
    test_name: str
    hypothesis: str
    assignment: str
    primary_metric: str
    guardrails: list
    sample_size: PowerResult
    citations: dict

def build_design(brief: str, primary_metric: str, baseline: float, mde: float, power: float, alpha: float, glossary_path: str) -> Design:
    glossary = json.loads(Path(glossary_path).read_text())
    if primary_metric not in glossary:
        raise ValueError(f"Metric '{primary_metric}' not found in glossary.")
    m = glossary[primary_metric]
    # choose some default guardrails present in glossary (if any)
    guardrails = [k for k in glossary.keys() if k != primary_metric][:2]
    pr = sample_size_proportions(baseline=baseline, mde=mde, power=power, alpha=alpha)
    hypo = f"If we {brief.lower()}, then the {primary_metric} will increase by ~{mde:.2%} (from {baseline:.0%} to {(baseline+mde):.0%})."
    return Design(
        test_name=brief[:60],
        hypothesis=hypo,
        assignment="Randomized 50/50 at user level; stratify by platform if possible.",
        primary_metric=primary_metric,
        guardrails=guardrails,
        sample_size=pr,
        citations={primary_metric: m.get("definition","")}
    )

def save_design(design: Design, out_path: str):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(asdict(design), indent=2))
