from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qw
from PySide2 import QtGui as qg

import sys
import gui_utils as utils
import os.path
#import overhoorscript_v01 as content
        

class GUI(qw.QDialog):

    green_style = "QLabel { background-color : green; color : white; }"
    orange_style = "QLabel { background-color : orange; color : black; }"
    arial_font = qg.QFont("Arial", 16) 
    sentence_width = 130

    def __init__(self, title="subject placeholder"):
        qw.QDialog.__init__(self)

        # window setup
        self.setWindowTitle("Overhoorscript: {}".format(title))
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
        
        # main layout button
        self.check_button = utils.PushButton_custom('Check', 'SansSerif', 12, [60, 140, 60])
        
        # add makePlayblast button to main layout
        self.mainLayout.addLayout(self.content_layout)
        self.mainLayout.addWidget(self.check_button)

    def replace_question(self, question):
        print('question:', question)
        self.question.setText(question)

    def set_correctiontext(self, correctiontext):
        self.check_button.setText("Next Question")

        sentence = ""
        for word in correctiontext.split(" "):
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
        self.clear_layout(self.correction_layout)

    def enable_textfield(self, lockstate):
        self.txtfield.setEnabled(lockstate)

    def clear_layout(self, layout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

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
        del self

        print('GUI closed.')
        

def main():
    gui = GUI()
    gui.show()
    return gui

if __name__ == '__main__':
    app = qw.QApplication(sys.argv)
    gui = main()
    app.exec_()

