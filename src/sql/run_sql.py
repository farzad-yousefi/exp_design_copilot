from __future__ import annotations
import duckdb, pathlib

sql_dir = pathlib.Path("artifacts/sql")
db = duckdb.connect()

def run(file, out_csv):
    q = (sql_dir / file).read_text()
    df = db.execute(q).df()
    print(f"\n--- {file} ---")
    print(df.head())
    (sql_dir / out_csv).write_text(df.to_csv(index=False))

run("01_assignment_check.sql", "assignment_check.csv")
run("02_primary_metric.sql", "activation_rate.csv")
run("03_guardrail_crash_rate.sql", "crash_rate.csv")
print("\nSaved CSVs in artifacts/sql/")
