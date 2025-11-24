# External Libraries
import os

# Data Sources
from data_sources.DataAggregate import DataAggregate

# Prediction Models
from prediction_models.XGBoost import XGBoost
from prediction_models.LinearRegression import LinearRegression
from prediction_models.RandomForest import RandomForest
from prediction_models.LogisticRegression import LogisticRegression
from prediction_models.KNearest import KNearest

# Models
from models.optimize_model import OptimizeState

# Utilities
from utils.logger import log

# Initialize global variables
this_filename = os.path.basename(__file__).replace(".py","")
log_path = None
log_type = None
db_path = None

def evaluate_model_with_features(da, model_name, feature_list):	
	if(model_name == 'XGBoost'):
		model = XGBoost(da, 'point_differential', feature_list)
	
	elif(model_name == 'LinearRegression'):
		model = LinearRegression(da, 'point_differential', feature_list)
	
	elif(model_name == 'RandomForest'):
		model = RandomForest(da, 'point_differential', feature_list)
	
	elif(model_name == 'LogisticRegression'):
		model = LogisticRegression(da, 'win', feature_list)
	
	elif(model_name == 'KNearest'):
		model = KNearest(da, 'win', feature_list)
	
	return model.model_output

def optimize_trainer(state: OptimizeState) -> OptimizeState:
	"""
	Trains models with specified features and returns performance metrics.
	
	Args:
		model_name: One of ['XGBoost', 'LinearRegression', 'RandomForest', 'LogisticRegression', 'KNearest']
		features: List of feature names to include
	
	Returns:
		{
			'model_name': str,
			'target': str,
			'features_used': list[str],
			'mae': float (regression only),
			'rmse': float (regression only),
			'train_accuracy': float (classification only),
			'test_accuracy': float (classification only),
			'feature_importance': dict (regression only),
			'confidence_intervals': dict (classification only),
			'train_time_seconds': float
		}
	"""
	global log_path, log_type, db_path
	log_path = state["log_path"]
	log_type = state["log_type"]
	db_path = state["db_path"]

	all_train_results = []
	for experiment in state["next_experiments"]:
		result = evaluate_model_with_features(state["data_aggregates"], experiment['model'], experiment['features'])
		result_dict = {
			"experiment_num": state["experiment_count"] + 1,
			"model_name": experiment['model'],
			"result": result,
			"features_used": experiment['features']
		}
		state["historical_results"].append(result_dict)
		all_train_results.append(result_dict)

	state["last_results"] = all_train_results
	return state