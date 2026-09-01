-- Group-level summary for the cleaned A/B experiment.
-- One result row is produced for each experiment arm.

SELECT
    "group",
    COUNT(*) AS users,
    CAST(SUM(converted) AS BIGINT) AS conversions,
    AVG(converted) AS conversion_rate
FROM clean_ab
GROUP BY "group"
ORDER BY "group";
