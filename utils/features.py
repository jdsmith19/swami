base_features = [
    'elo_rating',
    'rpi_rating',
    'days_rest']
    
windowed_features = [
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

def get_extended_features():
    ef = base_features
    for feature in windowed_features:
        for interval in [3, 5, 7]:
            ef.append(f"{ feature }_l{ interval }")
        for location in ['home', 'away']:
            ef.append(f"{ feature }_{ location }")
    return ef