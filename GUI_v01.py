# Easy Playblast tool
from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qg
from functools import partial

from maya import cmds
import pymel.core as pm
import maya.mel as mel
import sys
import gui_utils as max
import os.path


class Model():

    VIEWPORT_BLAST_SETTINGS = {'cams':0, 'nurbs':0, 'lights':0, 'grid':0, 'aa':1, 'displ_res':0, 'displ_gatemask':0, 'fieldchart':0, 'locators':0}
    MAINPANE = 'MainPane'

    def __init__(self):
        self.targetPath = None
        self.targetDirectory = None
        self.active_model_panel = None
        self.user_selection = None
        self.all_model_panels = None
        self.fieldchart = None

    def generate_default_name(self):
        # find correct disk name
        for diskName in ['E']:
            if os.path.exists(diskName + ':\\Dropbox\\resources'):
                break

        # find playblastDirectory
        scene_short_name = cmds.file(query = True, sceneName = True, shortName = True)
        scene_long_name = cmds.file(query = True, sceneName = True)

        if self.invalid_scene_name(scene_short_name):
            raise RuntimeError("Invalid scene name. This tool only works with scenes that have been saved as something other than 'untitled'.")

        targetDirectory = scene_long_name.replace(scene_short_name, '').replace('scenes', 'playblasts').replace('shots', 'playblasts')
        print 'playblast directory is: ', str(targetDirectory)
                
        # remove version suffix
        version_suffix_indicator = '_v'
        split_name = scene_short_name.split(version_suffix_indicator)
        del split_name[-1]
        glue_segment = ''
        default_playblastName = ''
        for name_segment in split_name:
            default_playblastName += '{0}{1}{2}'.format(default_playblastName, glue_segment, name_segment)
            glue_segment = version_suffix_indicator

        # find out what the newest existing playblast version is
        i = 1
        versionCount = '001'
        while os.path.exists(targetDirectory + default_playblastName + '_v' + versionCount + '.mov'):
            i += 1
            versionCount = str(i)
            while len(versionCount) < 3:
                versionCount = '0' + versionCount

        default_playblastName = default_playblastName + '_v' + versionCount

        return default_playblastName, targetDirectory

    def determine_targetPath(self, playblastName, playblast_dir):
        targetPath = playblast_dir + playblastName
        #if not targetPath.endswith('.mov'):
        	#targetPath = '{}.mov'.format(targetPath)

        print 'writing file to "{}"'.format(targetPath)

        return targetPath

    def save_model_panel_info(self):
        self.user_selection = cmds.ls(selection=True)
        self.active_model_panel = cmds.getPanel(withFocus=True)
        self.all_model_panels = cmds.getPanel(type='modelPanel')
        self.docked_model_panels = self.get_docked_panels()
        self.active_cam = pm.windows.modelPanel(self.active_model_panel, query=True, camera=True)
        print 'active model panel: "{}"'.format(self.active_model_panel)
        print 'active camera: "{}"'.format(self.active_cam)

        self.cams_vis = cmds.modelEditor(self.active_model_panel, query=True, cameras=True)
        self.nurbs_vis = cmds.modelEditor(self.active_model_panel, query=True, nurbsCurves=True)
        self.locator_vis = cmds.modelEditor(self.active_model_panel, query=True, locators=True)
        self.lights_vis = cmds.modelEditor(self.active_model_panel, query=True, lights=True)
        self.grid_vis = cmds.modelEditor(self.active_model_panel, query=True, grid=True)
        self.anti_alias = cmds.getAttr('hardwareRenderingGlobals.multiSampleEnable')
        self.displ_res = cmds.getAttr('{}.displayResolution'.format(self.active_cam))
        self.displ_gatemask = cmds.getAttr('{}.displayGateMask'.format(self.active_cam))
        self.fieldchart = cmds.getAttr('{}.displayFieldChart'.format(self.active_cam))
        print '- Cam visibility: {}'.format(str(self.cams_vis))
        print '- Nurbs visibility: {}'.format(str(self.nurbs_vis))
        print '- Lights visibility: {}'.format(str(self.lights_vis))
        print '- Grid visibility: {}'.format(str(self.lights_vis))
        print '- Anti-alias: {}'.format(str(self.anti_alias))

    def get_docked_panels(self):
        docked_panels = []
        for modelpanel in self.all_model_panels:
            model_parent = cmds.modelEditor(modelpanel, query=True, parent=True)
            if not model_parent:
                continue
            elif self.MAINPANE in model_parent:
                docked_panels.append(modelpanel)
        return docked_panels

    def update_model_panels(self):
        for docked_panel in self.docked_model_panels:
            mel.eval('updateModelPanelBar MainPane|viewPanes|{0}|{0}|modelEditorTabLayout|{0};'.format(docked_panel))
        mel.eval('updateModelPanelBar {0}Window|{0}|{0}|modelEditorTabLayout|{0};'.format(self.active_model_panel))

    def camera_gatemask_display(self, gatemask, res):
        cmds.setAttr('{}.displayGateMask'.format(self.active_cam), gatemask)
        if self.active_model_panel in self.docked_model_panels:
            print 'active panel recognized as docked.'
            mel.eval('modelPanelBarDecorationsCallback("ResolutionGateBtn", "MainPane|viewPanes|{0}|{0}|modelEditorTabLayout|{0}", "MainPane|viewPanes|{0}|{0}|modelEditorIconBar"); restoreLastPanelWithFocus(); updateModelPanelBar MainPane|viewPanes|{0}|{0}|modelEditorTabLayout|{0};'.format(self.active_model_panel))
        else:
            mel.eval('modelPanelBarDecorationsCallback("ResolutionGateBtn", "{0}Window|{0}|{0}|modelEditorTabLayout|{0}", "{0}Window|{0}|{0}|modelEditorIconBar"); restoreLastPanelWithFocus();'.format(self.active_model_panel))
        self.update_model_panels()

        cmds.setAttr('{}.displayResolution'.format(self.active_cam), res)
        self.update_model_panels()

    def apply_viewport_blast_settings(self):
        cmds.select(clear=True)
        cmds.modelEditor(self.active_model_panel, edit=True, cameras=self.VIEWPORT_BLAST_SETTINGS['cams'])
        cmds.modelEditor(self.active_model_panel, edit=True, nurbsCurves=self.VIEWPORT_BLAST_SETTINGS['nurbs'])
        cmds.modelEditor(self.active_model_panel, edit=True, lights=self.VIEWPORT_BLAST_SETTINGS['lights'])
        cmds.modelEditor(self.active_model_panel, edit=True, grid=self.VIEWPORT_BLAST_SETTINGS['grid'])
        cmds.modelEditor(self.active_model_panel, edit=True, locators=self.VIEWPORT_BLAST_SETTINGS['locators'])
        cmds.setAttr('hardwareRenderingGlobals.multiSampleEnable', self.VIEWPORT_BLAST_SETTINGS['aa'])
        cmds.setAttr('{}.displayFieldChart'.format(self.active_cam), self.VIEWPORT_BLAST_SETTINGS['fieldchart'])

        self.camera_gatemask_display(self.VIEWPORT_BLAST_SETTINGS['displ_gatemask'], self.VIEWPORT_BLAST_SETTINGS['displ_res'])
        self.camera_gatemask_display(self.VIEWPORT_BLAST_SETTINGS['displ_gatemask'], self.VIEWPORT_BLAST_SETTINGS['displ_res'])

        cmds.refresh(currentView=True, force=True)

    def reset_viewport(self):
        cmds.modelEditor(self.active_model_panel, edit=True, cameras=self.cams_vis)
        cmds.modelEditor(self.active_model_panel, edit=True, nurbsCurves=self.nurbs_vis)
        cmds.modelEditor(self.active_model_panel, edit=True, lights=self.lights_vis)
        cmds.modelEditor(self.active_model_panel, edit=True, grid=self.grid_vis)
        cmds.modelEditor(self.active_model_panel, edit=True, grid=self.grid_vis)
        cmds.modelEditor(self.active_model_panel, edit=True, grid=self.locator_vis)
        cmds.setAttr('hardwareRenderingGlobals.multiSampleEnable', self.anti_alias)
        cmds.setAttr('{}.displayFieldChart'.format(self.active_cam), self.fieldchart)
        
        self.camera_gatemask_display(self.displ_gatemask, self.displ_res)
        self.camera_gatemask_display(self.displ_gatemask, self.displ_res)

        cmds.select(self.user_selection)
        cmds.refresh(currentView=True, force=True)

    def prepare_viewport(self):
        print '-- Preparing viewport for playblast...'
        self.save_model_panel_info()
        self.apply_viewport_blast_settings()
        mel.eval('modelPanelBarDecorationsCallback("GateMaskBtn", "{0}Window|{0}|{0}|modelEditorTabLayout|{0}", "{0}Window|{0}|{0}|modelEditorIconBar"); restoreLastPanelWithFocus();'.format(self.active_model_panel))
        mel.eval('updateModelPanelBar {0}Window|{0}|{0}|modelEditorTabLayout|{0};'.format(self.active_model_panel))
        mel.eval('modelPanelBarDecorationsCallback("ResolutionGateBtn", "{0}Window|{0}|{0}|modelEditorTabLayout|{0}", "{0}Window|{0}|{0}|modelEditorIconBar"); restoreLastPanelWithFocus();'.format(self.active_model_panel))
        mel.eval('updateModelPanelBar {0}Window|{0}|{0}|modelEditorTabLayout|{0};'.format(self.active_model_panel))

    def create_playblast(self, playblastName, playblast_dir): 
        target_path = self.determine_targetPath(playblastName, playblast_dir)

        cmds.playblast(format = 'qt', widthHeight = [1920, 1080], viewer = False, filename = target_path, sequenceTime = 0, 
        clearCache = 1, showOrnaments = 1, fp = 4, percent = 100, compression = 'H.264', quality = 100, offScreen=True)

    def create_directory(self, playblast_dir):
        if not os.path.exists(playblast_dir):
            os.makedirs(playblast_dir)

    def invalid_scene_name(self, scene_short_name):
        if scene_short_name == '':
            return True
        

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
        browse_header = max.Label_custom('File Name:')
        self.name_lineEdit = max.LineEdit_custom()
        
        # add to browsing layout
        browse_layout.addWidget(browse_header)
        browse_layout.addWidget(self.name_lineEdit)
        
        # main layout button
        self.makePlayblast_button = max.PushButton_custom('Playblast', 'SansSerif', 12, [60, 140, 60])
        
        # add makePlayblast button to main layout
        self.mainLayout.addWidget(self.makePlayblast_button)

    def closeEvent(self, event=None):
        self.close()
        self.deleteLater()
        del self

        print 'easyPlayblast-GUI closed.'


class Controller(qc.QObject):
    def __init__(self):
        qc.QObject.__init__(self)
        self.model = Model()
        self.gui = GUI()
        self.playblast_dir = None

    def setup(self):
        self.setup_default_values()
        self.connect_button()
        self.gui.show()

    def setup_default_values(self):
        default_playblastName, self.playblast_dir = self.model.generate_default_name()
        self.model.create_directory(self.playblast_dir)
        self.gui.name_lineEdit.setText(default_playblastName)

    def connect_button(self):
        self.gui.makePlayblast_button.clicked.connect(self.playblast_button_clicked)

    def playblast_button_clicked(self):
        playblast_name = self.gui.name_lineEdit.text()
        self.gui.closeEvent()
        self.model.prepare_viewport()
        self.model.create_playblast(playblast_name, self.playblast_dir)
        self.model.reset_viewport() 
        print '-- Playblast Complete.'
        del self
        

def main():
    controller = Controller()
    controller.setup()
    return controller

if __name__ == '__main__':
    controller = main()

