import requests
from bs4 import BeautifulSoup
import logging
import time
import json
import os

# --------------------------------------------
from game import Game
from include import Include
# --------------------------------------------

class TeamScraper(object):

	base_url = "http://basketball-reference.com"

	stat_names = ['fg', 'fga', 'fg3', 'fg3a', 'ft', 'fta', 'orb', 'drb', 'ast', 'blk', 'tov', 'pts']

	full_script_path = os.path.realpath(__file__)

	def __init__(self, shortcut):

		self.include = Include()

		url = "http://www.basketball-reference.com/teams/" + shortcut + "/2017_games.html"
		
		r = requests.get(url)

		soup = BeautifulSoup(r.text, 'lxml')

		links = soup.findAll('td', attrs = {'data-stat' : 'box_score_text'})
		game_locations = soup.findAll('td', attrs = {'data-stat' : 'game_location'})

		locations = []

		for location in game_locations:
			if not location.text:
				locations.append('home')
			else:
				locations.append('road')

		games = []

		for i in range(0, len(links)):

			print "i: {0}".format(i)

			boxscore_link = self.base_url + links[i].a['href']

			r = requests.get(boxscore_link)
			time.sleep(0.5)

			soup = BeautifulSoup(r.text, 'lxml')

			if "Page Not Found" not in soup.text:

				date = soup.title.text.split(',')[1].strip()
				
				performers = soup.findAll('a', attrs = {'itemprop' : 'name'})

				rival_shortcuts = []

				for performer in performers:
					rival_shortcuts.append(self.include.shortcuts[performer.text].lower())

				if shortcut.lower() == rival_shortcuts[1]:
					rival_shortcuts[0], rival_shortcuts[1] = rival_shortcuts[1], rival_shortcuts[0]

				stats_1 = self._fill_stats(soup, rival_shortcuts[0])
				stats_2 = self._fill_stats(soup, rival_shortcuts[1])

				stats_1.update({'location' : locations[i]})
				if locations[i] == 'home':
					stats_2.update({'location' : 'road'})
				else:
					stats_2.update({'location' : 'home'})
		
				game = Game(rival_shortcuts[0], rival_shortcuts[1], stats_1, stats_2, date)
				games.append(game)

			else:
				break

		data = []

		for game in games:

			entry = {
				 'team1'  : game.shortcut1, 
				 'stats1' : game.stats1,
				 'team2'  : game.shortcut2,
				 'stats2' : game.stats2,
				 'date' : game.date
				 }

			data.append(entry)

		file_path = os.path.join(os.path.dirname(self.full_script_path), "../data/" + shortcut.upper() + ".json")

		with open(file_path, mode = 'w+') as outputfile:
			outputfile.write(json.dumps(data, indent = 4, sort_keys = True, separators = (',', ': ')))

	def _fill_stats(self, soup, shortcut):

		table_id = 'box_' + shortcut + '_basic'

		last_line = soup.find('table', attrs = {'id' : table_id}).tfoot.tr

		stats = {}

		for stat_name in self.stat_names:
			stats.update({stat_name : int(last_line.find('td', attrs = {'data-stat' : stat_name}).text)})

		return stats