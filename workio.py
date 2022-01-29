"""Getter- and setter functions for database"""
import json
import os
import pathlib
from datetime import datetime


def get_data(db_path):
    if not os.path.exists(db_path):
        return {}
    else:
        with open(db_path, "r", encoding='utf-16') as database:
            return json.load(database)


def get_rawdata_files(subject):
    if os.path.isdir(subject):
        assert not os.path.isfile(subject), "Given subject dir '{}' is a file, not a directory.".format(subject)
        rawdata_dir = subject
    else:
        work_dir = pathlib.Path(__file__).parent.absolute()
        rawdata_dir = os.path.join(work_dir, "content_bronnen", subject)

    rawdata_files = [os.path.join(rawdata_dir, file) for file in os.listdir(rawdata_dir)]

    return rawdata_files


def get_curriculum_file(subject):
    subject_dir = get_subject_dir(subject)

    return os.path.join(subject_dir, "curriculum.json")


def get_subject_dir(subject):
    work_dir = pathlib.Path(__file__).parent.absolute()
    subject_dir = os.path.join(work_dir, "database", subject)
    
    return subject_dir


def get_subjects():
    """Return the names of all subject folders in the database dir."""

    work_dir = pathlib.Path(__file__).parent.absolute()
    database_dir = os.path.join(work_dir, "database")

    return [subject for subject in os.listdir(database_dir)
            if os.path.isdir(os.path.join(database_dir, subject))]


def get_subject_dirs():
    subjects = get_subjects()
    subject_dirs = []
    for subj in subjects:
        subject_dirs.append(get_subject_dir(subj))

    return subject_dirs


def get_last_session_path():
    latest_time = 0
    for subject_dir in get_subject_dirs():
        session_dirs = [os.path.join(subject_dir, session_dir) for session_dir in os.listdir(subject_dir)]
        session_dir_index = -1
        while len(os.listdir(session_dirs[session_dir_index])) == 0:
            session_dir_index -= 1

        session_dir = session_dirs[session_dir_index]
        session_files = os.listdir(session_dir)
        last_session_file = os.path.join(session_dir, session_files[-1])

        creation_time = os.path.getmtime(last_session_file)
        if creation_time > latest_time:
            latest_time = creation_time
            latest_file = last_session_file

    return latest_file


def get_global_preferences():
    global_preferences = {}

    session_file = get_last_session_path()
    print("Getting global prefs from file:", session_file)
    session_data = get_data(session_file)
    global_preferences["question_mode"] = session_data.get("question_mode", None)
    global_preferences["subject_index"] = session_data.get("subject_index", None)

    return global_preferences


class Session():

    def __init__(self, subject):
        self.subject_dir = get_subject_dir(subject)
        self.curriculum_path = os.path.join(self.subject_dir, "curriculum.json")
        self.session_dir = os.path.join(self.subject_dir, "Session_{}".format(
            datetime.strftime(datetime.now(), "%m-%d-%Y,%H-%M-%S")))
        self.results_path = os.path.join(self.session_dir, "results.json")

    def get_results(self):
        return get_data(self.results_path)

    def get_curriculum(self):
        return get_data(self.curriculum_path)

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
        part_length = len(self.get_curriculum().get(part))
        for session_dir in os.listdir(self.subject_dir):
            session_dir = os.path.join(self.subject_dir, session_dir)
            if not os.path.isfile(session_dir):
                try:
                    session_file = os.path.join(session_dir, os.listdir(session_dir)[0])
                except IndexError:
                    continue

                session_data = get_data(session_file)

                if part in session_data.keys():
                    #print("session amount for part", part, "is", (len(session_data[part].get("successes", {})) / part_length))
                    session_amount += (len(session_data[part].get("successes", {})) / part_length)

        return round(session_amount, 1)
