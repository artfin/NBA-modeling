from __future__ import print_function
import json
import numpy as np
from pprint import pprint
from dateutil.parser import parse
from datetime import date, timedelta as td
import os

TEAMS = ['ATL', 'BOS', 'BRK', 'CHI', 'CHO', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL',
		'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']

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

class __game__(object):
	def __init__(self, data):
		self.date = data["date"]
		self.team1 = data["team1"]
		self.team2 = data["team2"]
		self.stats1 = data["stats1"]
		self.stats2 = data["stats2"]

	def show(self):
		"""
		Presents game info in readable format: date | first team (location for first team) -- second team (location for second team)
		: score.
		"""
		print('{0} | {1} ({2}) -- {3} ({4}): {5} : {6}'.format(self.date, self.team1.upper(), self.stats1["location"], 
			self.team2.upper(), self.stats2["location"], self.stats1["pts"], self.stats2["pts"]))

	def show_advanced(self):
		"""
		Presents additional info about game.
		"""
		self.show()
		print('{0} -- PTS: {1}; ORB: {2}; AST: {3}; DRB: {4}; BLK: {5}'.format(self.team1.upper(), self.stats1["pts"], self.stats1["orb"],
			self.stats1["ast"], self.stats1["drb"], self.stats1["blk"]))
		print('{0} -- PTS: {1}; ORB: {2}; AST: {3}; DRB: {4}; BLK: {5}'.format(self.team2.upper(), self.stats2["pts"], self.stats2["orb"],
			self.stats2["ast"], self.stats2["drb"], self.stats2["blk"]))
		print('='*50)

class VectorCalculator(object):

	# stats we include into offensive table
	OFFENSIVE_TABLE = ['pts', 'orb', 'ast']

	# stats we include into defensive table
	DEFENSIVE_TABLE_RIVAL_TEAM = ['pts'] # these correspond to rival team
	DEFENSIVE_TABLE_CURRENT_TEAM = ['drb', 'blk'] # these correspond to current team

	def __init__(self, games, team, depth = 3):
		self.team = team

		if len(games) > depth:
			self.games = games[-depth:]
		else:
			print('Not enough games.')
			return None

		# for game in self.games:
		# 	game.show_advanced()

		offensive_stats = self.create_offensive_stats_table()
		defensive_stats = self.create_defensive_stats_table()
		
		self.offensive_vector = self.calculate_offensive_vector(offensive_stats)
		self.defensive_vector = self.calculate_defensive_vector(defensive_stats)

	@staticmethod
	def get_team_statistics(game, team):
		if team.lower() == game.team1.lower(): attr = 'stats1'
		if team.lower() == game.team2.lower(): attr = 'stats2'
		return getattr(game, attr)

	def get_offensive_stats(self, game):
		team_stat = self.get_team_statistics(game, self.team)

		offensive_stats = []
		for element in self.OFFENSIVE_TABLE:
			offensive_stats.append(team_stat.get(element))
		return offensive_stats

	def get_team_defensive_stats(self, game):
		teams = [getattr(game, 'team1'), getattr(game, 'team2')]
		rival_team = teams[1] if self.team.lower() == teams[0] else teams[0]

		team_statistics = self.get_team_statistics(game, self.team)
		rival_statistics = self.get_team_statistics(game, rival_team)

		defensive_stats = []
		for element in self.DEFENSIVE_TABLE_RIVAL_TEAM:
			defensive_stats.append(rival_statistics.get(element))
		for element in self.DEFENSIVE_TABLE_CURRENT_TEAM:
			defensive_stats.append(team_statistics.get(element))
		return defensive_stats

	def create_offensive_stats_table(self):
		offensive_stats = []
		for game in self.games:
			offensive_stats.append(self.get_offensive_stats(game))
		return np.array(offensive_stats)

	def create_defensive_stats_table(self):
		defensive_stats = []
		for game in self.games:
			defensive_stats.append(self.get_team_defensive_stats(game))
		return np.array(defensive_stats)

	def calculate_offensive_vector(self, offensive_stats):
		nP, nQ = matrix_factorization(offensive_stats)
		return nP

	def calculate_defensive_vector(self, defensive_stats):
		nP, nQ = matrix_factorization(defensive_stats)
		return nQ

class Loader(object):

	def __init__(self, date):
		self.date = date

	def prepare_games(self, team):
		blocks = self.data.get(team)

		games = []
		for block in blocks:
			games.append(__game__(block))

		games = self.slice_by_date(games, self.date)
		return self.filter_games(games, team)

	@classmethod
	def set_teams(cls, teams):
		cls.data = {}
		for team in teams:
			path = os.path.join('../crawler/data/', team + '.json')
		
			with open(path, mode = 'r') as inputfile:
				games = json.load(inputfile)

			for game in games:
				game["date"] = parse('2016 ' + game["date"]).date()

			cls.data.update({team : games})

	@classmethod
	def parse_date(cls, date):
		return cls(parse(date).date())

	@staticmethod
	def get_team_statistics(game, team):
		attr = None
		if team.lower() == game.team1.lower(): attr = 'stats1'
		if team.lower() == game.team2.lower(): attr = 'stats2'
		
		if attr == None:
			print("Given team hasn't played in game.")
			return None
		return getattr(game, attr)

	def get_game_location(self, game, team):
		"""
		Given the game and current team, returns location relative to the current team. 
		"""
		team_statistics = self.get_team_statistics(game, team)
		return team_statistics["location"]

	def filter_games(self, games, team):
		home_games = []
		road_games = []
		for game in games:
			location = self.get_game_location(game, team)
			if location == 'home': home_games.append(game)
			if location == 'road': road_games.append(game)
		return home_games, road_games

	def slice_by_date(self, games, date):
		res = []
		for game in games:
			if game.date < date:
				res.append(game)
		return res

Loader.set_teams(TEAMS)

start_date = date(year = 2016, month = 10, day = 1)
end_date = date(year = 2016, month = 10, day = 30)
delta = end_date - start_date

for day in range(delta.days + 1):
	print(start_date + td(days = day))

loader = Loader.parse_date(date = '2016-12-10')
home_games, road_games = loader.prepare_games('ATL')

vectorCalculator = VectorCalculator(games = home_games, team = 'ATL', depth = 3)
pprint(vectorCalculator.offensive_vector)
pprint(vectorCalculator.defensive_vector)






