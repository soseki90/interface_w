from functools import partial

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

    def __init__(self, image_path, edit_shelf, parent=None):
        super(PickerWidget, self).__init__(parent)

        self.image_path = image_path
        self.edit_shelf = edit_shelf

        self.setFixedSize(10000, 10000)
        self.move(-5000, -5000)

        self.create_actions()
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

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

        self.pixmap = QtGui.QPixmap()
        self.background_color = QtCore.Qt.darkGray

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def create_actions(self):
        self.create_btn_action = QtWidgets.QAction('Create Button', self)

    def create_widgets(self):
        self.internal_wdg = PickerBackgroundWidget(self.image_path, self)
        self.background_img_label = self.internal_wdg.get_image_widget()

        self.container_wdg = PickerButtonsContainerWidget(self)

    def create_layouts(self):
        pass

    def create_connections(self):
        self.create_btn_action.triggered.connect(self.create_selection_button_on_point)

    def show_context_menu(self, point):
        context_menu = QtWidgets.QMenu()
        if EDIT_MODE:
            context_menu.addAction(self.create_btn_action)

        context_menu.exec_(self.mapToGlobal(point))

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

    def create_selection_button(self, x=5000, y=5000, size=(24, 24)):
        picker_btn = PickerSelectionButton(x=x, y=y,
                                           width=size[0], height=size[1],
                                           color=(150, 150, 255),
                                           text=None,
                                           picker_scale = self.scale,
                                           edit_shelf = self.edit_shelf,
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
        global EDIT_MODE

        if event.button() == QtCore.Qt.MiddleButton:
            self.move_enabled = True
            self.initial_intetnal_wdg_pos = self.internal_wdg.pos()
            self.initial_container_wdg_pos = self.container_wdg.pos()
            self.global_pos = event.globalPos()

        elif event.button() == QtCore.Qt.RightButton:
            # PickerUI Position
            pos = event.pos()  # relative to widget
            global_pos = self.mapToGlobal(pos)  # relative to screen
            picker_pos = self.mapFromGlobal(global_pos)  # relative to window
            picker_pos = picker_pos.toTuple()
            self.mouse_right_click_pos = picker_pos

            # Container Position
            container_moved = self.container_wdg.pos().toTuple()
            container_pos = (picker_pos[0] - container_moved[0], picker_pos[1] - container_moved[1])
            self.mouse_right_click_container_pos = container_pos

        elif event.button() == QtCore.Qt.LeftButton:
            if EDIT_MODE == True:
                self.edit_shelf.update_shelf(item=None)

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

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(0, 0, 10000, 10000, self.background_color)
        painter.drawPixmap(self.rect(), self.pixmap)

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

    def __init__(self, x, y, width, height, color, text, picker_scale=1, edit_shelf=None, parent=None):
        super(PickerSelectionButton, self).__init__(parent)

        global EDIT_MODE

        if text:
            self.setText(text)

        self.picker_scale = picker_scale
        self.edit_shelf = edit_shelf

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

    def set_size(self, size=None):
        if size:
            self.size = size

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

            # Update Edit Mode Shelf
            self.edit_shelf.update_shelf(self)

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

class EditModeShelf(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super(EditModeShelf, self).__init__(parent)

        self.item = None

        self.setObjectName('shelfGroupBox')
        self.setStyleSheet('#shelfGroupBox {border: 1px solid #2e2e2e}')
        self.setFixedWidth(75)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.edit_shelf_layout = QtWidgets.QVBoxLayout()

        self.edit_menu_label = QtWidgets.QLabel('EDIT MENU')
        self.edit_menu_label.setAlignment(QtCore.Qt.AlignCenter)

        self.text_title_label = QtWidgets.QLabel('TEXT')
        self.text_title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.text_title_label.setVisible(False)
        self.text_label = QtWidgets.QLabel('Text')
        self.text_label.setVisible(False)
        self.text_line = QtWidgets.QLineEdit()
        self.text_line.setVisible(False)
        self.font_size_label = QtWidgets.QLabel('Font Size')
        self.font_size_label.setVisible(False)
        self.font_size_spinb = QtWidgets.QSpinBox()
        self.font_size_spinb.setMinimum(1)
        self.font_size_spinb.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.font_size_spinb.setVisible(False)

        self.size_label = QtWidgets.QLabel('SIZE')
        self.size_label.setAlignment(QtCore.Qt.AlignCenter)
        self.size_label.setVisible(False)
        self.width_label = QtWidgets.QLabel('Width')
        self.width_label.setVisible(False)
        self.width_spinb = QtWidgets.QSpinBox()
        self.width_spinb.setMinimum(1)
        self.width_spinb.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.width_spinb.setVisible(False)
        self.height_label = QtWidgets.QLabel('Height')
        self.height_label.setVisible(False)
        self.height_spinb = QtWidgets.QSpinBox()
        self.height_spinb.setMinimum(1)
        self.height_spinb.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.height_spinb.setVisible(False)

    def create_layouts(self):
        self.edit_shelf_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.edit_shelf_layout)
        self.edit_shelf_layout.setContentsMargins(2, 2, 2, 2)
        self.edit_shelf_layout.setAlignment(QtCore.Qt.AlignTop)
        self.edit_shelf_layout.addWidget(self.edit_menu_label)

        self.edit_shelf_layout.addWidget(self.text_title_label)
        self.edit_shelf_layout.addWidget(self.text_label)
        self.edit_shelf_layout.addWidget(self.text_line)
        self.edit_shelf_layout.addWidget(self.font_size_label)
        self.edit_shelf_layout.addWidget(self.font_size_spinb)

        self.edit_shelf_layout.addWidget(self.size_label)
        self.edit_shelf_layout.addWidget(self.width_label)
        self.edit_shelf_layout.addWidget(self.width_spinb)
        self.edit_shelf_layout.addWidget(self.height_label)
        self.edit_shelf_layout.addWidget(self.height_spinb)

    def create_connections(self):
        pass

    def update_shelf(self, item):
        print ('Actualizando Shelf')
        if item:
            self.item = item

            self.text_title_label.setVisible(True)
            self.text_label.setVisible(True)
            self.text_line.setVisible(True)
            self.font_size_label.setVisible(True)
            self.font_size_spinb.setVisible(True)

            self.size_label.setVisible(True)
            self.width_label.setVisible(True)
            self.width_spinb.setVisible(True)
            self.height_label.setVisible(True)
            self.height_spinb.setVisible(True)

            self.btn_text = self.item.text()
            self.text_line.setText(self.btn_text)
            self.btn_font = self.item.font()
            self.btn_font_size = self.btn_font.pointSize()
            self.font_size_spinb.setValue(self.btn_font_size)

            item_width = self.item.width()
            item_height = self.item.height()
            self.width_spinb.setValue(item_width)
            self.height_spinb.setValue(item_height)

            self.text_line.editingFinished.connect(self.modify_btn_text)
            self.font_size_spinb.valueChanged.connect(self.modify_btn_text_size)
            self.width_spinb.valueChanged.connect(self.modify_button_size)
            self.height_spinb.valueChanged.connect(self.modify_button_size)

        else:
            self.text_title_label.setVisible(False)
            self.text_label.setVisible(False)
            self.text_line.setVisible(False)
            self.font_size_label.setVisible(False)
            self.font_size_spinb.setVisible(False)

            self.size_label.setVisible(False)
            self.width_label.setVisible(False)
            self.width_spinb.setVisible(False)
            self.height_label.setVisible(False)
            self.height_spinb.setVisible(False)

    def modify_button_size(self):
        width_value = self.width_spinb.value()
        height_value = self.height_spinb.value()
        self.item.set_size(size = (width_value, height_value))

    def modify_btn_text(self):
        self.btn_text = self.text_line.text()
        self.item.setText(self.btn_text)

        self.btn_font = self.item.font()
        self.btn_font_size = self.btn_font.pointSize()
        if self.btn_font_size == -1:
            self.btn_font_size = 10
            self.btn_font.setPointSize(self.btn_font_size)
        self.font_size_spinb.setValue(self.btn_font_size)

    def modify_btn_text_size(self):
        self.btn_font_size = self.font_size_spinb.value()
        self.btn_font = self.item.font()
        self.btn_font.setPointSize(self.btn_font_size)
        self.item.setFont(self.btn_font)

class PickerUI(QtWidgets.QDialog):
    dlg_instance = None

    WINDOW_TITLE = 'PickerUI'

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = PickerUI()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(PickerUI, self).__init__(parent)

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
        self.menu_create_new_picker = QtWidgets.QAction('Create New PickerUI', self)

        self.menu_create_btn_action = QtWidgets.QAction('Create Button', self)
        self.menu_edit_mode_action = QtWidgets.QAction('Edit Mode', self)
        self.menu_edit_mode_action.setCheckable(True)
        self.menu_edit_mode_action.setChecked(False)

    def create_widgets(self):
        self.menu_bar = QtWidgets.QMenuBar()
        file_menu = self.menu_bar.addMenu('File')
        file_menu.addAction(self.menu_create_new_picker)
        edit_menu = self.menu_bar.addMenu('Edit')
        edit_menu.addAction(self.menu_create_btn_action)
        edit_menu.addAction(self.menu_edit_mode_action)

        self.edit_shelf_wdg = EditModeShelf()

        self.pickers_tab_wdg = QtWidgets.QTabWidget()
        self.pickers_tab_wdg.setObjectName('PickerUIsTabW')
        self.pickers_tab_wdg.setStyleSheet('#PickerUIsTabW {background-color:  #383838}')
        self.pickers_tab_wdg.setTabsClosable(True)
        self.pickers_tab_wdg.setMovable(True)

    def create_layout(self):
        picker_layout = QtWidgets.QHBoxLayout()
        picker_layout.setContentsMargins(0, 0, 0, 0)
        picker_layout.addWidget(self.edit_shelf_wdg)
        picker_layout.setSpacing(2)
        picker_layout.addWidget(self.pickers_tab_wdg)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(0)
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addLayout(picker_layout)

    def create_connections(self):
        self.menu_create_new_picker.triggered.connect(self.create_picker_tab)

        self.menu_edit_mode_action.triggered.connect(self.modify_edit_mode)

        self.pickers_tab_wdg.tabCloseRequested.connect(self.close_picker_tab)

    def create_picker_tab(self):
        # Create tab and picker wdg
        pick_wdg = PickerWidget(self.picker_background_image_path, edit_shelf = self.edit_shelf_wdg,  parent=None)
        index = self.pickers_tab_wdg.addTab(pick_wdg, 'New picker')

        # Select new tab
        self.pickers_tab_wdg.setCurrentIndex(index)

    def close_picker_tab(self, index):
        picker_wdg = self.pickers_tab_wdg.widget(index)
        if picker_wdg is not None:
            picker_wdg.deleteLater()
        self.pickers_tab_wdg.removeTab(index)

    def modify_edit_mode(self):
        global EDIT_MODE
        if EDIT_MODE:
            self.change_edit_mode_status(status=False)
        else:
            self.change_edit_mode_status(status=True)

    def change_edit_mode_status(self, status):
        global EDIT_MODE

        if status == True:
            EDIT_MODE = True

            # Modify Menu CheckBox Status
            self.menu_edit_mode_action.blockSignals(True)
            self.menu_edit_mode_action.setChecked(True)
            self.menu_edit_mode_action.blockSignals(False)

            # Show edit shelf
            self.edit_shelf_wdg.setVisible(True)

        elif status == False:
            EDIT_MODE = False

            # Modify Menu CheckBox Status
            self.menu_edit_mode_action.blockSignals(True)
            self.menu_edit_mode_action.setChecked(False)
            self.menu_edit_mode_action.blockSignals(False)

            # Hide edit shelf
            self.edit_shelf_wdg.setVisible(False)

        # Update moveable status at picker buttons
        picker_tabs_num = self.pickers_tab_wdg.count()
        for i in range(picker_tabs_num):
            picker_wdg = self.pickers_tab_wdg.widget(i)
            picker_wdg.update_edit_mode()

        print('Edit Mode: {}'.format(str(EDIT_MODE)))

    def get_edit_shelf(self):
        return self.edit_shelf_wdg

    def showEvent(self, e):
        super(PickerUI, self).showEvent(e)

        if self.geometry:
            self.restoreGeometry(self.geometry)

        self.change_edit_mode_status(status=False)

    def closeEvent(self, e):
        global EDIT_MODE

        if isinstance(self, PickerUI):
            super(PickerUI, self).closeEvent(e)

            self.geometry = self.saveGeometry()

        self.change_edit_mode_status(status=False)

if __name__ == '__main__':
    '''
    Only run when executes the code directly.
    '''

    try:
        test_dialog.close()
        test_dialog.deleteLater()
    except:
        pass

    test_dialog = PickerUI()
    test_dialog.show()
