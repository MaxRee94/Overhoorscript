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
        
        # browse widgets
        self.question = utils.Label_custom('Wat is dit?')
        self.txtfield = qg.QLineEdit()
        
        # add to browsing layout
        self.mainLayout.addWidget(self.question)
        self.mainLayout.addWidget(self.txtfield)
        
        # main layout button
        self.makePlayblast_button = utils.PushButton_custom('Check', 'SansSerif', 12, [60, 140, 60])
        
        # add makePlayblast button to main layout
        self.mainLayout.addWidget(self.makePlayblast_button)

    def closeEvent(self, event=None):
        self.close()
        self.deleteLater()
        del self

        print('GUI closed.')


class Controller(qc.QObject):
    def __init__(self):
        qc.QObject.__init__(self)
        self.gui = GUI()

    def setup(self):
        self.connect_button()
        self.gui.show()

    def connect_button(self):
        self.gui.makePlayblast_button.clicked.connect(self.button_click_event)

    def button_click_event(self):
        answer = self.gui.txtfield.text()
        print('button clicked. input:', answer)
        

def main():
    controller = Controller()
    controller.setup()
    return controller

if __name__ == '__main__':
    app = qg.QApplication(sys.argv)
    controller = main()
    app.exec_()

