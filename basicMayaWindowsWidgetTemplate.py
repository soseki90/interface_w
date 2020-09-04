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


class TestWidget(QtWidgets.QWidget):
    dlg_instance = None

    WINDOW_TITLE = 'Widget Windows Template'

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = TestWidget()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(TestWidget, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWindowFlags(QtCore.Qt.WindowType.Window)
        self.setMinimumSize(500, 400)

        self.geometry = None

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        pass

    def create_layout(self):
        pass

    def create_connections(self):
        pass

    def showEvent(self, e):
        super(TestWidget, self).showEvent(e)

        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        if isinstance(self, TestWidget):
            super(TestWidget, self).closeEvent(e)

            self.geometry = self.saveGeometry()


if __name__ == '__main__':
    '''
    Only run when executes the code directly.
    '''

    try:
        test_widget.close()
        test_widget.deleteLater()
    except:
        pass

    test_widget = TestWidget()
    test_widget.show()