# External Libraries
import sqlite3
from typing import Annotated
import json

# LangGraph / LangChain
from langchain.tools import tool

# Utilities
from utils.features import calculate_feature_effects

class train_result_tools:
    def __init__(self, agent_id, db_path):
        self.agent_id = agent_id
        self.db_path = db_path
    
    def dict_factory(self, cursor, row):
        fields = [column[0] for column in cursor.description]
        return {key: value for key, value in zip(fields, row)}

    def query_database(self, query, db_path):
        conn = sqlite3.connect(db_path)
        conn.row_factory = self.dict_factory
        cur = conn.cursor()
        result = cur.execute(query)
        rows = result.fetchall()
        conn.close()
        if not rows:
            rows = "No experiments run yet"
        return rows

    def calculate_feature_effects(data_with, data_without):
        effects = {}
        for model in ['XGBoost', 'LinearRegression', 'RandomForest', 'LogisticRegression', 'KNearest']:
            effects[model] = { 
                'with': { 'total': 0.0, 'count': 0, 'average': 0.0 },
                'without': { 'total': 0.0, 'count': 0, 'average': 0.0 },
            }
        for item in data_with:
            effects[item['model_name']]['with']['count'] += 1
            if item['model_name'] in ['XGBoost', 'LinearRegression', 'RandomForest']:
                effects[model]['with']['total'] += item['mean_absolute_error']
            else:
                effects[model]['with']['total'] += item['test_accuracy']
            effects[item['model_name']]['with']['average'] = round(effects[item['model_name']]['with']['total'] / effects[item['model_name']]['with']['count'], 2)

        for item in data_without:
            effects[item['model_name']]['without']['count'] += 1
            if item['model_name'] in ['XGBoost', 'LinearRegression', 'RandomForest']:
                effects[model]['without']['total'] += item['mean_absolute_error']
            else:
                effects[model['without']]['total'] += item['test_accuracy']
            effects[item['model_name']]['without']['average'] = round(effects[item['model_name']]['without']['total'] / effects[item['model_name']]['without']['count'], 2)

        for model in effects:
            effects[model]['with'].pop('total')
            effects[model]['without'].pop('total')
        print(effects)
        return effects

    def get_best_experiments(self, n: int):
        print(f"Agent is requesting { n } best experiments.")
        with open("queries/get_top_n_experiments.sql") as f:
            query = f.read()
        query = query.format(
            agent_id = f"\"{ self.agent_id }\"",
            n = n
        )
        result = self.query_database(self, query, self.db_path)
        return result

    @tool
    def get_recent_experiments(self, n: int):
        """Returns the last "n" experiment results."""
        print(f"Agent is requesting last { n } experiments.")
        with open("queries/get_n_recent_experiments.sql") as f:
            query = f.read()
        query = query.format(
            agent_id = f"\"{ self.agent_id }\"",
            n = n
        )
        result = self.query_database(query, self.db_path)
        return result

    @tool
    def get_experiments_with_feature(self, feature: str):
        """Returns last 25 experiments run that DO contain a specific feature."""
        print(f"Agent is requesting experiments with feature: { feature }")
        with open("queries/get_experiments_by_feature.sql") as f:
            query = f.read()
        query = query.format(
            agent_id = f"\"{ self.agent_id }\"",
            feature = f"\"%{ feature }%\""
        )
        result = self.query_database(query, self.db_path)
        return result

    @tool
    def get_experiments_without_feature(self, feature: str):
        """Returns last 25 experiments run that DO NOT contain a specific feature."""
        print(f"Agent is requesting experiments without feature: { feature }")
        with open("queries/get_experiments_without_feature.sql") as f:
            query = f.read()
        query = query.format(
            agent_id = f"\"{ self.agent_id }\"",
            feature = f"\"%{ feature }%\""
        )
        result = self.query_database(query, self.db_path)
        return result

    @tool 
    def get_feature_usage(self):
        """Returns a dictionary of all features and how many experiments have contained them."""
        print(f"Agent is requesting feature usage data")
        with open("queries/get_feature_usage.sql") as f:
            query = f.read()
        query = query.format(
            agent_id = f"\"{ self.agent_id }\""
        )
        result = self.query_database(query, self.db_path)

        usage = {}
        for feature in self.get_extended_features():
            usage[feature] = {
                'XGBoost': 0,
                'LinearRegression': 0,
                'RandomForest': 0,
                'LogisticRegression': 0,
                'KNearest': 0
            }
            
        result = self.query_database(query, self.db_path)
        
        if isinstance(result, str):
            return result
        
        for item in result:
            for feature in json.loads(item['features_used']):
                usage[feature][item['model_name']] += 1
        
        return usage

    @tool
    def summarize_feature_effects(self, feature):
        """
            Returns a dictionary of the effects of including or not including a specific feature.
            Provides the average score for each model type.
        """
        print(f"Agent is requesting feature effect summary for { feature }")
        with open("queries/get_experiments_by_feature.sql") as f:
            query_with = f.read()
        query_with = query_with.format(
            agent_id = f"\"{ self.agent_id }\"",
            feature = f"\"%{ feature }%\""
        )
        with open("queries/get_experiments_without_feature.sql") as f:
            query_without = f.read()
        query_without = query_without.format(
            agent_id = f"\"{ self.agent_id }\"",
            feature = f"\"%{ feature }%\""
        )

        result_with = self.query_database(query_with, self.db_path)
        result_without = self.query_database(query_without, self.db_path)
        if isinstance(result_with, str):
            print("No experiments found")
            return f"No experiments found using { feature }"

        effects = self.calculate_feature_effects(result_with, result_without)
        print(self.json.dumps(effects, indent=2))
        return effects