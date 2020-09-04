from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import time

import maya.OpenMayaUI as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds


def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''

    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class ProgressBarDialog(QtWidgets.QDialog):
    dlg_instance = None

    WINDOW_TITLE = 'Dialog Template'

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = ProgressBarDialog()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(ProgressBarDialog, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)
        self.setMinimumSize(300, 120)

        self.geometry = None

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.progress_bar_button = QtWidgets.QPushButton('Run')

    def create_layout(self):
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.progress_bar_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)

    def create_connections(self):
        self.progress_bar_button.clicked.connect(self.run_progress_test)

    def run_progress_test(self):
        number_of_operations = 10

        progress_dialog = QtWidgets.QProgressDialog('Waiting to process...', 'Cancel', 0, number_of_operations, self)
        progress_dialog.setWindowTitle('Progess...')
        progress_dialog.setValue(0)
        progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        progress_dialog.show()

        QtCore.QCoreApplication.processEvents()

        for i in range(1, number_of_operations + 1):
            if progress_dialog.wasCanceled():
                break

            progress_dialog.setLabelText('Processing operation: {} (of {})'.format(i, number_of_operations))
            progress_dialog.setValue(i)
            time.sleep(0.5)

            QtCore.QCoreApplication.processEvents()

        progress_dialog.close()

    def showEvent(self, e):
        super(ProgressBarDialog, self).showEvent(e)

        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        if isinstance(self, ProgressBarDialog):
            super(ProgressBarDialog, self).closeEvent(e)

            self.geometry = self.saveGeometry()


if __name__ == '__main__':
    '''
    Only run when executes the code directly.
    '''

    try:
        progressbar_dialog.close()
        progressbar_dialog.deleteLater()
    except:
        pass

    progressbar_dialog = ProgressBarDialog()
    progressbar_dialog.show()