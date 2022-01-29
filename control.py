"""Controller"""
import sys
import random
import re
from functools import partial

from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qg

import content, workio, window


class Controller(qc.QObject):

    title = "Overhoorscript"
    finished = qc.Signal()

    def __init__(self):
        self.test_gui = None
        self.start_menu = None
        self.state = "question"
        self.global_prefs = workio.get_global_preferences()
        self.question_mode = self.global_prefs["question_mode"] or "term"
        self.subjects = workio.get_subjects()
        self.reload()

    def reload(self, subj_index=None):
        if self.start_menu:
            self.start_menu.deleteLater()
            self.start_menu = None

        if subj_index is None:
            self.subj_index = self.global_prefs["subject_index"] or -1
        else:
            self.subj_index = subj_index

        self.start_menu = window.StartMenu(self.subjects, self.subj_index, title=self.title)
        self.subject = self.subjects[self.subj_index]
        self.exam = Examinator(self.subject, self.subj_index)
        self.on_questionmode_clicked(force_question_mode=self.question_mode)
        self.difficulty = 50

        #self.update_gui()
        self.show_startmenu()
        self.make_menu_connections()

    def show_startmenu(self):
        parts = self.exam.get_parts()
        self.start_menu.add_parts_buttons(parts)
        self.start_menu.show()

    def start_test(self, part_number):
        # delete start menu
        self.start_menu.deleteLater()
        self.start_menu = None

        # init session-curriculum and test menu
        self.exam.update_curriculum(part_number)
        self.exam.update()
        self.test_gui = window.TestGUI("{}  -  {}".format(self.exam.subject, self.exam.part_name))
        self.make_test_connections()
        self.update_gui()
        self.test_gui.show()

    def close(self):
        self.test_gui.close()

    def make_test_connections(self):
        # ---------------------------------------------- #
        # TEST UI
        # ---------------------------------------------- #
        self.test_gui.check_button.clicked.connect(self.on_check_clicked)
        self.test_gui.hint_button.clicked.connect(self.on_hint_clicked)
        self.test_gui.skip_button.clicked.connect(self.on_skip_clicked)
        self.test_gui.consider_correct_btn.clicked.connect(self.on_consider_correct_clicked)
        self.test_gui.closed.connect(self.exam.close)

    def make_menu_connections(self):
        # ---------------------------------------------- #
        # EXAMINATOR
        # ---------------------------------------------- #
        # self.exam.finished.connect(self.on_finished)

        # ---------------------------------------------- #
        # STARTMENU UI
        # ---------------------------------------------- #
        # question mode
        self.start_menu.questionmode_button.clicked.connect(self.on_questionmode_clicked)

        # search option
        self.start_menu.search_button.clicked.connect(self.execute_search)

        # subject selection
        self.start_menu.subject_changed.connect(self.reload)

        # parts buttons
        parts_layout = self.start_menu.parts_layout
        rows_count = parts_layout.count()
        part_index = 1
        for i in range(rows_count):
            parts_row = parts_layout.itemAt(i).layout()
            for j in range(parts_row.count()):
                button = parts_row.itemAt(j).widget()
                button.clicked.connect(partial(self.start_test, part_index))
                part_index += 1

    def on_finished(self):
        self.exam.close()
        self.test_gui.deleteLater()

    def execute_search(self):
        search_query = self.start_menu.search_field.text().capitalize()
        search_result = self.exam.get_search_result(search_query)
        self.start_menu.set_search_result(search_result)
        if self.exam.search_term:
            self.start_menu.update_search_field(self.exam.search_term)

    def on_consider_correct_clicked(self):
        user_answer = self.test_gui.txtfield.text()

        if self.exam.question_mode == "definition":
            print(f"Considering answer '{user_answer}' as correct...")
            current_answer = self.exam.correct_answer
            new_answer = current_answer.strip() + " && " + user_answer.strip()

            self.exam.curriculum_session[self.exam.question] = new_answer
            del self.exam.curriculum_total[self.exam.part_name][current_answer]
            self.exam.curriculum_total[self.exam.part_name][new_answer] = (
                self.exam.question
            )

            if self.exam.question in self.exam.questions:
                self.exam.questions.remove(self.exam.question)

            if user_answer not in self.exam.correct_answer.split(" && "):
                print(f"Writing new answer '{new_answer}' to database...")
                self.exam.session.write_curriculum(self.exam.curriculum_total)
                print("New answer written succesfully.")
            else:
                print("Alternative answer was already in database. Skipping write.")

        else:
            print(f"Considering answer '{user_answer}' as correct...")
            current_answer = self.exam.correct_answer
            new_answer = current_answer.strip() + " && " + user_answer.strip()

            self.exam.curriculum_session[self.exam.question] = new_answer
            del self.exam.curriculum_total[self.exam.part_name][self.exam.question]
            self.exam.curriculum_total[self.exam.part_name][self.exam.question] = (
                new_answer
            )

            if self.exam.question in self.exam.questions:
                self.exam.questions.remove(self.exam.question)

            if user_answer not in self.exam.correct_answer.split(" && "):
                print(f"Writing new answer '{new_answer}' to database...")
                self.exam.session.write_curriculum(self.exam.curriculum_total)
                print("New answer written succesfully.")
            else:
                print("Alternative answer was already in database. Skipping write.")

        self.exam.total_question_count -= 1
        remove_mistake = True
        # if current_answer in self.exam.log.get("mistakes", []):
        #     self.exam.total_question_count -= 1
        #     remove_mistake = True
        # else:
        #     remove_mistake = False

        # update log
        self.exam.update_log("successes", remove_mistake=remove_mistake)

        # update gui to indicate acceptance of alternative answer.
        self.test_gui.replace_result(True)

        # update gui to indicate new remaining questions number.
        self.test_gui.set_qtracker(self.exam.total_question_count, self.exam.answered_question_count - 1)

    def on_skip_clicked(self):
        print(f"skipping '{self.exam.question}'")
        if self.exam.question_mode == "definition":
            if self.exam.curriculum_total[self.exam.part_name].get(self.exam.correct_answer):
                del self.exam.curriculum_total[self.exam.part_name][self.exam.correct_answer]
            
            if self.exam.question in self.exam.questions:
                self.exam.questions.remove(self.exam.question)
            self.exam.total_question_count -= 1

            print("Removing question from database...")
            self.exam.session.write_curriculum(self.exam.curriculum_total)
            print("Removal successful.")

            self.on_check_clicked()
            if self.exam.question_mode == "evaluation":
                self.on_check_clicked()
        else:
            raise NotImplementedError("Skipping questions is not yet implemented for term-definition order.")

    def on_questionmode_clicked(self, force_question_mode=None):
        if self.exam.question_mode == "term" or force_question_mode == "definition":
            # switch questionmode to "definition"
            self.exam.question_mode = "definition"
            self.start_menu.questionmode_button.setText("Definition - Term")
        elif self.exam.question_mode == "definition" or force_question_mode == "term":
            # switch questionmode to "term"
            self.exam.question_mode = "term"
            self.start_menu.questionmode_button.setText("Term - Definition")

    def on_hint_clicked(self):
        if self.state == "question":
            print("hint requested")
            self.exam.update_log("hints")
            self.test_gui.set_correctiontext(self.exam.correct_answer, 
                                             reveal=self.difficulty*0.8)

    def on_check_clicked(self):
        if self.state == "question":
            answer = self.test_gui.txtfield.text()
            self.state = "evaluation"
            self.exam.eval(answer)
            self.update_gui(self.exam.result)
        else:
            # Close if all questions have been answered
            if not self.exam.questions:
                self.test_gui.close()
                self.reload(subj_index=self.subj_index)
                return

            self.state = "question"
            self.exam.update()
            self.update_gui()

    def update_gui(self, result=None):
        print('-- Updating gui...\n')

        if self.state == "question": 
            self.test_gui.set_qtracker(self.exam.total_question_count,
                                       self.exam.answered_question_count)
            self.test_gui.enable_textfield(True)
            self.test_gui.reset_textfields()
            self.test_gui.set_questiontext(self.exam.question)
            self.test_gui.set_mode(self.state)
        else:
            self.test_gui.enable_textfield(False)
            self.test_gui.set_correctiontext(self.exam.correct_answer)
            self.test_gui.replace_result(result)
            self.test_gui.set_mode(self.state)
            self.test_gui.set_qtracker(self.exam.total_question_count,
                                       self.exam.answered_question_count - 1)


class Examinator():

    def __init__(self, subject, subject_index):
        self.question = ""
        self.correct_answer = ""
        self.curriculum_total = {}
        self.curriculum_session = {}
        self.questions = []
        self.search_term = None
        self.minimum_answer = 3
        self.result = None
        self.log = {}
        self.total_question_count = 0
        self.answered_question_count = 0
        self.part_name = ""
        self.match_threshold = 90.0
        self.subject_index = subject_index
        self.subject = subject
        self.session = workio.Session(subject)
        self.question_mode = "definition"
        self.part_number = None
        self.update_curriculum()

    def update_curriculum(self, part_number=None):
        if part_number is None:
            self.curriculum_total = self.session.get_curriculum()
            return
        else:
            self.part_number = part_number

        self.part_name = list(self.curriculum_total.keys())[part_number - 1]
        if self.question_mode == "term":
            self.curriculum_session = self.curriculum_total[self.part_name]
        else:
            self.curriculum_session = self.get_reversed_curriculum(self.curriculum_total[self.part_name])

        self.total_question_count = len(self.curriculum_session)
        self.questions = [q.split("&&")[0].strip() for q in self.curriculum_session.keys()]

    def get_reversed_curriculum(self, curriculum):
        reversed_curriculum = {}
        for term, definition in curriculum.items():
            if isinstance(definition, list):
                print("definition:", definition)
            reversed_curriculum[definition] = term

        return reversed_curriculum

    def get_search_result(self, search_query):
        result = ""
        print(" search query:", search_query)
        result_options = {}
        for part in self.curriculum_total.values():
            #print("keys:", list(part.keys()))
            for term in part.keys():
                match, percentage = self._match(search_query, term, log=False, match_threshold=20, give_percentage=True)
                if match:
                    result_options[percentage] = {"term": term, "definition": part[term]}

        try:
            result = result_options[max(list(result_options.keys()))]["definition"]
            self.search_term = result_options[max(list(result_options.keys()))]["term"]
        except ValueError:
            self.search_term = None
            result = ""

        return result.split(" && ")[0]

    def close(self):
        log = {self.part_name: self.log, "question_mode": self.question_mode, "subject_index": self.subject_index}
        self.session.write_log(log)

    def update_log(self, log_key, remove_mistake=False):
        if log_key in self.log.keys():
            self.log[log_key].append(self.question)
        else:
            self.log[log_key] = [self.question]

        if remove_mistake:
            self.log["mistakes"].remove(self.question)

    def eval(self, answer, consider_correct=False):
        print("-- Evaluating answer:", answer, "to question", 
              self.question)

        self.answered_question_count += 1

        if self.match(answer, self.correct_answer):
            print("-- The answer was correct!")
            self.questions.remove(self.question)
            self.result = True
            self.update_log("successes")
        else:
            print("-- Incorrect.", self.correct_answer)

            self.result = False
            self.total_question_count = self.total_question_count + 1
            self.update_log("mistakes")

    def get_parts(self):
        return {part: self.session.get_part_info(part) for part in self.curriculum_total.keys()}

    def update(self):
        self.question = self.questions[random.randint(0, len(self.questions) - 1)]

        self.correct_answer = self.curriculum_session[self.question]

    def get_all_word_concatenations(self, words, inbetween=""):
        all_word_concatenations = []
        for word1 in words:
            for word2 in words:
                if not word1 == word2:
                    all_word_concatenations.append(word1+inbetween+word2)

        return all_word_concatenations

    def get_match_percentage(self, word_matches, correct_words_amnt):
        if correct_words_amnt == 0:
            return 0.0
        else:
            return (word_matches / correct_words_amnt)  * 100.0

    def _get_word_matches(self, correct_words, answer_words):
        matches = 0
        for word in answer_words:
            if word != "" and word.strip(",") in correct_words:
                matches += 1

        return matches

    def get_word_matches(self, correct_words, answer, recurse=True):
        conventional_matches = self._get_word_matches(correct_words, answer.split(" "))
        concatenation_matches = self._get_word_matches(correct_words, self.get_all_word_concatenations(answer.split(" ")))
        dash_matches = self._get_word_matches(correct_words, self.get_all_word_concatenations(answer.split(" "), "-"))
        non_dash_matches = 0
        if recurse:
            non_dash_answer_matches = self.get_word_matches(correct_words, answer.replace("-", ""), recurse=False)
            non_dash_corrections = []
            for word in correct_words:
                non_dash_corrections.extend(word.split("-"))
            non_dash_correction_matches = self.get_word_matches(non_dash_corrections, answer.replace("-", ""), recurse=False)
            non_dash_matches = non_dash_answer_matches + non_dash_correction_matches

        return conventional_matches + concatenation_matches + dash_matches + non_dash_matches

    def remove_brackets(self, word):
        return re.sub(r"\(.+\) ", " ", word).strip().lower()

    def _match(self, answer, correct_answer, log=True, match_threshold=None, give_percentage=False):
        correct_answer = self.remove_brackets(correct_answer)
        answer = self.remove_brackets(answer)
        if log:
            print("Your answer:", answer)
        print("Correct answer:", correct_answer)

        correct_words = [word.strip(",") for word in correct_answer.split(" ") if word]
        word_matches = self.get_word_matches(correct_words, answer)
        match_percentage = self.get_match_percentage(word_matches, len(correct_words) * 3)

        if match_percentage < self.match_threshold:
            correct_concatenations = self.get_all_word_concatenations(correct_words)
            _word_matches = self.get_word_matches(correct_concatenations, answer)
            _match_percentage = self.get_match_percentage(word_matches, len(correct_words) * 3)
            if _match_percentage > match_percentage:
                match_percentage = _match_percentage

        # print("Word matches:", word_matches)
        # print("Match percentage:", match_percentage)

        if not match_threshold:
            match_threshold = self.match_threshold

        if give_percentage:
            return (match_percentage >= match_threshold), match_percentage
        else:
            return (match_percentage >= match_threshold)

    def match(self, answer, correct_answer):
        print("checking:", answer)
        print("correct answers:", ", ".join(correct_answer.split(" && ")))
        for possible_answer in correct_answer.split(" && "):
            if self._match(answer, possible_answer):
                return True

        return False


def main():
    # GUI
    app = qg.QApplication(sys.argv)
    controller = Controller()
    app.exec_()

if __name__ == "__main__":
    main()
