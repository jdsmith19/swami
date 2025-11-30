from utils.features import calculate_feature_effects, get_extended_features
import sqlite3
import json

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def query_database(query, db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    result = cur.execute(query)
    rows = result.fetchall()
    conn.close()
    if not rows:
        rows = "No experiments run yet"
    return rows

def get_latest_agent_id(db_path):
    query = "SELECT agent_id FROM result ORDER BY created desc LIMIT 1"
    agent_id = query_database(query, db_path)
    return agent_id[0]['agent_id']
    
def get_feature_usage(agent_id, db_path):
    """Returns a dictionary of all features and how many experiments have contained them."""
    print(f"Agent is requesting feature usage data")
    with open("queries/get_feature_usage.sql") as f:
        query = f.read()
    query = query.format(
        agent_id = f"\"{ agent_id }\""
    )
    result = query_database(query, db_path)

    usage = {}
    for feature in get_extended_features():
        usage[feature] = {
            'XGBoost': 0,
            'LinearRegression': 0,
            'RandomForest': 0,
            'LogisticRegression': 0,
            'KNearest': 0
        }
        
    result = query_database(query, db_path)
    
    if isinstance(result, str):
        return result
    
    for item in result:
        for feature in json.loads(item['features_used']):
            usage[feature][item['model_name']] += 1
    
    return usage

db_path = 'db/historical_data.db'
agent_id = get_latest_agent_id(db_path)
usage = get_feature_usage(agent_id, db_path)
print(json.dumps(usage, indent=2))