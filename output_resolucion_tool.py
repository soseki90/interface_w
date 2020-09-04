from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMayaUI as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds

def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class OuputResolutionDialog(QtWidgets.QDialog):
    
    RESOLUTION_ITEMS = [
                        ['1920x1080 (1080p)', 1920.0, 1080.0],
                        ['1280x720 (720p)', 1280.0, 720.0],
                        ['960x540 (540p)', 960.0, 540.0],
                        ['640x480', 640.0, 480.0],
                        ['320x240', 320.0, 240.0],
                       ]
    
    def __init__(self, parent=maya_main_window()):
        super(OuputResolutionDialog, self).__init__(parent)

        self.setWindowTitle('Output Resolution')
        self.setMinimumWidth(200) 
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        
    def create_widgets(self):
        self.resolution_list_wdg = QtWidgets.QListWidget()
        for resolution_item in self.RESOLUTION_ITEMS:
            list_wdg_item = QtWidgets.QListWidgetItem(resolution_item[0])
            list_wdg_item.setData(QtCore.Qt.UserRole, [resolution_item[1], resolution_item[2]])
            self.resolution_list_wdg.addItem(list_wdg_item)
        
        self.close_btn = QtWidgets.QPushButton('Close')
        
    def create_layout(self):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2,2,2,2)
        main_layout.setSpacing(2)
        main_layout.addWidget(self.resolution_list_wdg)
        main_layout.addLayout(button_layout)
    
    def create_connections(self):
        self.resolution_list_wdg.itemClicked.connect(self.set_output_resolution)
        
        self.close_btn.clicked.connect(self.close)
    
    def set_output_resolution(self, item):
        resolution = item.data(QtCore.Qt.UserRole)
        
        print ('Resolution: {}'.format(resolution))
        
        cmds.setAttr('defaultResolution.width', resolution[0])
        cmds.setAttr('defaultResolution.height', resolution[1])
        cmds.setAttr('defaultResolution.deviceAspectRatio', resolution[0]/resolution[1])
        
if __name__ == '__main__':
    
    try:
        output_res_dlg.close()
        output_res_dlg.deleteLater()
    except:
        pass
    
    output_res_dlg = OuputResolutionDialog()
    output_res_dlg.show()