"""Controller"""
import sys
import random
import re
from functools import partial

from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qg

import content, workio, window


class Controller(qc.QObject):

    title = "'Bedrijfsinformatiesystemen'"

    def __init__(self):
        qc.QObject.__init__(self)
        self.test_gui = window.TestGUI(self.title)
        self.start_menu = window.StartMenu(self.title)
        self.exam = Examinator()
        self.state = "question"
        self.difficulty = 50

    def show_startmenu(self):
        parts = self.exam.get_parts()
        self.start_menu.add_parts_buttons(parts)
        self.start_menu.show()

    def start_test(self, part_number):
        # delete start menu
        self.start_menu.deleteLater()
        del self.start_menu

        # init session-curriculum and test menu
        self.exam.init_curriculum(part_number)
        self.exam.update()
        self.update_gui()
        self.test_gui.show()

    def make_connections(self):
        # ---------------------------------------------- #
        # TEST UI
        # ---------------------------------------------- #
        self.test_gui.check_button.clicked.connect(self.on_check_clicked)
        self.test_gui.hint_button.clicked.connect(self.on_hint_clicked)

        # close event
        self.test_gui.closed.connect(self.exam.close)

        # ---------------------------------------------- #
        # STARTMENU UI
        # ---------------------------------------------- #
        # question mode
        self.start_menu.questionmode_button.clicked.connect(self.on_questionmode_clicked)

        # parts buttons
        parts_layout = self.start_menu.parts_layout
        rows_count = parts_layout.count()
        for i in range(rows_count):
            parts_row = parts_layout.itemAt(i).layout()
            for j in range(parts_row.count()):
                button = parts_row.itemAt(j).widget()
                button.clicked.connect(partial(self.start_test, i*rows_count+j+1))

    def on_questionmode_clicked(self):
        if self.exam.question_mode == "term":
            # switch questionmode to "definition"
            self.exam.question_mode = "definition"
            self.start_menu.questionmode_button.setText("Definition - Term")
        else:
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
            # switch state to 'evaluation'
            self.state = "evaluation"
            answer = self.test_gui.txtfield.text()
            self.exam.eval(answer)
            self.update_gui(self.exam.result)
        else:
            # switch state to 'question'
            self.state = "question"
            self.exam.update()
            self.update_gui()

    def update_gui(self, result=None):
        print('-- Updating gui...\n')

        if self.state == "question": 
            self.test_gui.set_qtracker(self.exam.total_question_count,
                                       len(self.exam.log.values()))
            self.test_gui.enable_textfield(True)  
            self.test_gui.reset_textfields() 
            self.test_gui.set_questiontext(self.exam.question)
        else:
            self.test_gui.enable_textfield(False)
            self.test_gui.set_correctiontext(self.exam.correct_answer)
            self.test_gui.replace_result(result)


class Examinator():

    def __init__(self):
        self.question = ""
        self.correct_answer = ""
        self.curriculum_total = {}
        self.curriculum_session = {}
        self.questions = []
        self.minimum_answer = 3
        self.result = None
        self.log = {}
        self.total_question_count = 0
        self.part_name = ""
        self.match_threshold = 70.0
        self.session = workio.Session()
        self.question_mode = "definition"
        self.init_curriculum()

    def init_curriculum(self, part_number=None):
        if part_number is None:
            self.curriculum_total = self.session.get_curriculum()
            return

        self.part_name = "Part {}".format(part_number)
        if self.question_mode == "term":
            self.curriculum_session = self.curriculum_total[self.part_name]
        else:
            self.curriculum_session = self.get_reversed_curriculum(self.curriculum_total[self.part_name])
        
        self.total_question_count = len(self.curriculum_session)
        self.questions = list(self.curriculum_session.keys())

    def get_reversed_curriculum(self, curriculum):
        reversed_curriculum = {}
        for term, definition in curriculum.items():
            reversed_curriculum[definition] = term

        return reversed_curriculum

    def close(self):
        log = {self.part_name: self.log}
        self.session.write_log(log)

    def update_log(self, log_key):
        if log_key in self.log.keys():
            self.log[log_key].append(self.question)
        else:
            self.log[log_key] = [self.question]

    def eval(self, answer):
        print("-- Evaluating answer:", answer, "to question", 
              self.question)

        self.total_question_count += 1

        if self.match(answer, self.correct_answer):
            print("-- The answer was correct!")
            self.questions.remove(self.question)
            self.result = True
            self.update_log("successes")
        else:
            print("-- Incorrect. The correct answer is:\n",
                  self.correct_answer)
            self.questions.append(self.question)
            self.result = False
            self.update_log("mistakes")

    def get_parts(self):
        return {part: self.session.get_part_info(part) for part in self.curriculum_total.keys()}

    def update(self):
        self.question = self.questions[random.randint(
                            0, len(self.questions)-1)]

        self.correct_answer = self.curriculum_session[self.question]

    def match(self, answer, correct_answer):
        correct_answer = correct_answer.lower()
        answer = answer.lower()
        print("Your answer:", answer)

        correct_words = [word for word in correct_answer.split(" ") if word]
        correct_words_without_spaces = [word.replace(" ", "") for word in correct_words]
        word_matches = [word != "" and (word in correct_words
                                        or word.replace(" ", "") in correct_words
                                        or word in correct_words_without_spaces)
                        for word in answer.split(" ")]

        print("Word matches:", word_matches)

        match_percentage = (sum(word_matches) / len(correct_words))  * 100.0
        print("Match percentage:", match_percentage)

        return (match_percentage >= self.match_threshold)


def main():
    # GUI
    app = qg.QApplication(sys.argv)
    controller = Controller()
    controller.update_gui()
    controller.show_startmenu()
    controller.make_connections()
    app.exec_()

if __name__ == "__main__":
    main()
