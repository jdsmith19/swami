import pandas as pd
import sqlite3

class PredictionModel:
	def __init__(self, data_aggregate, target, feature_columns, prediction_set):
		self.target = target
		self.feature_columns = feature_columns
		self.team_specific_feature_columns = self.__get_team_specific_feature_columns(self.feature_columns)
		self.training_features = self.__prepare_features(data_aggregate, prediction=False)
		self.prediction_features = self.__prepare_features(prediction_set, prediction=True)
		self.prediction_df = pd.DataFrame

	def __prepare_features(self, aggregate_data, prediction=False):
		feature_columns = self.team_specific_feature_columns
		if(prediction):
			feature_columns.remove("team_a_" + self.target)
		features = aggregate_data[feature_columns].copy()
		features = features.dropna()
		return features
	
	def __get_team_specific_feature_columns(self, prediction_columns=False):
		team_specific_feature_columns = []
		team_specific_feature_columns.append("team_a_" + self.target)
		for col in self.feature_columns:
			if "_away" not in col:
				team_specific_feature_columns.append("team_a_" + col)
			if "_home" not in col:
				team_specific_feature_columns.append("team_b_" + col)
		return team_specific_feature_columns
	
	def add_predictions_to_database(self):
		conn = sqlite3.connect("db/historical_data.db")
		self.prediction_df.to_sql('predictons', conn, if_exists = "append", index=False)
		conn.close()

	def sanitize_features(self, df, model):
		"""
		Ensure columns are unique and log any duplicates the moment they appear.
		Keeps the first occurrence of each column.
		"""
		cols = pd.Index(df.columns)
		dup_mask = cols.duplicated()

		if not dup_mask.any():
			return df
		
		dupes = cols[dup_mask].tolist()

		# 🔎 Log everything you'd ever want to inspect later
		print("⚠️ Duplicate feature columns detected")
		print(f"Model: { model }")
		print(f"Total columns: { df.shape[1] }")
		print(f"Duplicate columns: { dupes }")

		# Canonical fix: keep first occurrence of each name
		df = df.loc[:, ~dup_mask].copy()

		return df