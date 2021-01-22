"""Controller"""
import sys
import random
import re

from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qg

import content, workio, window


class Controller(qc.QObject):

    def __init__(self, examinator):
        qc.QObject.__init__(self)
        self.gui = window.GUI("'Bedrijfsinformatiesystemen'")
        self.exam = examinator
        self.state = "question"

    def show_window(self):
        self.connect_button()
        self.gui.show()

    def connect_button(self):
        self.gui.check_button.clicked.connect(self.on_check_clicked)

    def on_check_clicked(self):
        if self.state == "question":
            # switch state to 'evaluation'
            self.state = "evaluation"
            answer = self.gui.txtfield.text()
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
            self.gui.enable_textfield(True)   
            self.gui.replace_question(self.exam.question)
            self.gui.reset_textfields()
        else:
            self.gui.enable_textfield(False)
            self.gui.set_correctiontext(self.exam.correct_answer)
            self.gui.replace_result(result)


class Examinator():

    def __init__(self):
        self.question = ""
        self.correct_answer = ""
        self.curriculum = {}
        self.questions = []
        self.minimum_answer = 3
        self.result = None
        self.match_threshold = 25.0

    def init_curriculum(self):
        self.curriculum = content.main()
        self.questions = self.get_questions(self.curriculum)
        workio.write_to_database(self.curriculum)

    def get_questions(self, curriculum, q_is_term=True):
        if q_is_term:
            return list(self.curriculum.keys())
        else:
            return list(self.curriculum.values())

    def eval(self, answer):
        print("-- Evaluating answer:", answer, "to question", 
              self.question)

        if self.match(answer, self.correct_answer):
            print("-- The answer was correct!")
            self.questions.remove(self.question)
            self.result = True
        else:
            print("-- Incorrect. The correct answer is:\n",
                  self.correct_answer)
            self.questions.append(self.question)
            self.result = False

    def update(self):
        self.question = self.questions[random.randint(
                            0, len(self.questions)-1)]

        self.correct_answer = self.curriculum[self.question]

    def match(self, answer, correct_answer):
        correct_answer = correct_answer.lower()
        answer = answer.lower()
        print("Your answer:", answer)

        word_matches = [word != "" and word in correct_answer.split(" ")
                        for word in answer.split(" ")]

        print("word matches:", word_matches)
        match_percentage = sum(word_matches) / len(word_matches) * 100.0
        print("match percentag:", match_percentage)

        return (match_percentage >= self.match_threshold 
                and len(word_matches) >= self.minimum_answer)


def main():
    # Examinator
    exam = Examinator()
    exam.init_curriculum()
    exam.update()

    # GUI
    app = qg.QApplication(sys.argv)
    controller = Controller(exam)
    controller.update_gui()
    controller.show_window()
    app.exec_()

if __name__ == "__main__":
    main()
