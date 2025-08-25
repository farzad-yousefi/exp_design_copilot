
-- Crash rate per 1k sessions (guardrail)
WITH s AS (
  SELECT DATE_TRUNC('day', ts) AS d,
         SUM(CASE WHEN event_name='crash' THEN 1 ELSE 0 END) AS crash_events,
         SUM(CASE WHEN event_name IN ('open','action','pair') THEN 1 ELSE 0 END) AS session_count
  FROM read_parquet('data/events.parquet')
  GROUP BY 1
)
SELECT d, 1000.0 * crash_events / NULLIF(session_count,0) AS crash_per_1k
FROM s
ORDER BY d;
