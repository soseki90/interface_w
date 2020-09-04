from functools import partial

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

class CustomColorButton(QtWidgets.QWidget):

    color_changed = QtCore.Signal(QtGui.QColor)

    def __init__(self, color=QtCore.Qt.white, parent=None):
        super(CustomColorButton, self).__init__(parent)

        self.setObjectName('CustomColorButton')

        self.create_control()

        self.set_size(50, 14)
        self.set_color(color)

    def create_control(self):
        ''' 1) Create the colorSliderGrp '''
        window = cmds.window()
        self._name = cmds.colorSliderGrp()

        ''' 2) Find the colorSliderGrp widget '''
        color_slider_obj = omui.MQtUtil.findControl(self._name)
        if color_slider_obj:
            self._color_slider_widget = wrapInstance(long(color_slider_obj), QtWidgets.QWidget)

            ''' 3) Reparent the colorSliderGrp widget to this widget '''
            main_layout = QtWidgets.QVBoxLayout(self)
            main_layout.setObjectName('main_layout')
            main_layout.setContentsMargins(0,0,0,0)
            main_layout.addWidget(self._color_slider_widget)

            ''' 4) Update the colorSliderGrp control name (used by Maya)'''
            self._name = omui.MQtUtil.fullName(long(color_slider_obj))

            ''' 5) Identify/Store the colorSliderGrp's child widgets (and hife if necessary) '''
            self._slider_widget = self._color_slider_widget.findChild(QtWidgets.QWidget, 'slider')
            if self._slider_widget:
                self._slider_widget.hide()
            self._color_widget = self._color_slider_widget.findChild(QtWidgets.QWidget, 'port')

            cmds.colorSliderGrp(self._name, e=True, changeCommand=partial(self.on_color_changed))


        ''' Delete Mel Window '''
        cmds.deleteUI(window, window=True)

    def set_size(self, width, height):
        self._color_slider_widget.setFixedWidth(width)
        self._color_widget.setFixedHeight(height)

    def set_color(self, color):
        color = QtGui.QColor(color)

        cmds.colorSliderGrp(self._name, e=True, rgbValue=(color.redF(), color.greenF(), color.blueF()))
        self.on_color_changed()

    def get_color(self):
        color = cmds.colorSliderGrp(self._color_slider_widget.objectName(), query=True, rgbValue=True)

        color = QtGui.QColor(color[0]*255, color[1]*255, color[2]*255)
        return color

    def on_color_changed(self, *args):
        self.color_changed.emit(self.get_color())


class CustomColorWdg(QtWidgets.QWidget):
    dlg_instance = None

    WINDOW_TITLE = 'Widget Windows Template'

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = CustomColorWdg()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(CustomColorWdg, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWindowFlags(QtCore.Qt.WindowType.Window)
        self.setMinimumSize(500, 400)

        self.geometry = None

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.foreground_color_btn = CustomColorButton(QtGui.QColor(QtCore.Qt.white))
        self.background_color_btn = CustomColorButton(QtGui.QColor(QtCore.Qt.black))

        self.print_btn = QtWidgets.QPushButton('Print')
        self.close_btn = QtWidgets.QPushButton('Close')

    def create_layout(self):
        color_layout = QtWidgets.QFormLayout()
        color_layout.addRow('Foreground:', self.foreground_color_btn)
        color_layout.addRow('Background:', self.background_color_btn)

        color_grp = QtWidgets.QGroupBox('Color Options')
        color_grp.setLayout(color_layout)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(2)
        button_layout.addStretch()
        button_layout.addWidget(self.print_btn)
        button_layout.addWidget(self.close_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.addWidget(color_grp)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.foreground_color_btn.color_changed.connect(self.on_foreground_color_changed)
        self.background_color_btn.color_changed.connect(self.on_background_color_changed)

        self.close_btn.clicked.connect(self.close)

    def on_foreground_color_changed(self, new_color):
        print('Foreground Color: [{}, {}, {}]'.format(new_color.red(),
                                                      new_color.green(),
                                                      new_color.blue()))

    def on_background_color_changed(self, new_color):
        print('Background Color: [{}, {}, {}]'.format(bg_color.red(),
                                                      bg_color.green(),
                                                      bg_color.blue()))

    def showEvent(self, e):
        super(CustomColorWdg, self).showEvent(e)

        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        if isinstance(self, CustomColorWdg):
            super(CustomColorWdg, self).closeEvent(e)

            self.geometry = self.saveGeometry()


if __name__ == '__main__':
    '''
    Only run when executes the code directly.
    '''

    try:
        custom_colot_wdg.close()
        custom_colot_wdg.deleteLater()
    except:
        pass

    custom_colot_wdg = CustomColorWdg()
    custom_colot_wdg.show()