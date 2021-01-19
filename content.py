"""
Create a structured dataset from (semi-) unstructured text.
"""
import pathlib
import os
import re


class Content(dict):
    """Stores content-related data."""

    file = "informatiekunde_begrippen_RAW_v02.txt"
    error_patterns = [r"\]", r"\[", "[000-999]", r"(\n)", r"[A-Z]$"]
    contatenation_indicators = [r"(\-)$"]

    def __init__(self):
        super().__init__(self)
        self.data = None
        self.structured = None
        self.fpath = None
        self.work_dir = None

    def init_raw_data(self):
        with open(self.rawtext_fpath, "r", encoding="utf8") as f:
            self.data = [line for line in f.readlines()]

    def init_fullpath(self):
        self.work_dir = pathlib.Path(__file__).parent.absolute()
        self.rawtext_fpath = os.path.normpath("{}/content_bronnen/{}".format(
                                              self.work_dir, self.file))

    def clean_line(self, line):
        """Remove errors from given line of text and return result"""
        for pattern in self.error_patterns:
            line = re.sub(pattern, "", line)

        return line

    def contains_concatenation_indicator(self, line):
        for indicator in self.contatenation_indicators:
            if re.search(indicator, line):
                return indicator

    def prepend_to_nextline(self, line, inbetween, line_index, line_skips):
        nextline = self.data[line_index+1]

        if not nextline.endswith("."):
            indicator = self.contains_concatenation_indicator(nextline)
            if indicator:
                next_inbetween = ""
                nextline = re.sub(indicator, "", nextline)
            else:
                next_inbetween = " "

            nextline, line_skips = self.prepend_to_nextline(nextline, next_inbetween, line_index+1, 
                                                            line_skips+1)

        return line + inbetween + nextline, line_skips

    def concatenate_lines(self):
        concatenated_lines = []
        line_skips = 0
        for i, line in enumerate(self.data):
            #print("line ", line)
            if line_skips:
                line_skips -= 1
                continue

            if not line.endswith("."): 
                inbetween = " "   
                indicator = self.contains_concatenation_indicator(line)
                if indicator:
                    inbetween = ""
                    line = re.sub(indicator, "", line)
                
                line, line_skips = self.prepend_to_nextline(line, inbetween,
                                                            i, line_skips+1)

            concatenated_lines.append(line)

        self.data = concatenated_lines

    def remove_data_errors(self):
        clean_data = []
        for line in self.data:
            cleanline = self.clean_line(line)
            if cleanline:
                clean_data.append(cleanline)

        self.data = clean_data


content = Content()
content.init_fullpath()
content.init_raw_data()
content.remove_data_errors()
content.concatenate_lines()

print("Structured data:", content.data[len(content.data)-200:len(content.data)])
