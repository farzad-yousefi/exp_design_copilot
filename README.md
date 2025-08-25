# Experiment Design Copilot (A/B + Guardrails + CUPED + SQL)

**What it does**
- Takes a short brief and returns: hypothesis, success & guardrail metrics (cited to a glossary), sample size/power, and runnable SQL for assignment checks + metric extraction.
- Ships a CUPED-adjusted lift calculator for your simulated A/B.

**Quickstart**
```bash
make setup
python data/generate_ab_events.py --out data/events.parquet
python -m src.design.cli design --brief "Test new onboarding tooltip to improve activation" \
  --primary_metric activation_rate --baseline 0.25 --mde 0.03 --power 0.8 --alpha 0.05 \
  --out artifacts/design.json
python -m src.sql.gen --schema data/schema.json --design artifacts/design.json --out artifacts/sql
python -m src.sql.run_sql
python -m src.design.cli powercurve --baseline 0.25 --mde_pp "1,2,3,4,5,6" > artifacts/powercurve.csv
python tools_make_readout.py
python -m src.experiments.cuped --csv data/ab_demo.csv
make api   # serve http://127.0.0.1:8000  (see /design)
Folders

src/design/ (power calc, design generator, CLI)

src/sql/ (SQL generators)

src/experiments/ (CUPED)

data/ (synthetic generator + demo CSV)

docs/ (metric glossary)

app/ (FastAPI endpoints)
