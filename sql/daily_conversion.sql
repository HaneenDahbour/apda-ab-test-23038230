-- Daily conversion summary for each experiment arm.

SELECT
    CAST(timestamp AS DATE) AS experiment_date,
    "group",
    COUNT(*) AS users,
    CAST(SUM(converted) AS BIGINT) AS conversions,
    AVG(converted) AS conversion_rate
FROM clean_ab
GROUP BY
    experiment_date,
    "group"
ORDER BY
    experiment_date,
    "group";
