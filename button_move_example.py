from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

# import maya.OpenMayaUI as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds

EDIT_MODE = False


def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''

    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class PickerWidget(QtWidgets.QWidget):
    global EDIT_MODE

    def __init__(self, image_path, parent=None):
        super(PickerWidget, self).__init__(parent)

        self.setFixedSize(10000, 10000)
        self.move(-5000, -5000)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.internal_wdg = PickerBackgroundWidget(image_path, self)
        self.background_img_label = self.internal_wdg.get_image_widget()

        self.container_wdg = PickerButtonsContainerWidget(self)
        self.buttons_list = []

        self.move_enabled = True
        self.image_visibility = True
        self.mouse_right_click_pos = (0, 0)
        self.mouse_right_click_container_pos = (0, 0)
        self.scale = 1.0
        self.previous_scale = 1.0
        self.original_size = (self.width(), self.height())
        self.original_background_size = self.internal_wdg.get_size()
        self.original_image_size = self.background_img_label.get_size()

    def get_background_widget(self):
        return self.internal_wdg

    def get_container_widget(self):
        return self.container_wdg

    def get_scale(self):
        return self.scale

    def get_previous_scale(self):
        return self.previous_scale

    def set_image_visibility(self):
        if self.image_visibility:
            self.background_img_label.hide()
            self.image_visibility = False
        else:
            self.background_img_label.show()
            self.image_visibility = True

    def update_edit_mode(self):
        global EDIT_MODE
        if EDIT_MODE:
            for sel_btn in self.buttons_list:
                sel_btn.setMoveable(True)
        else:
            for sel_btn in self.buttons_list:
                sel_btn.setMoveable(False)

    def get_mouse_right_click_pos(self):
        return self.mouse_right_click_pos

    def get_mouse_right_click_container_pos(self):
        return self.mouse_right_click_container_pos

    def create_selection_button(self, x=0, y=0, size=(24, 24)):
        picker_btn = PickerSelectionButton(x=x, y=y,
                                           width=size[0], height=size[1],
                                           color=(150, 150, 255),
                                           text=None,
                                           picker_scale = self.scale,
                                           parent=self.container_wdg)
        picker_btn.show()
        picker_btn.activateWindow()
        picker_btn.raise_()

        self.buttons_list.append(picker_btn)

    def create_selection_button_on_point(self, size=(24, 24)):
        pkr_mouse_pos = self.get_mouse_right_click_container_pos()
        mid_size = ((size[0]*self.scale) / 2, (size[1]*self.scale) / 2)
        final_btn_pos = (pkr_mouse_pos[0] - mid_size[0], pkr_mouse_pos[1] - mid_size[1])
        self.create_selection_button(x=final_btn_pos[0], y=final_btn_pos[1])

    def updateButtonsScale(self, scale):
        for sel_btn in self.buttons_list:
            if self.scale != 1:
                # Scale Position
                pos_without_scale = sel_btn.get_base_position()
                rel_pos_without_scale = (pos_without_scale[0] - 5000, pos_without_scale[1] - 5000)
                rel_pos_scaled = (rel_pos_without_scale[0] * self.scale, rel_pos_without_scale[1] * self.scale)
                new_pos = (int(rel_pos_scaled[0]) + 5000, int(rel_pos_scaled[1]) + 5000)
                sel_btn.move(new_pos[0], new_pos[1])

                ### Modify Button Size ###
                btn_size = sel_btn.get_original_size()
                new_size = (btn_size[0] * scale, btn_size[1] * scale)
                sel_btn.setFixedSize(new_size[0], new_size[1])
            else:
                # Reset Position
                btn_base_pos = sel_btn.get_base_position()
                sel_btn.move(btn_base_pos[0], btn_base_pos[1])

                #Reset Size
                btn_size = sel_btn.get_original_size()
                sel_btn.setFixedSize(btn_size[0], btn_size[1])

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

    def wheelEvent(self, event):
        self.previous_scale = self.scale
        scale_wheel = self.scale + ((event.delta() / 120) / 10.0)
        if scale_wheel < 0.3:
            scale_wheel = 0.3

        self.scale = scale_wheel
        self.scale_pick()

    def scale_pick(self):
        new_image_size = (int(self.original_image_size[0] * self.scale),
                          int(self.original_image_size[1] * self.scale))

        # Scale Background image
        self.background_img_label.set_size(new_image_size[0], new_image_size[1])

        # Update Buttons
        self.updateButtonsScale(self.scale)


class PickerButtonsContainerWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(PickerButtonsContainerWidget, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedSize(10000, 10000)
        self.move(-5000, -5000)


class PickerBackgroundWidget(QtWidgets.QWidget):

    def __init__(self, image_path, parent=None):
        super(PickerBackgroundWidget, self).__init__(parent)

        self.width = 10000
        self.height = 10000

        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setFixedSize(self.width, self.height)

        self.image_path = image_path

        self.add_image_widget()

    def add_image_widget(self):
        self.picker_img_label = PickerImageWidget(None, None, self.image_path, self)

    def get_image_widget(self):
        return self.picker_img_label

    def get_size(self):
        return (self.width, self.height)

    def set_size(self, w, h):
        self.setFixedSize(w, h)


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

    def __init__(self, x, y, width, height, color, text, picker_scale=1, parent=None):
        super(PickerSelectionButton, self).__init__(parent)

        global EDIT_MODE

        if text:
            self.setText(text)

        self.picker_scale = picker_scale

        self.creation_pos = (x, y)
        self.move(x, y)

        self.base_position = self.calculate_scaled_position(self.creation_pos, self.picker_scale)

        self.size = (width, height)
        self.set_size()

        if color:
            self.setStyleSheet('background-color:rgb({},{},{})'.format(*color))

        self.move_enabled = EDIT_MODE

        self.selection_at_creation = cmds.ls(sl=True)

    def setMoveable(self, moveable):
        self.move_enabled = moveable

    def set_size(self):
        scaled_size = (self.size[0]*self.picker_scale, self.size[1]*self.picker_scale)

        self.setFixedSize(scaled_size[0], scaled_size[1])

    def calculate_scaled_position(self, position, scale):
        creation_pos_rel = (position[0] - 5000, position[1] - 5000)
        rel_pos_scaled = (creation_pos_rel[0]/scale, creation_pos_rel[1]/scale)
        final_pos = (rel_pos_scaled[0] + 5000, rel_pos_scaled[1] + 5000)

        return final_pos

    def getMoveable(self):
        return self.move_enabled

    def get_original_size(self):
        return self.size

    def get_base_position(self):
        return self.base_position

    def mousePressEvent(self, event):
        if self.move_enabled:
            if event.button() == QtCore.Qt.LeftButton:
                self.initial_pos = self.pos()
                self.global_pos = event.globalPos()
        else:
            self.select_elements()

    def mouseMoveEvent(self, event):
        if self.move_enabled:
            diff = event.globalPos() - self.global_pos
            final_pos = (self.initial_pos + diff)
            self.move(final_pos)

            picker_wdg = self.parent().parent()
            scale = picker_wdg.get_scale()
            self.base_position = self.calculate_scaled_position(self.pos().toTuple(), scale)

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

        self.mouse_picker_wdg_pos = (0, 0)

        self.picker_buttons = []

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
        shelf_group_box.setContentsMargins(0, 0, 0, 0)

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
        self.edit_mode_btn.clicked.connect(self.modify_edit_mode)
        self.create_btn.clicked.connect(self.pick_wdg.create_selection_button)
        self.img_btn.clicked.connect(self.pick_wdg.set_image_visibility)

        self.create_btn_action.triggered.connect(self.pick_wdg.create_selection_button_on_point)

    def picker_show_context_menu(self, point):
        context_menu = QtWidgets.QMenu()
        context_menu.addAction(self.create_btn_action)

        context_menu.exec_(self.pick_wdg.mapToGlobal(point))

    def modify_edit_mode(self):
        global EDIT_MODE

        if EDIT_MODE:
            self.edit_mode_btn.setChecked(False)
            EDIT_MODE = False

        else:
            self.edit_mode_btn.setChecked(True)
            EDIT_MODE = True

        print('Edit Mode: {}'.format(str(EDIT_MODE)))
        self.update_edit_mode()

    def update_edit_mode(self):
        self.pick_wdg.update_edit_mode()

    def showEvent(self, e):
        super(MouseEventExample, self).showEvent(e)

        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        global EDIT_MODE

        if isinstance(self, MouseEventExample):
            super(MouseEventExample, self).closeEvent(e)

            self.geometry = self.saveGeometry()

        EDIT_MODE = False
        self.update_edit_mode()


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
