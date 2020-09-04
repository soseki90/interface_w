from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

#import maya.OpenMayaUI as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds


def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''

    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class PickerWidget(QtWidgets.QWidget):
    def __init__(self, image_path, parent=None):
        super(PickerWidget, self).__init__(parent)

        #self.image_path = image_path

        self.setFixedSize(10000, 10000)
        self.move(-5000, -5000)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.internal_wdg = PickerBackgroundWidget(image_path, self)
        self.background_img_label = self.internal_wdg.get_image_widget()

        self.container_wdg = PickerButtonsContainerWidget(self)

        self.move_enabled = False
        self.image_visibility = True
        self.mouse_right_click_pos = (0, 0)
        self.mouse_right_click_container_pos = (0,0)
        self.scale_wheel = 1.0
        self.original_size = (self.width(), self.height())
        self.original_image_size = self.background_img_label.get_size()

    def get_background_widget(self):
        return self.internal_wdg

    def get_container_widget(self):
        return self.container_wdg

    def set_image_visibility(self):
        if self.image_visibility:
            self.background_img_label.hide()
            self.image_visibility = False
        else:
            self.background_img_label.show()
            self.image_visibility = True

    def get_mouse_right_click_pos(self):
        return self.mouse_right_click_pos

    def get_mouse_right_click_container_pos(self):
        return self.mouse_right_click_container_pos

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.move_enabled = True
            self.initial_intetnal_wdg_pos = self.internal_wdg.pos()
            self.initial_container_wdg_pos = self.container_wdg.pos()
            self.global_pos = event.globalPos()

        elif event.button() == QtCore.Qt.RightButton:
            # Picker Position
            pos = event.pos()  # relative to widget
            global_pos = self.mapToGlobal(pos)  # relative to screen
            picker_pos = self.mapFromGlobal(global_pos)  # relative to window
            picker_pos = picker_pos.toTuple()
            self.mouse_right_click_pos = picker_pos

            # Container Position
            container_moved = self.container_wdg.pos().toTuple()
            # print ('El background se ha movido: {}'.format(str(container_moved)))
            # print ('Posicion en el widget: {}'.format(str(picker_pos)))
            # print (picker_pos[0] - container_moved[0], picker_pos[1] - container_moved[1])
            container_pos = (picker_pos[0] - container_moved[0], picker_pos[1] - container_moved[1])
            self.mouse_right_click_container_pos = container_pos

    def mouseReleaseEvent(self, event):
        if self.move_enabled:
            self.move_enabled = False

    def mouseMoveEvent(self, event):
        if self.move_enabled:
            diff = event.globalPos() - self.global_pos
            self.internal_wdg.move(self.initial_intetnal_wdg_pos + diff)
            self.container_wdg.move(self.initial_container_wdg_pos + diff)

    '''
    def wheelEvent(self, event):
        self.scale_wheel = self.scale_wheel + ((event.delta() / 120) / 10.0)

        new_image_size = (int(self.original_image_size[0] * self.scale_wheel),
                          int(self.original_image_size[1] * self.scale_wheel))

        # Scale Widget
        self.setFixedSize(new_image_size[0], new_image_size[1])

        # Scale Background image
        self.picker_img_label.set_size(new_image_size[0], new_image_size[1])
    '''

class PickerButtonsContainerWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(PickerButtonsContainerWidget, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedSize(10000, 10000)
        self.move(-5000, -5000)


class PickerBackgroundWidget(QtWidgets.QWidget):

    def __init__(self, image_path, parent=None):
        super(PickerBackgroundWidget, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setFixedSize(10000, 10000)

        self.image_path = image_path

        self.add_image_widget()

    def add_image_widget(self):
        self.picker_img_label = PickerImageWidget(None, None, self.image_path, self)

    def get_image_widget(self):
        return self.picker_img_label

class PickerImageWidget(QtWidgets.QLabel):

    def __init__(self, width, height, image_path, parent=None):
        super(PickerImageWidget, self).__init__(parent)

        self.set_image(image_path)
        self.set_background_color(QtCore.Qt.black)
        if width or height:
            self.set_size(width, height)

        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

    def set_size(self, width, height):
        self.setFixedSize(width, height)

    def get_size(self):
        return (self.width(), self.height())

    def set_image(self, image_path):
        image = QtGui.QImage(image_path)
        image = image.scaled(image.width(), image.height(), QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)

        self.pixmap = QtGui.QPixmap()
        self.pixmap.convertFromImage(image)
        self.set_size(self.pixmap.width(), self.pixmap.height())

    def set_background_color(self, color):
        self.background_color = color

        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        painter.fillRect(0, 0, self.width(), self.height(), self.background_color)
        painter.drawPixmap(self.rect(), self.pixmap)

class PickerSelectionButton(QtWidgets.QPushButton):

    def __init__(self, x, y, width, height, color, text, parent=None):
        super(PickerSelectionButton, self).__init__(parent)

        if text:
            self.setText(text)

        self.setFixedSize(width, height)
        self.move(x, y)

        if color:
            self.setStyleSheet('background-color:rgb({},{},{})'.format(*color))

        self.move_enabled = False

        self.selection_at_creation = cmds.ls(sl=True)

    def setMoveable(self, moveable):
        self.move_enabled = moveable

    def getMoveable(self):
        return self.move_enabled

    def mousePressEvent(self, mouse_event):
        if self.move_enabled:
            if mouse_event.button() == QtCore.Qt.LeftButton:
                self.initial_pos = self.pos()
                self.global_pos = mouse_event.globalPos()
        else:
            self.select_elements()

    def mouseMoveEvent(self, mouse_event):
        if self.move_enabled:
            print('Mouse Move')
            diff = mouse_event.globalPos() - self.global_pos
            self.move(self.initial_pos + diff)

    def select_elements(self):
        cmds.select(self.selection_at_creation, r=True)

class MouseEventExample(QtWidgets.QDialog):
    dlg_instance = None

    WINDOW_TITLE = 'Mouse Event Example'

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = MouseEventExample()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(MouseEventExample, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)
        self.setMinimumSize(200, 200)
        self.resize(750, 750)

        self.geometry = None

        self.mouse_picker_wdg_pos = (0,0)

        self.picker_buttons = []

        self.edit_mode_status = False

        self.picker_background_image_path = r"D:\Trabajo\Desarrollos\INTERFACE\picker_test\CHARS_kid_rig_picker_bck.JPG"

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        self.create_btn_action = QtWidgets.QAction('Create Button', self)

        self.display_shape_action = QtWidgets.QAction('Shapes', self)
        self.display_shape_action.setCheckable(True)
        self.display_shape_action.setChecked(True)
        self.display_shape_action.setShortcut(QtGui.QKeySequence('Ctrl+Shift+H'))

    def create_widgets(self):
        self.create_btn = QtWidgets.QPushButton('Create')
        self.create_btn.setFixedSize(33, 33)
        self.edit_mode_btn = QtWidgets.QPushButton('Edit')
        self.edit_mode_btn.setCheckable(True)
        self.edit_mode_btn.setFixedSize(33, 33)
        self.img_btn = QtWidgets.QPushButton('img')
        self.img_btn.setFixedSize(33, 33)

        self.pick_wdg = PickerWidget(self.picker_background_image_path, parent=None)
        self.pick_wdg.customContextMenuRequested.connect(self.picker_show_context_menu)
        self.pick_background_wdg = self.pick_wdg.get_background_widget()
        self.pick_container_wdg = self.pick_wdg.get_container_widget()

    def create_layout(self):
        shelf_group_box = QtWidgets.QGroupBox()
        shelf_group_box.setMaximumHeight(36)
        shelf_group_box.setContentsMargins(0,0,0,0)

        shelf_layout = QtWidgets.QHBoxLayout(shelf_group_box)
        shelf_layout.setContentsMargins(0, 0, 0, 0)
        shelf_layout.setAlignment(QtCore.Qt.AlignLeft)
        shelf_layout.addWidget(self.create_btn)
        shelf_layout.addWidget(self.edit_mode_btn)
        shelf_layout.addWidget(self.img_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(shelf_group_box)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.pick_wdg)

    def create_connections(self):
        self.edit_mode_btn.clicked.connect(self.edit_mode)
        self.create_btn.clicked.connect(self.create_picker_selection_button)
        self.img_btn.clicked.connect(self.pick_wdg.set_image_visibility)

        self.create_btn_action.triggered.connect(self.create_picker_selection_button_on_point)

    def picker_show_context_menu(self, point):
        context_menu = QtWidgets.QMenu()
        context_menu.addAction(self.create_btn_action)

        context_menu.exec_(self.pick_wdg.mapToGlobal(point))

    def create_picker_selection_button(self, x=0, y=0, size=(24, 24)):
        picker_btn = PickerSelectionButton(x=x, y=y,
                                 width=size[0], height=size[1],
                                 color=(150,150,255),
                                 text=None,
                                 parent=self.pick_container_wdg)
        picker_btn.show()
        picker_btn.activateWindow()
        picker_btn.raise_()

        self.picker_buttons.append(picker_btn)

    def create_picker_selection_button_on_point(self, size=(24, 24)):
        picker_internal_mouse_pos = self.pick_wdg.get_mouse_right_click_container_pos()
        mid_size = (size[0]/2, size[1]/2)
        final_button_pos = (picker_internal_mouse_pos[0] - mid_size[0], picker_internal_mouse_pos[1] - mid_size[1])
        self.create_picker_selection_button(x=final_button_pos[0], y=final_button_pos[1])

    def edit_mode(self, status=False):
        if not status:
            if self.edit_mode_status:
                self.edit_mode_btn.setChecked(False)
                self.edit_mode_status = False
                self.set_moveable()

            else:
                self.edit_mode_btn.setChecked(True)
                self.edit_mode_status = True
                self.set_moveable()
        else:
            self.edit_mode_btn.setChecked(False)
            self.edit_mode_status = False
            self.set_moveable()

    def set_moveable(self):
        for picker_btn in self.picker_buttons:
            if self.edit_mode_status:
                picker_btn.setMoveable(True)
            else:
                picker_btn.setMoveable(False)

    def showEvent(self, e):
        super(MouseEventExample, self).showEvent(e)

        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        if isinstance(self, MouseEventExample):
            super(MouseEventExample, self).closeEvent(e)

            self.geometry = self.saveGeometry()

        self.edit_mode(status=False)


if __name__ == '__main__':
    '''
    Only run when executes the code directly.
    '''

    try:
        test_dialog.close()
        test_dialog.deleteLater()
    except:
        pass

    test_dialog = MouseEventExample()
    test_dialog.show()