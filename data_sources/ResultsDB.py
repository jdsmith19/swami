import json
import sqlite3
from datetime import datetime

class ResultsDB:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def save_best_result(self, best, features_used):
        model_name = best["model_name"]

        set_statements = ""
        set_statements += f"target = {self.sql_string(best['target'])},\n"
        set_statements += f"\ttrain_time_in_seconds = {self.sql_value(best['train_time_in_seconds'])},\n"
        set_statements += f"\tfeatures_used = {self.sql_json(features_used)},\n"
        set_statements += f"\tmean_absolute_error = {self.sql_value(best.get('mean_absolute_error'))},\n"
        set_statements += f"\troot_mean_squared_error = {self.sql_value(best.get('root_mean_squared_error'))},\n"
        set_statements += f"\ttrain_accuracy = {self.sql_value(best.get('train_accuracy'))},\n"
        set_statements += f"\ttest_accuracy = {self.sql_value(best.get('test_accuracy'))},\n"
        set_statements += f"\tfeature_importance = {self.sql_json(best.get('feature_importance'))},\n"
        set_statements += f"\tfeature_coefficients = {self.sql_json(best.get('feature_coefficients'))},\n"
        set_statements += f"\tconfidence_intervals = {self.sql_json(best.get('confidence_intervals'))},\n"
        set_statements += f"\tagent_id = { self.sql_string(best["agent_id"]) },\n"
        set_statements += f"\tlast_updated = CURRENT_TIMESTAMP\n"

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        with open('queries/update_best_result.sql', 'r') as f:
            template = f.read()
            query = template.format(
                set_statements = set_statements,
                model_name = model_name
            )

        cur.execute(query)
        conn.commit()
        conn.close()
    
    def insert_best_results_from_json(self):
        with open("results/feature_optimization_results.json", "r") as f:
            best_results = json.load(f)['best_results']
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        for result in best_results:    
            values = f"\t{ self.sql_string(result['model_name']) }, { self.sql_string(result['target']) }, { self.sql_value(result['train_time_in_seconds']) }, "
            values += f"{ self.sql_json(result.get('features_used')) }, { self.sql_value(result.get('mean_absolute_error')) }, "
            values += f"{ self.sql_value(result.get('root_mean_squared_error')) }, { self.sql_value(result.get('train_accuracy')) }, "
            values += f"{ self.sql_value(result.get('test_accuracy')) }, "
            values += f"{ self.sql_json(result.get('feature_importance')) }, "
            values += f"{ self.sql_json(result.get('feature_coefficients')) }, "
            values += f"{ self.sql_json(result.get('confidence_intervals')) }"
                
            with open("queries/insert_result.sql") as f:
                template = f.read()
                query = template.format(
                    table = "best_result",
                    values = values
                )   
            
            cur.execute(query)
            conn.commit()
        
        conn.close()

    def sql_value(self, val):
        """Convert Python value to SQL value"""
        if val is None or val == "NULL":
            return "NULL"
        return val
    
    def sql_string(self, val):
        """Convert Python value to SQL string or NULL"""
        if val is None:
            return "NULL"
        # Escape single quotes in strings
        return f"'{ str(val).replace("'", "''") }'"
    
    def sql_json(self, val):
        """Convert Python value to SQL JSON string or NULL"""
        if val is None:
            return "NULL"
        json_str = json.dumps(val).replace("'", "''")
        return f"'{ json_str }'"

    def load_best_results(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        query = "SELECT * FROM best_result"
        
        cur.execute(query)

        rows = cur.fetchall()
        conn.close()

        best_results = []
        for row in rows:
            result = dict(row)

             # Convert numeric fields back to numbers
            if result.get('train_time_in_seconds') is not None:
                result['train_time_in_seconds'] = float(result['train_time_in_seconds'])
            if result.get('mean_absolute_error') is not None:
                result['mean_absolute_error'] = float(result['mean_absolute_error'])
            if result.get('root_mean_squared_error') is not None:
                result['root_mean_squared_error'] = float(result['root_mean_squared_error'])
            if result.get('train_accuracy') is not None:
                result['train_accuracy'] = float(result['train_accuracy'])
            if result.get('test_accuracy') is not None:
                result['test_accuracy'] = float(result['test_accuracy'])
            
            for json_field in ['features_used', 'feature_importance', 'feature_coefficients', 'confidence_intervals']:
                if result.get(json_field):
                    result[json_field] = json.loads(result[json_field])
            
            best_results.append(result)
        
        return best_results

    def save_result(self, result, features_used):

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        values = f"\t{ self.sql_string(result['model_name']) }, { self.sql_string(result['target']) }, { self.sql_value(result['train_time_in_seconds']) }, "
        values += f"{ self.sql_json(features_used) }, { self.sql_value(result.get('mean_absolute_error')) }, "
        values += f"{ self.sql_value(result.get('root_mean_squared_error')) }, { self.sql_value(result.get('train_accuracy')) }, "
        values += f"{ self.sql_value(result.get('test_accuracy')) }, "
        values += f"{ self.sql_json(result.get('feature_importance')) }, "
        values += f"{ self.sql_json(result.get('feature_coefficients')) }, "
        values += f"{ self.sql_json(result.get('confidence_intervals')) }, "
        values += f"{ self.sql_string(result['agent_id']) }"
            
        with open("queries/insert_result.sql") as f:
            template = f.read()
            query = template.format(
                table = "result",
                values = values
            )   
        cur.execute(query)
        conn.commit()
        
        conn.close()
    
    def set_agent_completion(self, agent_id):
        with open("queries/set_agent_completion.sql") as f:
            template = f.read()
            query = template.format(
                agent_id = self.sql_string(agent_id)
            )
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()        
        conn.close()
