from utils.nfl import teams

def load_prompt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def get_team_lookup_string(matchup):
    teams_list = matchup.split(" @ ")
    lookup_string = ""
    for team in teams_list:
        lookup_string += f"{ team }: { teams.odds_api_team_to_pfr_team(team) }\n"
    return lookup_string
