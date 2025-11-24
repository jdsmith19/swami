from utils.nfl import teams

def create_matchups(upcoming_games):
    matchups = {}
    for idx, game in upcoming_games.iterrows():
        matchup_name = f"{ teams.pfr_team_to_odds_api_team(game['away_team']) } @ { teams.pfr_team_to_odds_api_team(game['home_team']) }"
        matchups[matchup_name] = {}
    return matchups

def get_predictions_by_matchup(predictions, matchups):
    for prediction in predictions:
        for result in prediction['results']:
            matchup_name = f"{ result['away_team'] } @ { result['home_team'] }"
            matchups[matchup_name].setdefault("predictions", {})[prediction["model_name"]] = result
    return matchups

def get_unique_teams(upcoming_games):
    unique_teams = []
    for idx, game in upcoming_games.iterrows():
        home_team = teams.pfr_team_to_odds_api_team(game['home_team'])
        away_team = teams.pfr_team_to_odds_api_team(game['away_team'])
        if home_team not in unique_teams:
            unique_teams.append(home_team)
        if away_team not in unique_teams:
            unique_teams.append(away_team)
    return unique_teams

def get_injury_reports_by_matchup(injury_reports, matchups):
    for injury_report in injury_reports:
        for matchup in matchups:
            if injury_report["team"] in matchup:
                matchups[matchup].setdefault("injury_reports", []).append(injury_report)
    return matchups

def get_unique_games(matchups):
    games = []
    for matchup in matchups:
        games.append(matchup)
    return games