from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qg

import sys
import gui_utils as utils
import os.path
#import overhoorscript_v01 as content
        

class GUI(qg.QDialog):
    def __init__(self):
        qg.QDialog.__init__(self)
        self.setWindowTitle('Overhoorscript')

        # window setup
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(500)
        
        # main layout
        self.mainLayout = qg.QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        # question widgets
        self.question = utils.Label_custom('')
        self.txtfield = qg.QLineEdit()
        
        # add to main layout
        self.mainLayout.addWidget(self.question)
        self.mainLayout.addWidget(self.txtfield)
        
        # main layout button
        self.check_button = utils.PushButton_custom('Check', 'SansSerif', 12, [60, 140, 60])
        
        # add makePlayblast button to main layout
        self.mainLayout.addWidget(self.check_button)

    def replace_question(self, question):
        print('question:', question)
        self.question.setText(question)

    def reset_textfield(self):
        self.txtfield.setText("")

    def closeEvent(self, event=None):
        self.close()
        self.deleteLater()
        del self

        print('GUI closed.')
        

def main():
    gui = GUI()
    return gui

if __name__ == '__main__':
    app = qg.QApplication(sys.argv)
    gui = main()
    app.exec_()

