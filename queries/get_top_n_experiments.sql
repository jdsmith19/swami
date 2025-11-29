SELECT
	*
FROM
	result r1
WHERE
	r1.agent_id = {agent_id} AND 
	(
	    r1.id IN (
	        SELECT 
	            distinct(id)
	        FROM 
	        	result r2 
	        WHERE 
	        	r2.agent_id = r1.agent_id AND 
	        	r2.model_name = r1.model_name AND
	        	r2.mean_absolute_error IS NOT NULL
	        ORDER BY 
	        	r2.mean_absolute_error ASC
	        LIMIT {n}
        )
     OR
	    r1.id IN (
	        SELECT 
	            distinct(id)
	        FROM 
	        	result r2 
	        WHERE 
	        	r2.agent_id = r1.agent_id AND 
	        	r2.model_name = r1.model_name AND
	        	r2.test_accuracy IS NOT NULL
	        ORDER BY 
	        	r2.test_accuracy DESC
	        LIMIT {n}
        )
    )	
ORDER BY
	r1.model_name,
    r1.mean_absolute_error ASC,
    r1.test_accuracy DESC;