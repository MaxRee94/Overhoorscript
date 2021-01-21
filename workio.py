"""Getter- and setter functions for database"""
import json
import os
import pathlib



work_dir = pathlib.Path(__file__).parent.absolute()
database_dir = os.path.join(work_dir, "database")
curriculum_path = os.path.join(database_dir, "curriculum.json")

def write_to_database(content):
	with open(curriculum_path, "w", encoding='utf-16') as database:
		json.dump(content, database, indent=4, ensure_ascii=False)
