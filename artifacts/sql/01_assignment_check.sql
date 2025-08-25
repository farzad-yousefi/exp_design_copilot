
-- Assignment sanity checks (quote reserved identifier "group")
SELECT "group" AS grp, COUNT(DISTINCT user_id) AS users, COUNT(*) AS events
FROM read_parquet('data/events.parquet')
GROUP BY 1
ORDER BY 2 DESC;
