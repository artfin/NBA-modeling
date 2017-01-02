import json
import os

class Game(object):
	'''Contains all information about the game'''

	def __init__(self, shortcut1, shortcut2, stats1, stats2, date):

		self.shortcut1 = shortcut1
		self.shortcut2 = shortcut2
		self.stats1 = stats1
		self.stats2 = stats2
		self.date = date


