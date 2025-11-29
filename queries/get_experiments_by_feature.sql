SELECT
    *
FROM
	result
WHERE
	agent_id = {agent_id} and
	features_used like {feature}
ORDER BY
    created desc
LIMIt 25;