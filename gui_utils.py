
from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qg
from PySide2 import QtGui as qtgui
import time

def minTime():
    return mc.playbackOptions(query=True,minTime=True)    

def maxTime():
    return mc.playbackOptions(query=True,maxTime=True)
  
def chanBox(object):
    mc.listAttr(object,k=True,o=True)
    
def sel():
    return mc.ls(sl=1)

"""
class errorPrompt(qg.QDialog):
    def __init__(self, inputText = '''An Error has occurred.
                 
                 Please try again''', inputTitle = 'Error'):
        promptID = 'prompt_ID'
        qg.QDialog.__init__(self)

        self.setWindowTitle(inputTitle)
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        
        self.setLayout(qg.QVBoxLayout())
        self.layout().setContentsMargins(5,5,5,5)
        self.layout().setSpacing(2)
        
        self.errorMessage = qg.QLabel(inputText)
        self.whiteSpace2 = qg.QLabel('')
        self.whiteSpace = qg.QLabel('')
        self.OK_button = qg.QPushButton('OK')
        self.layout().addWidget(self.whiteSpace)
        self.layout().addWidget(self.errorMessage)
        self.layout().addWidget(self.whiteSpace2)
        self.layout().addWidget(self.OK_button)
        
        self.OK_button.clicked.connect(lambda*_:self.close())
"""        

def windowExist(ui_title):
    if mc.window(ui_title, query=True, exists=True):
        mc.deleteUI(ui_title)

def column():
    mc.columnLayout(adjustableColumn = True)

def shortScene():
    return mc.file(query=1,sceneName=1,shortName=1)

def longScene():
    return mc.file(query=1,sceneName=1)

def keyTimeList(attribute,beginTime,endTime):
    return mc.keyframe(attribute, time=(beginTime,endTime), query=True, timeChange=True)

def queryScrollerSelect(name):
    return mc.textScrollList(name,query=True,selectItem=True)

def keyValueList(attribute,beginTime,endTime):
    return mc.keyframe(attribute, time=(beginTime,endTime), query=True, valueChange=True) 

def txtFieldButton(ID,fieldText):
    if fieldText=='sel':
        fieldText=mc.ls(sl=1)
        if not fieldText==[]:
            fieldText=fieldText[0]
        else:
            fieldText=''
    if fieldText=='selList':
        list_1=mc.ls(sl=1)
        fieldText=list_1[0]
        for i in range(len(list_1)-1):
            fieldText+=', '+list_1[i+1] 
    mc.textFieldButtonGrp(ID,edit=True,text=fieldText)

    
def commaList(list_1):
    var=''
    var=list_1[0]
    for i in range(len(list_1)-1):
        var+=', '+list_1[i+1] 
    return var

def window(ID,title,width,height):
    mc.window(ID, title = title, width = width, height = height, 
              menuBar = True, mbv = True)
    
def createFluidContainer():
    mel.eval('dynExecFluidEmitterCommands 1 { "1", "fluidEmitter -pos 0 0 0 -type omni -der 1 -her 1 -fer 1 -fdr 2 -r 100.0 -cye none -cyi 1 -mxd 1 -mnd 0 ", 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 0, 0, 1} ;')
    sel = mc.ls(sl=1)
    children = mc.listRelatives(sel)
    for child in children:
        nodeType = mc.nodeType(child)
        if nodeType == 'fluidEmitter':
            mc.delete(child)

    mel.eval('string $array[] = `ls -sl`;')
    mel.eval('string $fluidShape = $array[0]')
    mel.eval('setAttr ($fluidShape + ".fuelMethod") 2;')
    mel.eval('setAttr ($fluidShape + ".temperatureMethod") 2;')
    mel.eval('setAttr ($fluidShape + ".boundaryX") 0;')
    mel.eval('setAttr ($fluidShape + ".boundaryY") 0;')
    mel.eval('setAttr ($fluidShape + ".boundaryZ") 0;')
    mel.eval('setAttr ($fluidShape + ".autoResize") 1;')
    mel.eval('setAttr ($fluidShape + ".resizeToEmitter") 0;')
    mel.eval('setAttr ($fluidShape + ".resizeClosedBoundaries") 0;')
    mel.eval('setAttr ($fluidShape + ".baseResolution") 40;')
    mel.eval('setAttr ($fluidShape + ".autoResizeMargin") 1;')
    mel.eval('setAttr ($fluidShape + ".voxelQuality") 2;')
    mel.eval('setAttr ($fluidShape + ".boundaryDraw") 4;')
    
def createFluidContainer_inclEmitter():
    mel.eval('dynExecFluidEmitterCommands 1 { "1", "fluidEmitter -pos 0 0 0 -type omni -der 1 -her 1 -fer 1 -fdr 2 -r 100.0 -cye none -cyi 1 -mxd 1 -mnd 0 ", 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 0, 0, 1} ;')

    mel.eval('string $array[] = `ls -sl`;')
    mel.eval('string $fluidShape = $array[0]')
    mel.eval('setAttr ($fluidShape + ".fuelMethod") 2;')
    mel.eval('setAttr ($fluidShape + ".temperatureMethod") 2;')
    mel.eval('setAttr ($fluidShape + ".boundaryX") 0;')
    mel.eval('setAttr ($fluidShape + ".boundaryY") 0;')
    mel.eval('setAttr ($fluidShape + ".boundaryZ") 0;')
    mel.eval('setAttr ($fluidShape + ".autoResize") 1;')
    mel.eval('setAttr ($fluidShape + ".resizeToEmitter") 0;')
    mel.eval('setAttr ($fluidShape + ".resizeClosedBoundaries") 0;')
    mel.eval('setAttr ($fluidShape + ".baseResolution") 40;')
    mel.eval('setAttr ($fluidShape + ".autoResizeMargin") 1;')
    mel.eval('setAttr ($fluidShape + ".voxelQuality") 2;')
    mel.eval('setAttr ($fluidShape + ".boundaryDraw") 4;')

    fluidContainer = mc.ls(sl = True)[0]
    children = mc.listRelatives(children = True)
    for child in children:
        if mc.objectType(child, isType = 'fluidEmitter'):
            fluidEmitter = child
    return [fluidContainer, fluidEmitter]

def create_nParticleEmitter():
    #get fluid container name and delete fluid emitter
    fluidContainer = mc.ls(sl = True)[0]
    children = mc.listRelatives(fluidContainer, children = True)
    for child in children:
        if mc.objectType(child, isType = 'fluidEmitter'):
            mc.delete(child)

    #create emitter
    mel.eval('emitter -pos 0 0 0 -type omni -r 100 -sro 0 -nuv 0 -cye none -cyi 1 -spd 1 -srn 0 -nsp 1 -tsp 0 -mxd 0 -mnd 0 -dx 1 -dy 0 -dz 0 -sp 0 ;')
    emitterName = mc.ls(sl = True)[0]
    mc.setAttr(''.join([emitterName, '.emitterType']), 4)

    #create particle
    mel.eval('nParticle;')
    particleName = mc.ls(sl = True)[0]

    #connect particle to emitter
    mel.eval(''.join(['connectDynamic -em ', emitterName, ' ', particleName, ';']))

    #create new fluid emitter
    mel.eval('fluidEmitter -type surface -der 1 -her 1 -fer 1 -fdr 2 -r 100.0 -cye none -cyi 1 -mxd 1 -mnd 0 ;')
    fluidEmitter_new = mc.ls(sl = True)[0]

    #link new fluid emitter to fluid container
    mel.eval(''.join(['connectDynamic -em ', fluidEmitter_new, ' ', fluidContainer, ';'])) 

    return[emitterName, particleName, fluidEmitter_new, fluidContainer]
    

class Label_custom(qg.QLabel):
    def __init__(self, contents = '', font = 'SansSerif', size = 12):
        qg.QLabel.__init__(self)
        
        self.setText(contents)
        self.setFont(qtgui.QFont(font, size))


class Widget_custom(qg.QWidget):
    def __init__(self, rgb = [20, 20, 20]):
        qg.QWidget.__init__(self)
        
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        palette = self.palette()
        color = qtgui.QColor()
        color.setRgb(r,g,b)
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)


class PushButton_custom(qg.QPushButton):
    def __init__(self, contents = '', font = 'SansSerif', size = 12, rgb = [90, 90, 90]):
        qg.QPushButton.__init__(self)

        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        palette = self.palette()
        color = qtgui.QColor()
        color.setRgb(r,g,b)
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)
        self.setText(contents)
        self.setFont(qtgui.QFont(font, size))


class LineEdit_custom(qg.QLineEdit):
    def __init__(self, contents = '', font = 'SansSerif', size = 12,
                 rgb = [170, 170, 170]):
        qg.QLineEdit.__init__(self)

        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        palette = self.palette()
        color = qtgui.QColor()
        color.setRgb(r,g,b)
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)
        self.setText(contents)
        self.setFont(qtgui.QFont(font, size))


class HBoxLayout(qg.QHBoxLayout):
    def __init__(self, contentsMargins = [2,2,2,2], rgb = [40, 40, 40]):
        qg.QHBoxLayout.__init__(self)

        margin_1 = contentsMargins[0]
        margin_2 = contentsMargins[1]
        margin_3 = contentsMargins[2]
        margin_4 = contentsMargins[3]
        self.setContentsMargins(margin_1, margin_2, margin_3, margin_4)


class VBoxLayout(qg.QVBoxLayout):
    def __init__(self, contentsMargins = [2,2,2,2]):
        qg.QVBoxLayout.__init__(self)

        margin_1 = contentsMargins[0]
        margin_2 = contentsMargins[1]
        margin_3 = contentsMargins[2]
        margin_4 = contentsMargins[3]
        self.setContentsMargins(margin_1, margin_2, margin_3, margin_4)

        
class RadioButton_custom(qg.QRadioButton):
    def __init__(self, contents = '', font = 'SansSerif', size = 12):
        qg.QRadioButton.__init__(self)
        
        self.setText(contents)
        self.setFont(qtgui.QFont(font, size))
        

class CheckBox_custom(qg.QCheckBox):
    def __init__(self, contents = '', font = 'SansSerif', size = 12):
        qg.QCheckBox.__init__(self)
        
        self.setText(contents)
        self.setFont(qtgui.QFont(font, size))
        

class Splitter(qg.QWidget):      
    def __init__(self, lineWidth = 2):
        qg.QWidget.__init__(self)
        
        self.setMinimumHeight(6)
        self.setLayout(qg.QHBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignVCenter)
        
        main_line = qg.QFrame()
        main_line.setFrameStyle(qg.QFrame.HLine)
        main_line.setLineWidth(lineWidth)
        self.layout().addWidget(main_line)
    
    
    
    
    
