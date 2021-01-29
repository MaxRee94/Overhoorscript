"""Getter- and setter functions for database"""
import json
import os
import pathlib
from datetime import datetime


class Session():

	def __init__(self):
		self.work_dir = pathlib.Path(__file__).parent.absolute()
		self.database_dir = os.path.join(self.work_dir, "database")
		self.curriculum_path = os.path.join(self.database_dir, "curriculum.json")
		self.session_dir = os.path.join(self.database_dir, "Session_{}".format(
			datetime.strftime(datetime.now(), "%m-%d-%Y,%H-%M-%S")))
		self.results_path = os.path.join(self.session_dir, "results.json")

	def get_data(self, db_path):
		if not os.path.exists(db_path):
			return {}
		else:
			with open(db_path, "r", encoding='utf-16') as database:
				return json.load(database)

	def get_results(self):
		return self.get_data(self.results_path)

	def get_curriculum(self):
		return self.get_data(self.curriculum_path)

	def write_log(self, data):
		print("Writing log to database at '{}'".format(self.results_path))
		self.write_to_database(data, self.results_path)

	def write_curriculum(self, data):
		self.write_to_database(data, self.curriculum_path)

	def write_to_database(self, content, db_path):
		parent_dir = pathlib.Path(db_path).parent
		if not os.path.exists(parent_dir):
			os.makedirs(parent_dir)

		with open(db_path, "w", encoding='utf-16') as database:
			json.dump(content, database, indent=4, ensure_ascii=False)

	def get_part_info(self, part):
		session_amount = 0
		curriculum_length = len(self.get_curriculum())
		for session_dir in os.listdir(self.database_dir):
			session_dir = os.path.join(self.database_dir, session_dir)
			if not os.path.isfile(session_dir):
				try:
					session_file = os.path.join(session_dir, os.listdir(session_dir)[0])
				except IndexError:
					continue

				session_data = self.get_data(session_file)

				if part in session_data.keys():
					session_amount += round(len(session_data.values()) / curriculum_length, 1)

		return session_amount
