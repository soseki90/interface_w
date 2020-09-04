from PySide2 import QtWidgets

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import maya.cmds as cmds

class MyDockableButton(MayaQWidgetDockableMixin, QtWidgets.QPushButton):

    def __init__(self):
        super(MyDockableButton, self).__init__()

        self.setWindowTitle('Dockable Window')
        self.setText('My Button')
