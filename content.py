"""
Create a structured dataset from (semi-) unstructured text.
"""
import pathlib
import os
import re

import workio


class Content(dict):
    """Stores content-related data."""

    file = "informatiekunde_begrippen_RAW_v02.txt"
    error_patterns = [r"\]", r"\[", r"\[([000-999])\]", r"(\n)", r"[A-Z]$"]
    concatenation_indicators = [r"(\-)$"]
    redflags = ["Zie octrooi"]
    hotfixes = [(" 14f4 Kbps", " 144 Kbps"), ("begrippenlijst", ""), ("begrippenlijst ", "")]
    part_amount = 15

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

    def extract_concat_indicator(self, line):
        for indicator in self.concatenation_indicators:
            if re.search(indicator, line):
                return indicator

    def prepend_to_nextline(self, line, inbetween, line_index, line_skips):
        nextline = self.data[line_index+1]

        if not nextline.endswith("."):
            indicator = self.extract_concat_indicator(nextline)
            if indicator:
                next_inbetween = ""
                nextline = re.sub(indicator, "", nextline)
            else:
                next_inbetween = " "

            nextline, line_skips = self.prepend_to_nextline(nextline, next_inbetween, line_index+1, 
                                                            line_skips+1)

        return line + inbetween + nextline, line_skips

    def extract_definition(self, sentence):
        definition = False
        words = sentence.split(" ")
        for i, word in enumerate(words):
            if not word:
                continue

            if definition:
                definition += word + " "
            else:
                if word[0].isupper() and i != 0:
                    if i + 1 == len(words):
                        return

                    # If the next word's first letter is not capitalized,
                    # it means the current word is the start of the definition.
                    if (not words[i+1][0].isupper()) and (not words[i+2][0].isupper()):
                         definition = word + " "

        return definition

    def extract_term(self, sentence, definition):
        if not definition:
            return sentence
        else:
            return sentence.split(definition[0:15])[0]

    def separate_datapairs(self):
        datapairs = {}
        i = 0
        for sentence in self.data:
            i += 1
            _definition = self.extract_definition(sentence)
            _term = self.extract_term(sentence, _definition)
            if not _definition:
                datapairs[term] = definition + _term
            else:
                term = _term
                definition = _definition
                datapairs[term] = definition

        self.data = datapairs

    def remove_extraneous_sentences(self):
        filtered_data = self.data.copy()
        for sentence in self.data:
            if any([((not sentence) or redflag in sentence) for redflag in self.redflags]):
                filtered_data.remove(sentence)

        self.data = filtered_data

    def implement_hotfixes(self):
        hotfixed_data = {}
        for term, definition in self.data.items():
            for hotfix in self.hotfixes:
                definition = definition.replace(
                    hotfix[0], hotfix[1])

            hotfixed_data[term] = definition

        self.data = hotfixed_data                    

    def concatenate_lines(self):
        sentences = []
        line_skips = 0
        for i, line in enumerate(self.data):
            #print("line ", line)
            if line_skips:
                line_skips -= 1
                continue

            if not line.endswith("."): 
                inbetween = " "   
                indicator = self.extract_concat_indicator(line)
                if indicator:
                    inbetween = ""
                    line = re.sub(indicator, "", line)
                
                line, line_skips = self.prepend_to_nextline(line, inbetween,
                                                            i, line_skips+1)

            sentences.append(line)

        self.data = sentences

    def remove_data_errors(self):
        clean_data = []
        for line in self.data:
            cleanline = self.clean_line(line)
            if cleanline:
                clean_data.append(cleanline)

        self.data = clean_data

    def split_into_parts(self):
        part_length = len(self.data) / self.part_amount
        part_dictionary = {}
        part = {}
        i = 1
        for term, definition in self.data.items():
            if len(part) <= part_length:
                part[term] = definition
            else:
                part_dictionary["Part {}".format(i)] = part
                i += 1
                part = {}

        self.data = part_dictionary


def get_informatiekunde_data():
    content = BedrijfsInformatieSystemenContent()
    content.init_fullpath()
    content.init_raw_data()
    content.remove_data_errors()
    content.concatenate_lines()
    content.remove_extraneous_sentences()
    content.separate_datapairs()
    content.implement_hotfixes()
    content.split_into_parts()

    #print("Structured data:", content.data)

    return content.data


def get_data_dict(filepath, subject):
    rawdata = {}
    if filepath.endswith(".csv"):
        import csv
        with open(filepath, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=" ", quotechar="|")
            for row in reader:
                row = " ".join(row)
                question = row.split(";")[1].strip()
                answer = row.split(";")[0].strip()
                rawdata[answer] = question
    elif filepath.endswith(".py"):
        import importlib.util
        spec = importlib.util.spec_from_file_location("module.name", filepath)
        file_ = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(file_)
        rawdata = file_.content
    elif filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as textfile:
            for line in textfile.readlines():
                if not ":" in line:
                    print("skipping line: {} in path {}".format(line, filepath))
                    continue

                question = line.split(":")[1].strip()
                answer = line.split(":")[0].strip()
                rawdata[answer] = question
    else:
        return None

    return rawdata


def get_content(subject=None):
    content = {}
    work_dir = pathlib.Path(__file__).parent.absolute()
    subject_dir = os.path.join(work_dir, "database", subject)
    rawdata_files = workio.get_rawdata_files(subject)
    curriculum_file = os.path.join(subject_dir, "curriculum.json")
    if subject:
        for filepath in rawdata_files:
            data_dict = get_data_dict(filepath, subject)
            if not data_dict:
                continue

            chapter, _ = os.path.splitext(os.path.basename(filepath))
            content[chapter] = data_dict

    return content


if __name__ == "__main__":
    # content = get_informatiekunde_data()

    subject="Aarde, mens en milieu 1"
    content = get_content(subject)
    print("Chapters:", list(content.keys()))
    no_of_questions = 0 
    for chapter_data in content.values():
        no_of_questions += len(list(chapter_data.keys()))

    print("Total no. of questions:", no_of_questions)

    session = workio.Session(subject)
    session.write_curriculum(content)
