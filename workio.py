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
			datetime.strftime(datetime.now(), "%m-%d-%Y, %H-%M-%S")))
		self.results_path = os.path.join(self.session_dir, "results.json")

	def get_data(self, db_path):
		with open(db_path, "r", encoding='utf-16') as database:
			return json.load(database)

	def get_results(self):
		return self.get_data(self.results_path)

	def get_curriculum(self):
		return self.get_data(self.curriculum_path)

	def append_results(self, data):
		existing_results = self.get_results()
		results = {**existing_results, **data}
		self.write_to_database(results, self.results_path)

	def write_curriculum(self, data):
		self.write_to_database(data, self.curriculum_path)

	def write_to_database(self, content, db_path):
		with open(db_path, "w", encoding='utf-16') as database:
			json.dump(content, database, indent=4, ensure_ascii=False)
