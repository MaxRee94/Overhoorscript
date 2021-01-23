from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qw
from PySide2 import QtGui as qg
import random

import sys
import gui_utils as utils
import os.path
#import Test_v01 as content


def clear_layout(layout):
    for i in reversed(range(layout.count())):
        layout.itemAt(i).widget().setParent(None)


class TestGUI(qw.QDialog):

    green_style = "QLabel { background-color : green; color : white; }"
    orange_style = "QLabel { background-color : orange; color : black; }"
    arial_font = qg.QFont("Arial", 16) 
    sentence_width = 130

    def __init__(self, title="subject placeholder"):
        qw.QDialog.__init__(self)

        # window setup
        self.setWindowTitle("Test: {}".format(title))
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(1400)
        
        # main layout
        self.mainLayout = qw.QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        # question widgets
        self.content_layout = qw.QVBoxLayout()
        self.question = qw.QLabel("")
        self.question.setFont(self.arial_font)
        self.txtfield = qw.QLineEdit()
        self.txtfield.setFont(self.arial_font)
        self.resulttext = qw.QLabel("")
        self.resulttext.setFont(self.arial_font)
        self.spacer = qw.QLabel("")
        self.sentence_label = None

        # correction layout
        self.correction_layout = qw.QVBoxLayout()

        # add to content layout
        self.content_layout.addWidget(self.question)
        self.content_layout.addWidget(self.txtfield)
        self.content_layout.addWidget(self.spacer)
        self.content_layout.addWidget(self.resulttext)
        self.content_layout.addWidget(self.spacer)
        self.content_layout.addLayout(self.correction_layout)
        self.content_layout.addWidget(self.spacer)
        
        # buttons
        self.button_layout = qw.QHBoxLayout()
        self.hint_button = utils.PushButton_custom('Hint', 'Arial', 12, [60, 140, 60])
        self.skip_button = utils.PushButton_custom('Skip - unimportant', 'Arial', 12, [60, 140, 60])
        self.check_button = utils.PushButton_custom('Check', 'Arial', 12, [60, 140, 60])
        self.mark_button = utils.PushButton_custom('Mark as important', 'Arial', 12, [60, 140, 60])
        self.button_layout.addWidget(self.check_button)
        self.button_layout.addWidget(self.hint_button)
        self.button_layout.addWidget(self.skip_button)
        self.button_layout.addWidget(self.mark_button)
        
        # add makePlayblast button to main layout
        self.mainLayout.addLayout(self.content_layout)
        self.mainLayout.addLayout(self.button_layout)

    def replace_question(self, question):
        print('question:', question)
        self.question.setText(question)

    def set_mode(self, mode):
        if mode == "question":
            self.check_button.setText("Next Question")
            self.gui.enable_textfield(True)
            self.hint_button.setEnabled(True)
        else:
            self.check_button.setText("Check")
            self.gui.enable_textfield(False)
            self.hint_button.setEnabled(False)

    def set_correctiontext(self, correctiontext, reveal=100):
        clear_layout(self.correction_layout)

        sentence = ""
        for word in correctiontext.split(" "):
            if reveal < 100:
                if random.randint(0, 100) > reveal:
                    word = len(word) * "."

            sentence += word + " "
            if len(sentence) >= self.sentence_width:
                self.sentence_label = utils.Label_custom(sentence)
                self.sentence_label.setFont(self.arial_font)
                self.correction_layout.addWidget(self.sentence_label)
                sentence = ""

        self.sentence_label = utils.Label_custom(sentence)
        self.sentence_label.setFont(self.arial_font)
        self.correction_layout.addWidget(self.sentence_label)

    def reset_textfields(self):
        self.check_button.setText("Check")
        self.txtfield.clear()
        self.txtfield.setFocus()
        self.resulttext.setText("")
        self.resulttext.setStyleSheet("")
        clear_layout(self.correction_layout)

    def enable_textfield(self, lockstate):
        self.txtfield.setEnabled(lockstate)

    def replace_result(self, correct):
        if type(correct) is bool and correct:
            self.resulttext.setText("Correct!")
            self.resulttext.setStyleSheet(self.green_style)
        else:
            self.resulttext.setText("Incorrect.")
            self.resulttext.setStyleSheet(self.orange_style)

    def closeEvent(self, event=None):
        self.close()
        self.deleteLater()

        print('GUI closed.')
        

class StartMenu(qw.QDialog):

    green_style = "QLabel { background-color : green; color : white; }"
    orange_style = "QLabel { background-color : orange; color : black; }"
    arial_font = qg.QFont("Arial", 16) 
    sentence_width = 130

    def __init__(self, title="subject placeholder"):
        qw.QDialog.__init__(self)

        # window setup
        self.setWindowTitle("Test {} - Start Menu.".format(title))
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(800)
        
        # main layout
        self.mainLayout = qw.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # labels
        self.instruction_label = qw.QLabel("Please select one of the following test parts:")
        self.instruction_label.setFont(self.arial_font)
        self.mainLayout.addWidget(self.instruction_label)

        # parts layout
        self.parts_layout = qw.QVBoxLayout()
        self.mainLayout.addLayout(self.parts_layout)

    def add_parts_buttons(self, parts):
        clear_layout(self.parts_layout)
        horizontal_parts_amount = 5
        horizontal_layout = qw.QHBoxLayout()
        i = 1
        print("parts:", parts)
        for part in parts:
            part_button = utils.PushButton_custom(
                part, 'Arial', 12, [40, 40, 40])
            if i < horizontal_parts_amount:
                horizontal_layout.addWidget(part_button)
                i += 1
            else:
                i = 1
                self.parts_layout.addLayout(horizontal_layout)
                horizontal_layout = qw.QHBoxLayout()



def main():
    gui = TestGUI()
    gui.show()
    return gui

if __name__ == '__main__':
    app = qw.QApplication(sys.argv)
    gui = main()
    app.exec_()

