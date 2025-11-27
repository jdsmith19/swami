# External Libraries
from typing import List

# Models
from pydantic import BaseModel, Field, field_validator, ValidationError

# Utilities
from utils.features import get_extended_features

class Experiment(BaseModel):
    """Single experiment configuration"""

    # ... means field is required
    experiment_number: int = Field(..., description = "Represents the experiment number from 1 to 10, to help in counting a valid number of experiments has been planned")
    model: str = Field(..., description = "The name of the ML model to use")
    features: list[str] = Field(..., description = "The features to be used")

    @field_validator('model')
    @classmethod
    def validate_model(cls, v):
        if v not in ['XGBoost', 'LinearRegression', 'RandomForest', 'LogisticRegression', 'KNearest']:
            raise ValueError(f"Invalid model: { v }")
        return v
    
    @field_validator('features')
    @classmethod
    def validate_features(cls, v):
        invalid = False
        bad_features = []
        valid = get_extended_features()
        for feat in v:
            if feat not in valid:
                invalid = True
                bad_features.append(feat)
        if invalid:
            raise ValueError(f"You provided features that are not valid. Only list features as defined in the system prompt. The following features are not valid: { bad_features }")
        return v
        
class ExperimentPlan(BaseModel):
    """Experiment plan configuration"""
    experiments: List[Experiment] = Field(..., description = "A list of 10 experiments to run using the Experiment dictionary format")
    commentary: str

    @field_validator('experiments')
    @classmethod
    def validate_experiment_count(cls, v):
        if not len(v) == 10:
            raise ValueError(f"You should be planning 10 experiments, you planned { len(v) }")
        return v
