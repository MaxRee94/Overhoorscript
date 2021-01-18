"""
Create a structured dataset from (semi-) unstructured text.
"""
import pathlib
import os
import re


class Content(dict):
    """Stores content-related data."""

    def __init__(self):
        super().__init__(self)
        self.data = None
        self.structured = None
        self.fpath = None
        self.work_dir = None

    def init_raw_data(self):
        with open(self.rawtext_fpath, "r", encoding="utf8") as f:
            self.data = [line for line in f.readlines()]

    def init_fullpath(self, file):
        self.work_dir = pathlib.Path(__file__).parent.absolute()
        self.rawtext_fpath = os.path.normpath("{}/content_bronnen/{}".format(
                                              self.work_dir, file))

    def clean_line(self, line, error_patterns):
        """Remove errors from given line of text and return result"""
        for pattern in error_patterns:
            line = re.sub(pattern, "", line)

        return line

    def remove_data_errors(self, error_patterns):
        clean_data = []
        for line in self.data:
            cleanline = self.clean_line(line, error_patterns)
            clean_data.append(cleanline)

        self.data = clean_data


file = "informatiekunde_begrippen_RAW_v02.txt"
error_patterns = [r"(\n)", r"[A-Z]$"]

content = Content()
content.init_fullpath(file)
content.init_raw_data()
content.remove_data_errors(error_patterns)

print("Cleaned data:", content.data[len(content.data)-200:len(content.data)])
