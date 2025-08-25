from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
from src.design.brief_to_design import build_design
import json

app = FastAPI(title="Experiment Design Copilot")

class DesignRequest(BaseModel):
    brief: str
    primary_metric: str = "activation_rate"
    baseline: float = 0.25
    mde: float = 0.03
    power: float = 0.80
    alpha: float = 0.05

@app.post("/design")
def design(req: DesignRequest):
    d = build_design(
    brief=req.brief,
    primary_metric=req.primary_metric,
    baseline=req.baseline,
    mde=req.mde,
    power=req.power,
    alpha=req.alpha,
    glossary_path="docs/metric_glossary.json"
    )
    return json.loads(json.dumps(d, default=lambda o: o.dict))
