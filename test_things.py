from PySide2 import QtCore
from PySide2 import QtGui
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

class CustomImageWidget(QtWidgets.QLabel):

    def __init__(self, width, height, image_path, parent=None):
        super(CustomImageWidget, self).__init__(parent)

        self.set_size(width, height)
        self.set_image(image_path)
        self.set_background_color(QtCore.Qt.black)

    def set_size(self, width, height):
        self.setFixedSize(width, height)

    def set_image(self, image_path):
        image = QtGui.QImage(image_path)
        image = image.scaled(self.width(), self.height(), QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)

        self.pixmap = QtGui.QPixmap()
        self.pixmap.convertFromImage(image)

    def set_background_color(self, color):
        self.background_color = color

        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        painter.fillRect(0, 0, self.width(), self.height(), self.background_color)
        painter.drawPixmap(self.rect(), self.pixmap)


class TestThings(QtWidgets.QDialog):
    dlg_instance = None

    WINDOW_TITLE = 'Dialog Template'

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = TestThings()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(TestThings, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)
        self.setMinimumSize(500, 400)

        self.geometry = None

        self.picker_background_image_path = r"D:\Trabajo\Desarrollos\INTERFACE\picker_test\CHARS_kid_rig_picker_bck.JPG"

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.pick_wdg = QtWidgets.QWidget()

        self.picker_img_label = CustomImageWidget(1000, 1000, self.picker_background_image_path, parent=self.pick_wdg)



    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(self.pick_wdg)

    def create_connections(self):
        pass

    def showEvent(self, e):
        super(TestThings, self).showEvent(e)

        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        if isinstance(self, TestThings):
            super(TestThings, self).closeEvent(e)

            self.geometry = self.saveGeometry()


if __name__ == '__main__':
    '''
    Only run when executes the code directly.
    '''

    try:
        test_dialog.close()
        test_dialog.deleteLater()
    except:
        pass

    test_dialog = TestThings()
    test_dialog.show()