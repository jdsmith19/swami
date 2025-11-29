base_features = [
    'elo_rating',
    'rpi_rating',
    'days_rest']
    
windowed_avg_features = [
    'avg_points_scored',
    'avg_pass_adjusted_yards_per_attempt',
    'avg_rushing_yards_per_attempt',
    'avg_turnovers',
    'avg_penalty_yards',
    'avg_sack_yards_lost',
    'avg_points_allowed',
    'avg_pass_adjusted_yards_per_attempt_allowed',
    'avg_rushing_yards_per_attempt_allowed',
    'avg_turnovers_forced',
    'avg_sack_yards_gained',
    'avg_point_differential'
]

windowed_trend_features = [
    'trend_points_scored',
    'trend_pass_adjusted_yards_per_attempt',
    'trend_rushing_yards_per_attempt',
    'trend_turnovers',
    'trend_penalty_yards',
    'trend_sack_yards_lost',
    'trend_points_allowed',
    'trend_pass_adjusted_yards_per_attempt_allowed',
    'trend_rushing_yards_per_attempt_allowed',
    'trend_turnovers_forced',
    'trend_sack_yards_gained',
    'trend_point_differential',
    'trend_elo_rating'
]

def get_extended_features():
    ef = base_features
    for feature in windowed_avg_features:
        for interval in [3, 5, 7]:
            ef.append(f"{ feature }_l{ interval }")
        for location in ['home', 'away']:
            ef.append(f"{ feature }_{ location }")
    for feature in windowed_trend_features:
        for interval in [5, 7]:
            ef.append(f"{ feature }_l{ interval }")
    return ef

def calculate_feature_effects(data_with, data_without):
        effects = {}
        for model in ['XGBoost', 'LinearRegression', 'RandomForest', 'LogisticRegression', 'KNearest']:
            effects[model] = { 
                'with': { 'total': 0.0, 'count': 0, 'average': 0.0 },
                'without': { 'total': 0.0, 'count': 0, 'average': 0.0 },
            }
        for item in data_with:
            model = item['model_name']
            effects[model]['with']['count'] += 1
            if model in ['XGBoost', 'LinearRegression', 'RandomForest']:
                effects[model]['with']['total'] += float(item['mean_absolute_error'])
            else:
                effects[model]['with']['total'] += float(item['test_accuracy'])
            if effects[model]['with']['count'] > 0:
                effects[model]['with']['average'] = round(effects[model]['with']['total'] / float(effects[model]['with']['count']), 2)

        for item in data_without:
            model = item['model_name']
            effects[model]['without']['count'] += 1
            if model in ['XGBoost', 'LinearRegression', 'RandomForest']:
                effects[model]['without']['total'] += float(item['mean_absolute_error'])
            else:
                effects[model]['without']['total'] += float(item['test_accuracy'])
            effects[model]['without']['average'] = round(effects[model]['without']['total'] / (float(effects[model]['without']['count'])), 2)

        for model in effects:
            effects[model]['with'].pop('total')
            effects[model]['without'].pop('total')        

        return effects