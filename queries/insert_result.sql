INSERT INTO
    {table} (
        model_name, 
        target, 
        train_time_in_seconds, 
        features_used, 
        mean_absolute_error, 
        root_mean_squared_error,
        train_accuracy,
        test_accuracy,
        feature_importance,
        feature_coefficients,
        confidence_intervals,
        agent_id
    )
VALUES
    ({values})