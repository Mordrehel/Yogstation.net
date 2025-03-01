from datetime import datetime

import glob

import os

import re	# it begins

from yogsite.config import cfg


GAME_LOG_REGEX = re.compile(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\] ([\s\S]*?)\n(?=(?:^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]|\Z))", re.M) # wew

sound_extensions = [".aac",
	".mp3",
	".ogg",
	".opus",
	".wav",
	".weba"]

class RoundLogs():

	files_to_parse = [ # We will ignore any file not in this
		"asset.log",
		"attack.log",
		"cloning.log",
		"config_error.log",
		"game.log",
		"hrefs.log",
		"job_debug.log",
		"manifest.log",
		"map_errors.log",
		"mecha.log",
		"ntsl.log",
		"paper.log",
		"pda.log",
		"runtime.log",
		"sql.log",
		"telecomms.log",
		"tgui.log",
		"virus.log"
	]

	def __init__(self, round_id):
		self.round_id = round_id
		self.entries = []
	
	def get_directory(self):
		matches = glob.glob(f"{cfg.get('logs.directory')}/*/*/*/round-{self.round_id}")

		if matches:
			return matches[0]
	
	def find_demo_file(self):
		directory = self.get_directory()
		files = os.listdir(directory)

		if "demo.txt.gz" in files:
			return os.path.join(directory, "demo.txt.gz")

		elif "demo.txt" in files:
			return os.path.join(directory, "demo.txt")
		
		return None
	
	def get_sounds(self):
		directory = self.get_directory()
		files = os.listdir(directory)
		sounds = []
		for file in files:
			extension = os.path.splitext(file)[1]
			if extension in sound_extensions:
				sounds.append(file)
		return sounds

	def find_log_file(self, filename):
		directory = self.get_directory()
		files = os.listdir(directory)

		if filename in files:
			return os.path.join(directory, filename)
		return None

	def load_entries(self):

		directory = self.get_directory()

		if not directory:
			raise Exception(f"Can't find logs for round {self.round_id}")

		self.parse_directory(directory)

		self.entries = sorted(self.entries, key=lambda x: x.timestamp)

		return self.entries

	def parse_text(self, text, category):
		matches = GAME_LOG_REGEX.findall(text)

		for match in matches:

			timestamp = datetime.strptime(match[0], "%Y-%m-%d %H:%M:%S.%f")
			content = match[1]

			entry = LogEntry(timestamp, category, content)

			self.entries.append(entry)

	def parse_directory(self, directory):
		for filename in os.listdir(directory):
			if filename in self.files_to_parse:

				with open(os.path.join(directory, filename)) as logfile:
					self.parse_text(logfile.read(), filename.split(".")[0]) # TODO: change


class LogEntry():
	def __init__(self, timestamp, category, content):
		self.timestamp = timestamp
		self.category = category
		self.content = content
	
	def __str__(self):
		return f"[{self.category.upper()}] <{self.timestamp}>: {self.content}"
	
	def get_color_class(self):
		if self.category in self.category_color_classes:
			return self.category_color_classes[self.category]
		
		return ""
	
	def to_dict(self):
		return {
			"timestamp": self.timestamp.timestamp(),
			"category": self.category,
			"content": self.content
		}
