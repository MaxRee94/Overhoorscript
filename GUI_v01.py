# Easy Playblast tool
from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qg
from functools import partial

import sys
import gui_utils as utils
import os.path
        

class GUI(qg.QDialog):
    def __init__(self):
        qg.QDialog.__init__(self)
        
        # window setup
        self.setWindowTitle('Easy Playblast')
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(500)
        
        # main layout
        self.mainLayout = qg.QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        # browsing layout
        browse_layout = qg.QHBoxLayout()
        self.mainLayout.addLayout(browse_layout)
        
        # browse widgets
        browse_header = utils.Label_custom('File Name:')
        self.name_lineEdit = utils.LineEdit_custom()
        
        # add to browsing layout
        browse_layout.addWidget(browse_header)
        browse_layout.addWidget(self.name_lineEdit)
        
        # main layout button
        self.makePlayblast_button = utils.PushButton_custom('Playblast', 'SansSerif', 12, [60, 140, 60])
        
        # add makePlayblast button to main layout
        self.mainLayout.addWidget(self.makePlayblast_button)

    def closeEvent(self, event=None):
        self.close()
        self.deleteLater()
        del self

        print('easyPlayblast-GUI closed.')


class Controller(qc.QObject):
    def __init__(self):
        #window = qg.QWidget()
        qc.QObject.__init__(self)
        self.gui = GUI()

    def setup(self):
        self.connect_button()
        self.gui.show()

    def connect_button(self):
        self.gui.makePlayblast_button.clicked.connect(self.playblast_button_clicked)

    def playblast_button_clicked(self):
        print('button clicked')
        

def main():
    controller = Controller()
    controller.setup()
    return controller

if __name__ == '__main__':
    app = qg.QApplication(sys.argv)
    controller = main()
    app.exec_()

