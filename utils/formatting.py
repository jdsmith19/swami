class formatting:
    def format_best_results(best_results, prediction_models):
        """Format all best results for context summary"""
        
        # Initialize a list of strings that we will join later
        lines = []
        lines.append("BEST RESULTS FOUND SO FAR")
        
        # Loop through the results, key is the model name
        for result in best_results:
            
            # Need to know the model type is to log the right data
            for model in prediction_models:
                if model["name"] == result["model_name"]:
                    model_type = model["type"]
            
            # Pretty separator for each model
            lines.append(f"{'='*80}")
            lines.append(result["model_name"])
            lines.append(f"{'='*80}")

            # Print the best results
            if model_type == "regressor":
                lines.append(f"Mean Absolute Error: { result["mean_absolute_error"]}")
                lines.append(f"Root Mean Squared Error: { result["root_mean_squared_error"]}")
                if result.get("feature_importance") is not None:
                    lines.append(f"Feature Importance:")
                    for fi in result["feature_importance"]:
                        lines.append(f"\t{ fi }: { result["feature_importance"][fi] }")
                elif result.get("feature_coefficients") is not None:
                    lines.append(f"Feature Coefficients:")
                    for fi in result["feature_coefficients"]:
                        lines.append(f"\t{ fi }: { result["feature_coefficients"][fi] }")
            if model_type == "classifier":
                lines.append(f"Test Accuracy: { result["test_accuracy"]}")
                lines.append(f"Train Accuracy: { result["train_accuracy"]}")
                lines.append("Test Accuracy by Confidence Interval: ")
                for ci in result["confidence_intervals"]:
                    lines.append(f"\t{ ci }")
            lines.append(f"Features used: { ', '.join(result["features_used"]) }\n")

        formatted = "\n".join(lines)

        return formatted