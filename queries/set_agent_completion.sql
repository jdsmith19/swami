UPDATE agent_run
SET completed = CURRENT_TIMESTAMP
WHERE agent_id = {agent_id}