import numpy as np
import pandas as pd
import random
import time
import sqlite3
import traceback
import requests
from io import StringIO
from utils.logger import log
from langchain.agents import AgentState
import os
from tqdm import tqdm
from utils.nfl import teams
from utils.columns import col_utils

this_filename = os.path.basename(__file__).replace(".py","")

class ProFootballReference:
	def __init__(self, state: AgentState):
		self.state = state

	def get_data(self, seasons):
		# Get a start time so we can log total time to complete
		start_time = time.time()

		# Instantiate the Data Frames
		event_df = pd.DataFrame()
		up_event_df = pd.DataFrame()
		game_data_df = pd.DataFrame()

		# Parent bar for overall progress
		for season in self.state["seasons"]:
			# Child bar for season progress
			pbar = tqdm(teams.all_teams_pfr() , f"Getting team data for { season } season", position=0, leave=True)
			pbar.write(f"\n🏈 Getting team data for { season } season")
			i = 0
			for team in pbar:
				#if i >= 2:
					#break
				# Let's be sure to print the team names nicely				
				pretty_team = teams.pfr_team_to_odds_api_team(team)
				pbar.set_description(f"{ pretty_team }")
				log(self.state["log_path"], f"Getting data for { pretty_team } in { season }", "file", this_filename)
				game_data_url = f'https://www.pro-football-reference.com/teams/{team}/{str(season)}/gamelog/'
				
				# Fetch HTML Once
				response = requests.get(game_data_url)
				html_content = response.text
				# Loop through tables
				for table_id in [
					'table_pfr_team-year_game-logs_team-year-regular-season-game-log',
					'table_pfr_team-year_game-logs_team-year-playoffs-game-log'
				]:
					try:
						# Process the table data
						tm_df = pd.read_html(StringIO(html_content), header=1, attrs={'id': table_id})[0]
						# Drop the Rk column
						tm_df = tm_df.drop(columns=['Rk'], axis=1)

						# Rename cols to the ones I like
						tm_df = tm_df.rename(col_utils.col_rename_dict(), axis=1)

						# Historical games don't have a season_week_number_value
						tm_df = tm_df.dropna(subset=['season_week_number'])

						# Add the season
						tm_df['season'] = season

						# Tag whether a game is a playoff game or not
						if(table_id == 'table_pfr_team-year_game-logs_team-year-playoffs-game-log'):
							tm_df['is_playoffs'] = 1
						else:
							tm_df['is_playoffs'] = 0

						# Add the team abbreviation
						tm_df['team'] = team

						# Cast season_week_number to integer
						tm_df['season_week_number'] = tm_df['season_week_number'].astype(int)

						# Set is_neutral and is_home
						tm_df['is_neutral'] = np.where(tm_df['is_home'] == 'N', 1, 0)
						tm_df['is_home'] = np.where(tm_df['is_home'] == '@', 0, 1)

						# Deal with mapping opponent names and specifying home and away teams
						tm_df['opponent_raw'] = tm_df['opponent']
						tm_df['opponent'] = tm_df['opponent'].map(teams.opp_to_pfr_code())
						tm_df['home_team'] = np.where(tm_df['is_home'] == 1, team, tm_df['opponent'])
						tm_df['away_team'] = np.where(tm_df['is_home'] == 1, tm_df['opponent'], team)

						# Create a deterministic event_id value
						tm_df['event_id'] = np.where(
							tm_df['is_neutral'] == 1,
							tm_df['season'].astype(str) + '_' + tm_df['season_week_number'].astype(str) + '_' + np.minimum(tm_df['team'], tm_df['opponent']) + '_' + np.maximum(tm_df['team'], tm_df['opponent']),
							(tm_df['season'].astype(str) + '_' + tm_df['season_week_number'].astype(str) + '_' + tm_df['home_team'] + '_' + tm_df['away_team'])
						)
						
						tm_df['is_complete'] = np.where(tm_df['team_game_number'].isna(), 0, 1)
						tm_df['team_game_number'] = tm_df['team_game_number'].astype('Int64') # Using Int64 to keep null values as such and not error when converting to int
						tm_df['win'] = np.where(tm_df['win'] == 'W', 1, 0)
						tm_df['overtime'] = np.where(tm_df['overtime'] == 'OT', 1, 0)
						event_df = pd.concat([event_df, tm_df[col_utils.event_columns()].copy()], ignore_index=True)
						game_data_df = pd.concat([game_data_df, tm_df[tm_df['is_complete'] == 1][col_utils.game_data_columns()].copy()], ignore_index=True)

						
						# Create the game_data_df from tm_df when the game is in the future
						# game_data_df = pd.concat([game_data_df, tm_df[tm_df['is_complete'] == 1][col_utils.game_data_columns()].copy()], ignore_index=True)
						
					except (ValueError, IndexError):
						#log(self.state['log_path'],f"No playoff data found for { pretty_team } in { season }", self.state['log_type'], this_filename)
						pass

					except Exception as e:
						log(self.state['log_path'],f"Unexpected error for { pretty_team } in {season}: {e}", self.state['log_type'], this_filename)
						log(self.state['log_path'],f"{ traceback.format_exc() }", self.state['log_type'], this_filename)
					
					i += 1
					time.sleep(random.randint(4,5))
				
				# Data Cleanup -- have to drop duplicates because there will be one for each team page				
				event_df = event_df.drop_duplicates(subset=['event_id'], keep='first')
				# Create the game_data_df from tm_df when the game is in the future

		end_time = time.time()
		log(self.state["log_path"], f"Loaded Pro Football Reference data in {end_time - start_time:1f} seconds", self.state["log_type"], this_filename)
	
		return { 'events': event_df, 'game_data': game_data_df, 'upcoming_events': up_event_df }
	
	def load_game_data_from_db(self, is_complete = 1):
		conn=sqlite3.connect('db/historical_data.db')
		query_game_data = f"""
		SELECT
		
			e.event_id,
			e.season,
			e.season_week_number,
			e.date,
			e.home_team,
			e.away_team,
			--e.is_neutral,
			e.is_complete,
			
			-- TEAM A STATS
			team_a.team as team_a,
			team_a.is_home as team_a_is_home,
			team_a.points_scored as team_a_points_scored,
			team_a.win as team_a_win,
			
			--TEAM B STATS
			team_b.team as team_b,
			team_b.is_home as team_b_is_home,
			team_b.points_scored as team_b_points_scored,
			team_b.win as team_b_win
		
		FROM
		
			event e
			join team_result team_a on e.event_id = team_a.event_id AND e.home_team = team_a.team
			join team_result team_b on e.event_id = team_b.event_id AND e.away_team = team_b.team
		
		WHERE
			e.is_complete = { is_complete }

		ORDER BY
		
			e.season, 
			e.season_week_number
		"""
		game_data = pd.read_sql(query_game_data, conn)
		conn.close()
		return game_data
	
	def get_upcoming_games(self):
		conn=sqlite3.connect('db/historical_data.db')
		query_upcoming = """
		SELECT
			*
		FROM
			event e
		WHERE
			e.is_complete = 0 and
			season = (select min(season) from event where is_complete = 0) AND
			season_week_number = (select min(season_week_number) from event where is_complete = 0 and season = e.season)
		"""
		upcoming_games = pd.read_sql(query_upcoming, conn)
		conn.close()
		return upcoming_games

	def load_team_performance_from_db(self):
		conn=sqlite3.connect('db/historical_data.db')
		query_team_performance = """
		
		SELECT
			team_result.*,
			e.season,
			e.season_week_number
		FROM
			team_result
			join event e on e.event_id = team_result.event_id
		
		"""

		team_performance = pd.read_sql(query_team_performance, conn)
		conn.close()
		return team_performance
