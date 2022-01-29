from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qw
from PySide2 import QtGui as qg
import random

from functools import partial

import sys
import gui_utils as utils
import os.path
#import Test_v01 as content


def set_multiline_text(multiline_text, sentence_width, layout=None, reveal=100, capitalize=False):
    clear_layout(layout)

    sentence = ""
    for i, word in enumerate(multiline_text.split(" ")):
        if reveal < 100:
            if random.randint(0, 100) > reveal:
                word = len(word) * "."

        sentence += word + " "
        if len(sentence) >= sentence_width:
            sentence_label = utils.Label_custom(sentence)
            sentence_label.setFont(qg.QFont("Arial", 16))
            if capitalize and i == 0:
                sentence_label = sentence_label.capitalize()
            layout.addWidget(sentence_label)
            sentence = ""
        else:
            sentence = sentence.capitalize()

    sentence_label = utils.Label_custom(sentence)
    arial_font = qg.QFont("Arial", 16) 
    sentence_label.setFont(arial_font)
    layout.addWidget(sentence_label)

    return layout


def clear_layout(layout):
    for i in reversed(range(layout.count())):
        layout.itemAt(i).widget().setParent(None)


class TestGUI(qw.QDialog):

    green_style = "QLabel { background-color : green; color : white; }"
    orange_style = "QLabel { background-color : orange; color : black; }"
    arial_font = qg.QFont("Arial", 16) 
    sentence_width = 130
    closed = qc.Signal()

    def __init__(self, title="subject placeholder"):
        qw.QDialog.__init__(self)

        # window setup
        self.setWindowTitle("Test: {}".format(title))
        #self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(1400)
        
        # main layout
        self.mainLayout = qw.QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        # question tracker
        self.track_label = qw.QLabel("")
        self.track_label.setFont(qg.QFont("Arial", 12) )
        self.mainLayout.addWidget(self.track_label)

        # question widgets
        self.content_layout = qw.QVBoxLayout()
        self.question_layout = qw.QVBoxLayout()

        # textfield
        self.txtfield = qw.QLineEdit()
        self.txtfield.setFont(self.arial_font)
        self.resulttext = qw.QLabel("")
        self.resulttext.setFont(self.arial_font)
        self.spacer = qw.QLabel("")

        # correction layout
        self.correction_layout = qw.QVBoxLayout()

        # add to content layout
        self.content_layout.addLayout(self.question_layout)
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
        self.consider_correct_btn = utils.PushButton_custom('Answer was correct', 'Arial', 12, [60, 140, 60])
        self.button_layout.addWidget(self.check_button)
        self.button_layout.addWidget(self.consider_correct_btn)
        self.button_layout.addWidget(self.hint_button)
        self.button_layout.addWidget(self.skip_button)
        #self.button_layout.addWidget(self.mark_button)

        # add makePlayblast button to main layout
        self.mainLayout.addLayout(self.content_layout)
        self.mainLayout.addLayout(self.button_layout)

    def set_mode(self, mode):
        if mode == "question":
            self.check_button.setText("Check")
            self.enable_textfield(True)
            self.hint_button.setEnabled(True)
        else:
            self.check_button.setText("Next Question")
            self.enable_textfield(False)
            self.hint_button.setEnabled(False)

    def set_questiontext(self, questiontext, reveal=100):
        self.question_layout = set_multiline_text(questiontext, self.sentence_width, self.question_layout, reveal, capitalize=True)

    def set_correctiontext(self, correctiontext, reveal=100):
        correctiontext = correctiontext.split(" && ")[0]
        self.correction_layout = set_multiline_text(correctiontext, self.sentence_width, self.correction_layout, reveal, capitalize=True)

    def reset_textfields(self):
        self.check_button.setText("Check")
        self.txtfield.clear()
        self.txtfield.setFocus()
        self.resulttext.setText("")
        self.resulttext.setStyleSheet("")
        clear_layout(self.correction_layout)
        clear_layout(self.question_layout)

    def enable_textfield(self, lockstate):
        self.txtfield.setEnabled(lockstate)

    def replace_result(self, correct):
        if type(correct) is bool and correct:
            self.resulttext.setText("Correct!")
            self.resulttext.setStyleSheet(self.green_style)
        else:
            self.resulttext.setText("Incorrect.")
            self.resulttext.setStyleSheet(self.orange_style)

    def set_qtracker(self, total_questions, finished_questions):
        self.track_label.setText("{} / {}".format(finished_questions+1,
                                                  total_questions))

    def closeEvent(self, event=None):
        self.close()
        self.deleteLater()
        print('GUI closed.')
        self.closed.emit()

        

class StartMenu(qw.QDialog):

    green_style = "QLabel { background-color : green; color : white; }"
    orange_style = "QLabel { background-color : orange; color : black; }"
    arial_font = qg.QFont("Arial", 16)
    sentence_width = 100
    subject_changed = qc.Signal(int)

    def __init__(self, subjects, subject_index, title="subject placeholder"):
        qw.QDialog.__init__(self)

        # window setup
        self.setWindowTitle("Test {} - Start Menu.".format(title))
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(1200)
        
        # main layout
        self.mainLayout = qw.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.spacer = qw.QLabel("")

        # search term option
        self.search_layout = qw.QHBoxLayout()
        self.search_button = utils.PushButton_custom("Search", 'Arial', 12, [100, 140, 60])
        self.search_field = qw.QLineEdit()
        self.search_field.setFont(self.arial_font)
        self.search_layout.addWidget(self.search_field)
        self.search_layout.addWidget(self.search_button)
        self.search_result_layout = qw.QVBoxLayout()
        self.mainLayout.addLayout(self.search_result_layout)
        self.mainLayout.addLayout(self.search_layout)
        self.mainLayout.addWidget(self.spacer)

        # subject choice
        self.subject_announcer_text = qw.QLabel("Subject:")
        self.mainLayout.addWidget(self.subject_announcer_text)
        self.subject_buttons = []
        for i, subject in enumerate(subjects):
            subject_button = qw.QRadioButton(subject)
            self.subject_buttons.append(subject_button)
            subject_button.clicked.connect(partial(self.on_subj_button_clicked, i))
            self.mainLayout.addWidget(subject_button)

        # select one subject by default
        self.subject_buttons[subject_index].setChecked(True)
        self.mainLayout.addWidget(qw.QLabel(''))

        # question mode
        self.questionmode_label = qw.QLabel("Question mode:")
        self.questionmode_label.setFont(self.arial_font)
        self.questionmode_button = utils.PushButton_custom("Definition - Term", 
                                                           'Arial', 12, [60, 140, 60])

        self.mainLayout.addWidget(self.questionmode_label)
        self.mainLayout.addWidget(self.questionmode_button)
        self.mainLayout.addWidget(self.spacer)

        # parts selection
        self.instruction_label = qw.QLabel("Please select one of the following test parts:")
        self.instruction_label.setFont(self.arial_font)
        self.mainLayout.addWidget(self.instruction_label)

        # parts layout
        self.parts_layout = qw.QVBoxLayout()
        self.mainLayout.addLayout(self.parts_layout)

    def on_subj_button_clicked(self, subject_index):
        print("sending index", subject_index)
        self.subject_changed.emit(subject_index)

    def set_search_result(self, search_result):
        print(' search result:', search_result)
        set_multiline_text(search_result, self.sentence_width, self.search_result_layout, reveal=100)

    def update_search_field(self, search_term):
        self.search_field.setText(search_term)

    def add_parts_buttons(self, parts):
        clear_layout(self.parts_layout)
        horizontal_parts_amount = 5
        horizontal_layout = qw.QHBoxLayout()
        i = 1
        for part_name, part_info in parts.items():
            part_button = utils.PushButton_custom("{}\nsessions: {}".format(part_name, str(part_info)),
                                                  'Arial', 12, [40, 40, 40])

            horizontal_layout.addWidget(part_button)
            if i < horizontal_parts_amount:
                i += 1
            else:
                i = 1
                self.parts_layout.addLayout(horizontal_layout)
                horizontal_layout = qw.QHBoxLayout()

        if horizontal_layout.count() > 0:
            self.parts_layout.addLayout(horizontal_layout)



def main():
    gui = StartMenu(["Bedrijfsinformatiesystemen", "Aarde, mens en milieu 1"])
    gui.show()
    return gui

if __name__ == '__main__':
    app = qw.QApplication(sys.argv)
    gui = main()
    app.exec_()

