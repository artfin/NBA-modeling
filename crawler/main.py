import requests
from bs4 import BeautifulSoup
import os

# --------------------------------------------
from lib.game import Game
from lib.team_scraper import TeamScraper
from lib.include import Include
# --------------------------------------------

include = Include()

full_script_path = os.path.realpath(__file__)

for key, value in include.shortcuts.iteritems():
	file_path = os.path.join(os.path.dirname(full_script_path), "data/" + value + ".json")

	data = []

	print "Initializing teamScraper for {0}".format(value.upper())
	teamScraper = TeamScraper(value)

