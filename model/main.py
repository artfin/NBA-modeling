from __future__ import print_function
import json
import numpy as np
from pprint import pprint
from dateutil.parser import parse

OFFENSIVE_TABLE = ['pts', 'orb', 'ast']
DEFENSIVE_TABLE_RIVAL_TEAM = ['pts']
DEFENSIVE_TABLE_CURRENT_TEAM = ['drb', 'blk']

def matrix_factorization(R, K = 1, steps = 5000, alpha = 0.0002, beta = 0.02):
	P = np.random.rand(len(R), 1)
	Q = np.random.rand(len(R[0]), 1).T

	for step in xrange(steps):
		for i in xrange(len(R)):
			for j in xrange(len(R[i])):
				if R[i][j] > 0:
					eij = R[i][j] - np.dot(P[i,:], Q[:,j])
					for k in xrange(K):
						P[i][k] = P[i][k] + alpha * (2 * eij * Q[k][j] - beta * P[i][k])
						Q[k][j] = Q[k][j] + alpha * (2 * eij * P[i][k] - beta * Q[k][j])
	
	return P, Q

def parse_date(date):
	date = parse('2016 ' + date)
	return date.date()

def show_game(game):
	print('{0} | {1} ({2}) -- {3} ({4}): {5} : {6}'.format(parse_date(game["date"]), game["team1"].upper(), game["stats1"]["location"], 
		game["team2"].upper(), game["stats2"]["location"], game["stats1"]["pts"], game["stats2"]["pts"]))

def load_team_data(team):
	path = '../crawler/data/' + team + '.json'
	with open(path, mode = 'r') as inputfile:
		return json.load(inputfile)

def get_team_statistics(game, team):
	key = None
	if team.lower() == game['team1']: key = 'stats1'
	if team.lower() == game['team2']: key = 'stats2'
	
	if key == None:
		print("Given team hasn't played in game.")
		return None
	return game.get(key)

def get_team_offensive_stats(game, team):
	team_statistics = get_team_statistics(game, team)

	offensive_stats = []
	for element in OFFENSIVE_TABLE:
		offensive_stats.append(team_statistics.get(element))
	return offensive_stats

def get_team_defensive_stats(game, team):
	teams = [game['team1'], game['team2']]
	rival_team = teams[1] if team.lower() == teams[0] else teams[0]

	team_statistics = get_team_statistics(game, team)
	rival_statistics = get_team_statistics(game, rival_team)

	defensive_stats = []
	for element in DEFENSIVE_TABLE_RIVAL_TEAM:
		defensive_stats.append(rival_statistics.get(element))
	for element in DEFENSIVE_TABLE_CURRENT_TEAM:
		defensive_stats.append(team_statistics.get(element))
	return defensive_stats

def create_offensive_stats_table(games, team):
	offensive_stats = []
	for game in games:
		offensive_stats.append(get_team_offensive_stats(game, team))
	return np.array(offensive_stats)

def get_game_location(game, team):
	team_statistics = get_team_statistics(game, team)
	return team_statistics["location"]

def filter_games(games, team):
	home_games = []
	road_games = []
	for game in games:
		location = get_game_location(game, team)
		if location == 'home':
			home_games.append(game)
		if location == 'road':
			road_games.append(game)
	return {'home_games' : home_games, 'road_games' : road_games}

def calculate_offensive_vector(games, team):
	offensive_stats = create_offensive_stats_table(last_games, 'ATL')
	print(offensive_stats)
	nP, nQ = matrix_factorization(offensive_stats)
	return nP

data = load_team_data('ATL')

res = filter_games(data, team = 'ATL')
home_games, road_games = res["home_games"], res["road_games"]

last_games = home_games[-5:]
for game in last_games:
	show_game(game)

offensive_vector = calculate_offensive_vector(last_games, 'ATL')
print(offensive_vector)

