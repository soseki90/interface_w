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

class LabelsWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(LabelsWidget, self).__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel('Label 01'))
        layout.addWidget(QtWidgets.QLabel('Label 02'))
        layout.addWidget(QtWidgets.QLabel('Label 03'))
        layout.addWidget(QtWidgets.QLabel('Label 04'))


class ButtonsWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(ButtonsWidget, self).__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QPushButton('Button 01'))
        layout.addWidget(QtWidgets.QPushButton('Button 02'))
        layout.addWidget(QtWidgets.QPushButton('Button 03'))
        layout.addWidget(QtWidgets.QPushButton('Button 04'))

class OthersWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(OthersWidget, self).__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel('Label'))
        layout.addWidget(QtWidgets.QPushButton('Button'))
        layout.addWidget(QtWidgets.QCheckBox('Check Box'))
        layout.addWidget(QtWidgets.QLineEdit())

class CustomTabWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(CustomTabWidget, self).__init__(parent)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.tab_bar = QtWidgets.QTabBar()
        self.tab_bar.setObjectName('CustomTabBar')
        self.tab_bar.setStyleSheet('#CustomTabBar {background-color:  #383838}')

        self.stacked_wdg = QtWidgets.QStackedWidget()
        self.stacked_wdg.setObjectName('tabBarStackedWidget')
        self.stacked_wdg.setStyleSheet('#tabBarStackedWidget {border: 1px solid #2e2e2e}')

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.tab_bar)
        main_layout.addWidget(self.stacked_wdg)

    def create_connections(self):
        self.tab_bar.currentChanged.connect(self.stacked_wdg.setCurrentIndex)

    def addTab(self, widget, label):
        self.tab_bar.addTab(label)

        self.stacked_wdg.addWidget(widget)

class TabBarDialog(QtWidgets.QDialog):
    dlg_instance = None

    WINDOW_TITLE = 'Tab bar example.'

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = TabBarDialog()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(TabBarDialog, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)
        self.setMinimumSize(200, 200)

        self.geometry = None

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.labels_wdg = LabelsWidget()
        self.buttons_wdg = ButtonsWidget()
        self.other_wdg = OthersWidget()

        self.tab_widget = CustomTabWidget()
        self.tab_widget.addTab(self.labels_wdg, 'Labels')
        self.tab_widget.addTab(self.buttons_wdg, 'Buttons')
        self.tab_widget.addTab(self.other_wdg, 'Others')

    def create_layout(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tab_widget)
        #layout.addStretch()

    def create_connections(self):
        pass

    def showEvent(self, e):
        super(TabBarDialog, self).showEvent(e)

        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        if isinstance(self, TabBarDialog):
            super(TabBarDialog, self).closeEvent(e)

            self.geometry = self.saveGeometry()


if __name__ == '__main__':
    '''
    Only run when executes the code directly.
    '''

    try:
        tab_bar_dialog.close()
        tab_bar_dialog.deleteLater()
    except:
        pass

    tab_bar_dialog = TabBarDialog()
    tab_bar_dialog.show()