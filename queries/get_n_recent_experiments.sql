SELECT
    *
FROM
    result
WHERE
    agent_id = {agent_id}
ORDER BY
    created desc
LIMIT {n}