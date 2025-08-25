
WITH day0 AS (
  SELECT user_id, MIN(ts) AS first_ts
  FROM read_parquet('data/events.parquet')
  GROUP BY 1
),
joined AS (
  SELECT e.user_id, e.ts, e.event_name, d.first_ts
  FROM read_parquet('data/events.parquet') e
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
