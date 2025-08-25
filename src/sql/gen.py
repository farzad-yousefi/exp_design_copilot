from __future__ import annotations
import json
from pathlib import Path
from typing import Dict
import typer

def _load(path: str) -> Dict:
    return json.loads(Path(path).read_text())

def assignment_check_sql(schema_path: str) -> str:
    sch = _load(schema_path); tbl = "events"
    return f"""
-- Assignment sanity checks (quote reserved identifier "group")
SELECT "group" AS grp, COUNT(DISTINCT user_id) AS users, COUNT(*) AS events
FROM read_parquet('{sch[tbl]["path"]}')
GROUP BY 1
ORDER BY 2 DESC;
"""

def metric_extract_sql(schema_path: str, primary_metric: str) -> str:
    sch = _load(schema_path); tbl = "events"
    if primary_metric == "activation_rate":
        # DuckDB-safe: use INTERVAL arithmetic and GROUP BY instead of QUALIFY/casts
        return f"""
WITH day0 AS (
  SELECT user_id, MIN(ts) AS first_ts
  FROM read_parquet('{sch[tbl]["path"]}')
  GROUP BY 1
),
joined AS (
  SELECT e.user_id, e.ts, e.event_name, d.first_ts
  FROM read_parquet('{sch[tbl]["path"]}') e
  JOIN day0 d USING(user_id)
  WHERE e.ts <= d.first_ts + INTERVAL 7 DAY
),
per_user AS (
  SELECT
    user_id,
    CASE WHEN SUM(CASE WHEN event_name='pair' THEN 1 ELSE 0 END) > 0 THEN 1 ELSE 0 END AS paired,
    SUM(CASE WHEN event_name='action' THEN 1 ELSE 0 END) AS actions7
  FROM joined
  GROUP BY user_id
),
agg AS (
  SELECT
    SUM(CASE WHEN paired=1 AND actions7>=3 THEN 1 ELSE 0 END) * 1.0 AS activated_users,
    COUNT(*) * 1.0 AS total_users
  FROM per_user
)
SELECT activated_users / NULLIF(total_users, 0) AS activation_rate
FROM agg;
"""
    return "SELECT 1 AS ok;"

def guardrail_sql(schema_path: str) -> str:
    sch = _load(schema_path); tbl = "events"
    return f"""
-- Crash rate per 1k sessions (guardrail)
WITH s AS (
  SELECT DATE_TRUNC('day', ts) AS d,
         SUM(CASE WHEN event_name='crash' THEN 1 ELSE 0 END) AS crash_events,
         SUM(CASE WHEN event_name IN ('open','action','pair') THEN 1 ELSE 0 END) AS session_count
  FROM read_parquet('{sch[tbl]["path"]}')
  GROUP BY 1
)
SELECT d, 1000.0 * crash_events / NULLIF(session_count,0) AS crash_per_1k
FROM s
ORDER BY d;
"""

def main(
    schema: str = typer.Option("data/schema.json", help="Path to schema registry JSON"),
    design: str = typer.Option("artifacts/design.json", help="Design JSON with primary_metric"),
    out: str = typer.Option("artifacts/sql", help="Output directory for SQL files"),
):
    Path(out).mkdir(parents=True, exist_ok=True)
    primary = json.loads(Path(design).read_text())["primary_metric"]
    (Path(out) / "01_assignment_check.sql").write_text(assignment_check_sql(schema))
    (Path(out) / "02_primary_metric.sql").write_text(metric_extract_sql(schema, primary))
    (Path(out) / "03_guardrail_crash_rate.sql").write_text(guardrail_sql(schema))
    typer.echo(f"Wrote SQL to {out}")

if __name__ == "__main__":
    typer.run(main)