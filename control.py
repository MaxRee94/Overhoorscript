"""Controller"""
import sys
import random

from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qg

import content, workio, window


class Controller(qc.QObject):

    def __init__(self, examinator):
        qc.QObject.__init__(self)
        self.gui = window.GUI()
        self.exam = examinator

    def show_window(self):
        self.connect_button()
        self.gui.show()

    def connect_button(self):
        self.gui.check_button.clicked.connect(self.on_check_clicked)

    def on_check_clicked(self):
        self.evaluate_answer()
        self.update_gui()

    def update_gui(self):
        print('-- Updating gui...\n')
        self.gui.replace_question(self.exam.question)
        self.gui.reset_textfield()

    def evaluate_answer(self):
        answer = self.gui.txtfield.text()
        result = self.exam.eval(answer)


class Examinator():

    def __init__(self):
        self.question = ""
        self.correct_answer = ""
        self.curriculum = {}
        self.questions = []

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
        print("-- Evaluating answer:", answer)

        if self.match(answer, self.correct_answer):
            print("-- The answer was correct!")
            self.questions.remove(self.question)
            result = True
        else:
            print("-- Incorrect. The correct answer is:\n",
                  self.correct_answer)
            self.questions.append(self.question)
            result = False

        self.update_exam()

        return result

    def update_exam(self):
        self.question = self.questions[random.randint(
                            0, len(self.questions)-1)]

        self.correct_answer = self.curriculum[self.question]

    def match(self, answer, definition):
        return answer == definition            


def main():
    # Examinator
    exam = Examinator()
    exam.init_curriculum()
    exam.update_exam()

    # GUI
    app = qg.QApplication(sys.argv)
    controller = Controller(exam)
    controller.update_gui()
    controller.show_window()
    app.exec_()

if __name__ == "__main__":
    main()
