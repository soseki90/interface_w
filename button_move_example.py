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

        self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        self.origin = QtCore.QPoint()

        self.image_path = image_path
        self.edit_shelf = edit_shelf

        self.setFixedSize(10000, 10000)
        self.move(-5000, -5000)

        self.create_actions()
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.buttons_list = []
        self.buttons_in_selection_list = []

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
                sel_btn.set_moveable(True)
        else:
            for sel_btn in self.buttons_list:
                sel_btn.set_moveable(False)

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

            # Update picker scale info at button
            sel_btn.set_picker_scale(scale)

            # Scale Position
            sel_btn.update_scaled_position()

            # Scale Button Size
            btn_size = sel_btn.get_size()
            sel_btn.set_size(btn_size)

            # Scale Font
            btn_font_size = sel_btn.get_font_size()
            sel_btn.set_font_size(btn_font_size)

            # Scale border
            sel_btn.modify_style()

    def scale_pick(self):
        new_image_size = (int(self.original_image_size[0] * self.scale),
                          int(self.original_image_size[1] * self.scale))

        # Scale Background image
        self.background_img_label.set_size(new_image_size[0], new_image_size[1])

        # Update Buttons
        self.updateButtonsScale(self.scale)

    def convert_position_to_container(self, pos):
        container_moved = self.container_wdg.pos().toTuple()
        new_pos = (pos[0] - container_moved[0], pos[1] - container_moved[1])

        return new_pos

    def find_buttons_in_area(self, start_pos, end_pos):
        for btn in self.buttons_list:
            btn_pos = btn.pos().toTuple()
            if btn_pos[0] > start_pos[0] and btn_pos[0] < end_pos[0]:
                if btn_pos[1] > start_pos[1] and btn_pos[1] < end_pos[1]:
                    if btn not in self.buttons_in_selection_list:
                        self.buttons_in_selection_list.append(btn)
            elif btn_pos[0] < start_pos[0] and btn_pos[0] > end_pos[0]:
                if btn_pos[1] < start_pos[1] and btn_pos[1] > end_pos[1]:
                    if btn not in self.buttons_in_selection_list:
                        self.buttons_in_selection_list.append(btn)

    def select_buttons(self, buttons=None):
        if buttons:
            for btn in self.buttons_list:
                if btn in buttons:
                    btn.select_button(True)
                else:
                    btn.select_button(False)
        else:
            for btn in self.buttons_list:
                btn.select_button(False)


    def mousePressEvent(self, event):
        global EDIT_MODE
        pos = event.pos()
        self.global_pos = self.mapToGlobal(pos)
        if event.button() == QtCore.Qt.LeftButton:
            self.selection_origin = QtCore.QPoint(event.pos())
            self.selection_container_origin = self.convert_position_to_container(self.selection_origin.toTuple())
            self.rubberBand.setGeometry(QtCore.QRect(self.selection_origin, QtCore.QSize()))
            self.rubberBand.show()
            self.buttons_in_selection_list = []
            self.select_buttons()

        elif event.button() == QtCore.Qt.MiddleButton:
            self.move_enabled = True
            self.initial_internal_Wdg_pos = self.internal_wdg.pos()
            self.initial_container_wdg_pos = self.container_wdg.pos()
            self.global_pos = event.globalPos()

        elif event.button() == QtCore.Qt.RightButton:
            # PickerUI Position
            picker_pos = self.mapFromGlobal(self.global_pos)  # relative to window
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

        if event.button() == QtCore.Qt.LeftButton:
            self.rubberBand.hide()

    def mouseMoveEvent(self, event):
        if self.move_enabled:
            diff = event.globalPos() - self.global_pos
            self.internal_wdg.move(self.initial_internal_Wdg_pos + diff)
            self.container_wdg.move(self.initial_container_wdg_pos + diff)

        if not self.selection_origin.isNull():
            self.buttons_in_selection_list = []
            self.rubberBand.setGeometry(QtCore.QRect(self.selection_origin, event.pos()).normalized())
            selection_container_end = self.convert_position_to_container(event.pos().toTuple())
            self.find_buttons_in_area(start_pos = self.selection_container_origin,
                                      end_pos = selection_container_end)
            self.select_buttons(self.buttons_in_selection_list)

    def wheelEvent(self, event):
        self.previous_scale = self.scale
        scale_wheel = self.scale + ((event.delta() / 120) / 10.0)
        if scale_wheel < 0.3:
            scale_wheel = 0.3

        self.scale = scale_wheel
        self.scale_pick()

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

    def __init__(self, x, y, width, height, color, text, text_size=10, picker_scale=1, edit_shelf=None, parent=None):
        super(PickerSelectionButton, self).__init__(parent)

        global EDIT_MODE

        self.picker_scale = picker_scale
        self.edit_shelf = edit_shelf

        self.creation_pos = (x, y)
        self.move(x, y)

        self.base_position = self.calculate_scaled_position(self.creation_pos, self.picker_scale)

        self.size = (width, height)
        self.size_relation = float(height)/float(width)
        self.color = color
        self.border = 5
        self.hightlight_color = (self.color[0]+70, self.color[1]+70, self.color[2]+70)
        self.selected = False

        self.font_size = text_size
        self.font_color = (255, 255, 255)
        self.font_bold = False

        self.move_enabled = EDIT_MODE

        self.set_size()
        if self.color:
            self.set_color(self.color)
        if text:
            self.setText(text)
        self.set_font_size(text_size)
        self.set_font_color(self.font_color)
        self.set_font_bold(self.font_bold)

        self.selection_at_creation = cmds.ls(sl=True)

        self.clicked.connect(self.select_elements)

    def set_picker_scale(self, scale):
        self.picker_scale = scale

    def get_moveable(self):
        return self.move_enabled

    def set_moveable(self, moveable):
        self.move_enabled = moveable

    def get_base_position(self):
        return self.base_position

    def get_size(self):
        return self.size

    def set_size(self, size=None):
        if size:
            self.size = size

        scaled_size = (self.size[0]*self.picker_scale, self.size[1]*self.picker_scale)

        self.setFixedSize(scaled_size[0], scaled_size[1])
        self.modify_style()

    def update_size_relation(self):
        self.size_relation = float(self.size[1]) / float(self.size[0])

    def get_size_relation(self):
        return self.size_relation

    def get_color(self):
        return self.color

    def set_color(self, color=None):
        if color:
            self.color = color
        self.modify_style()

    def get_roundness(self):
        return self.border

    def set_roundness(self, roundness=None):
        if roundness:
            roundness = self.clamp_border(roundness)
            self.border = roundness
        self.modify_style()

    def clamp_border(self, border):
        min_size = self.size[0]
        if self.size[1] < min_size: min_size = self.size[1]
        clamp = (min_size/2)-1
        if border > clamp: border = clamp
        return border

    def modify_style(self, color=None, border=None):
        if color:
            self.color = color
        btn_color = 'background-color:rgb({},{},{});'.format(self.color[0], self.color[1], self.color[2])
        if self.hightlight_color[0] > 255: self.hightlight_color = (255, self.hightlight_color[1], self.hightlight_color[2])
        if self.hightlight_color[1] > 255: self.hightlight_color = (self.hightlight_color[0], 255, self.hightlight_color[2])
        if self.hightlight_color[2] > 255: self.hightlight_color = (self.hightlight_color[0], self.hightlight_color[1], 255)
        btn_hover_color = 'background-color:rgb({},{},{});'.format(*self.hightlight_color)
        btn_border = ' border: black 2px;'
        if border:
            border = self.clamp_border(border)
            self.border = border
        else:
            self.border = self.clamp_border(self.border)
        scaled_border = self.border*self.picker_scale
        btn_border_radius = ' border-radius: {}px;'.format(scaled_border)
        btn_border_style = ' border-style: outset;'
        btn_padding = ' padding: 5px;'

        btn_style = '{0}{1}{2}{3}{4}'.format(btn_color, btn_border, btn_border_radius, btn_border_style, btn_padding)
        btn_hover_style = '{0}{1}'.format(btn_hover_color, btn_border)
        btn_pressed = '{0}{1}'.format(btn_color, btn_border)
        final_btn_style = 'QPushButton{' + btn_style + '}  QPushButton:hover{' + btn_hover_style + '} QPushButton:pressed{' + btn_pressed + '}'
        self.setStyleSheet(final_btn_style)

    def update_scaled_position(self):
        if self.picker_scale != 1:
            rel_pos_without_scale = (self.base_position[0] - 5000, self.base_position[1] - 5000)
            rel_pos_scaled = (rel_pos_without_scale[0] * self.picker_scale, rel_pos_without_scale[1] * self.picker_scale)
            new_pos = (int(rel_pos_scaled[0]) + 5000, int(rel_pos_scaled[1]) + 5000)
            self.move(new_pos[0], new_pos[1])
        else:
            self.move(self.base_position[0], self.base_position[1])

    def calculate_scaled_position(self, position, scale):
        creation_pos_rel = (position[0] - 5000, position[1] - 5000)
        rel_pos_scaled = (creation_pos_rel[0]/scale, creation_pos_rel[1]/scale)
        final_pos = (rel_pos_scaled[0] + 5000, rel_pos_scaled[1] + 5000)

        return final_pos

    def get_text(self):
        return self.text()

    def set_text(self, text):
        if text:
            self.setText(text)
        else:
            self.setText('')

    def get_font_size(self):
        return self.font_size

    def set_font_size(self, size=None):
        if size:
            self.font_size = size
        else:
            self.font_size = 10

        scaled_size = self.font_size*self.picker_scale

        self.btn_font = self.font()
        self.btn_font.setPointSize(scaled_size)
        self.setFont(self.btn_font)

    def get_font_color(self):
        return self.font_color

    def set_font_color(self, color):
        btn_palette = QtGui.QPalette(self.palette())
        btn_font_color = QtGui.QColor()
        btn_font_color.setRgb(color[0], color[1], color[2])
        btn_palette.setColor(QtGui.QPalette.ButtonText, btn_font_color)
        self.setPalette(btn_palette)
        self.font_color = color

    def get_font_bold(self):
        return self.font_bold

    def set_font_bold(self, status):
        if status:
            self.font_bold = True
        else:
            self.font_bold = False
        self.btn_font = self.font()
        self.btn_font.setBold(self.font_bold)
        self.setFont(self.btn_font)

    def select_elements(self):
        print 'Button Pressed'
        if not self.move_enabled:
            cmds.select(self.selection_at_creation, r=True)

    def select_button(self, status):
        if status:
            original_color = self.color
            self.modify_style(color=self.hightlight_color)
            self.color = original_color
            self.selected = True
        else:
            self.modify_style()
            self.selected = False

    def mousePressEvent(self, event):
        if self.move_enabled:
            if event.button() == QtCore.Qt.LeftButton:
                self.initial_pos = self.pos()
                self.global_pos = event.globalPos()

            # Update Edit Mode Shelf
            self.edit_shelf.update_shelf(self)

        if event.button() == QtCore.Qt.LeftButton:
            print 'Button position: {}, {}'.format(*self.pos().toTuple())

    def mouseMoveEvent(self, event):
        if self.move_enabled:
            diff = event.globalPos() - self.global_pos
            final_pos = (self.initial_pos + diff)
            self.move(final_pos)

            picker_wdg = self.parent().parent()
            scale = picker_wdg.get_scale()
            self.base_position = self.calculate_scaled_position(self.pos().toTuple(), scale)

class PickerEditColorButton(QtWidgets.QWidget):

    color_changed = QtCore.Signal(tuple)

    def __init__(self, color=(255, 255, 255), parent=None):
        super(PickerEditColorButton, self).__init__(parent)

        self.setObjectName('PickerEditColorButton')

        self.create_control()

        self.set_size(68, 17)
        self.set_color(color)

    def create_control(self):
        #  Create the colorSliderGrp
        window = cmds.window()
        color_slider_name = cmds.colorSliderGrp()

        # Find the colorSliderGrp widget
        self._color_slider_obj = omui.MQtUtil.findControl(color_slider_name)
        if self._color_slider_obj:
            self._color_slider_widget = wrapInstance(long(self._color_slider_obj), QtWidgets.QWidget)

            # Reparent the colorSliderGrp widget to this widget
            main_layout = QtWidgets.QVBoxLayout(self)
            main_layout.setObjectName('main_layout')
            main_layout.setContentsMargins(0,0,0,0)
            main_layout.addWidget(self._color_slider_widget)

            # Identify/Store the colorSliderGrp's child widgets
            self._slider_widget = self._color_slider_widget.findChild(QtWidgets.QWidget, 'slider')
            if self._slider_widget:
                self._slider_widget.hide()
            self._color_widget = self._color_slider_widget.findChild(QtWidgets.QWidget, 'port')

            cmds.colorSliderGrp(self.get_full_name(), e=True, changeCommand=partial(self.on_color_changed))

        # Delete Mel Window
        cmds.deleteUI(window, window=True)

    def get_full_name(self):
        return omui.MQtUtil.fullName(long(self._color_slider_obj))

    def set_size(self, width, height):
        self._color_slider_widget.setFixedWidth(width)
        self._color_widget.setFixedHeight(height)

    def set_color(self, color):
        short_color = (color[0]/255.0, color[1]/255.0, color[2]/255.0)
        cmds.colorSliderGrp(self.get_full_name(), e=True, rgbValue=(short_color[0], short_color[1], short_color[2]))
        self.on_color_changed()

    def get_color(self):
        color = cmds.colorSliderGrp(self.get_full_name(), query=True, rgbValue=True)
        long_color = (int(color[0]*255), int(color[1]*255), int(color[2]*255))
        if long_color[0] > 255 or long_color[1] > 255 or long_color[2] > 255:
            long_color = (int(color[0]), int(color[1]), int(color[2]))
        return long_color

    def on_color_changed(self, *args):
        self.color_changed.emit(self.get_color())

class EditModeShelf(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super(EditModeShelf, self).__init__(parent)

        self.item = None

        self.setObjectName('shelfGroupBox')
        self.setStyleSheet('#shelfGroupBox {border: 1px solid #2e2e2e}')
        self.setFixedWidth(75)

        self.chain_icon = QtGui.QIcon(':UVTkRelationshipEditor.png')

        self.relation_size_status = False

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.edit_shelf_layout = QtWidgets.QVBoxLayout()

        self.edit_menu_label = QtWidgets.QLabel('EDIT MENU')
        self.edit_menu_label.setAlignment(QtCore.Qt.AlignCenter)

        self.text_title_label = QtWidgets.QLabel('TEXT')
        self.text_title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.text_label = QtWidgets.QLabel('Text:')
        self.text_line = QtWidgets.QLineEdit()
        self.font_size_label = QtWidgets.QLabel('Font Size:')
        self.font_size_spinb = QtWidgets.QSpinBox()
        self.font_size_spinb.setMinimum(1)
        self.font_size_spinb.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.font_bold_checkb = QtWidgets.QCheckBox('Bold')
        self.font_color_label = QtWidgets.QLabel('Font Color:')
        self.font_color_btn = PickerEditColorButton()

        self.size_label = QtWidgets.QLabel('BUTTON')
        self.size_label.setAlignment(QtCore.Qt.AlignCenter)
        self.width_label = QtWidgets.QLabel('Width:')
        self.width_spinb = QtWidgets.QSpinBox()
        self.width_spinb.setMinimum(1)
        self.width_spinb.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.height_label = QtWidgets.QLabel('Height:')
        self.height_spinb = QtWidgets.QSpinBox()
        self.height_spinb.setMinimum(1)
        self.height_spinb.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.size_relation_btn = QtWidgets.QPushButton()
        self.size_relation_btn.setFixedSize(20, 20)
        self.size_relation_btn.setIcon(self.chain_icon)
        self.size_relation_btn.setCheckable(True)
        self.roundness_label = QtWidgets.QLabel('Roundness:')
        self.roundness_spinb = QtWidgets.QSpinBox()
        self.roundness_spinb.setMinimum(0)
        self.roundness_spinb.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.btn_color_label = QtWidgets.QLabel('Button Color:')
        self.btn_color_btn = PickerEditColorButton()

    def create_layouts(self):
        self.edit_menu_shelf_wdg = QtWidgets.QWidget()
        self.edit_menu_shelf_wdg.setVisible(False)
        self.edit_shelf_layout = QtWidgets.QVBoxLayout()
        self.edit_menu_shelf_wdg.setLayout(self.edit_shelf_layout)
        self.edit_shelf_layout.setContentsMargins(2, 2, 2, 2)
        self.edit_shelf_layout.setAlignment(QtCore.Qt.AlignTop)

        self.edit_shelf_layout.addWidget(self.text_title_label)
        self.edit_shelf_layout.addWidget(self.text_label)
        self.edit_shelf_layout.addWidget(self.text_line)
        self.edit_shelf_layout.addWidget(self.font_size_label)
        self.edit_shelf_layout.addWidget(self.font_size_spinb)
        self.edit_shelf_layout.addWidget(self.font_bold_checkb)
        self.edit_shelf_layout.addWidget(self.font_color_label)
        self.edit_shelf_layout.addWidget(self.font_color_btn)

        self.edit_shelf_layout.addWidget(self.size_label)
        self.edit_shelf_layout.addWidget(self.width_label)
        self.edit_shelf_layout.addWidget(self.width_spinb)
        self.edit_shelf_layout.addWidget(self.height_label)
        self.edit_shelf_layout.addWidget(self.height_spinb)
        self.edit_shelf_layout.addWidget(self.size_relation_btn)
        self.edit_shelf_layout.addWidget(self.roundness_label)
        self.edit_shelf_layout.addWidget(self.roundness_spinb)
        self.edit_shelf_layout.addWidget(self.btn_color_label)
        self.edit_shelf_layout.addWidget(self.btn_color_btn)

        self.edit_shelf_main = QtWidgets.QVBoxLayout()
        self.setLayout(self.edit_shelf_main)
        self.edit_shelf_main.setContentsMargins(2, 2, 2, 2)
        self.edit_shelf_main.setAlignment(QtCore.Qt.AlignTop)
        self.edit_shelf_main.addWidget(self.edit_menu_label)
        self.edit_shelf_main.addWidget(self.edit_menu_shelf_wdg)


    def create_connections(self):
        pass

    def update_shelf(self, item):
        print ('Actualizando Shelf')
        if item:
            self.item = item

            self.edit_menu_shelf_wdg.setVisible(True)

            item_text_bold = self.item.get_font_bold()
            self.btn_text = self.item.text()
            self.text_line.blockSignals(True)
            self.text_line.setText(self.btn_text)
            self.text_line.blockSignals(False)
            self.btn_font_size = self.item.get_font_size()
            self.font_size_spinb.blockSignals(True)
            self.font_size_spinb.setValue(self.btn_font_size)
            self.font_size_spinb.blockSignals(False)
            self.font_bold_checkb.blockSignals(True)
            self.font_bold_checkb.setChecked(item_text_bold)
            self.font_bold_checkb.blockSignals(False)
            self.btn_font_color = self.item.get_font_color()
            self.font_color_btn.blockSignals(True)
            self.font_color_btn.set_color(self.btn_font_color)
            self.font_color_btn.blockSignals(False)

            item_width = self.item.width()
            item_height = self.item.height()
            item_roundness = self.item.get_roundness()
            self.width_spinb.blockSignals(True)
            self.width_spinb.setValue(item_width)
            self.width_spinb.blockSignals(False)
            self.height_spinb.blockSignals(True)
            self.height_spinb.setValue(item_height)
            self.height_spinb.blockSignals(False)
            self.size_relation_btn.setChecked(self.relation_size_status)
            self.roundness_spinb.blockSignals(True)
            self.roundness_spinb.setValue(item_roundness)
            self.roundness_spinb.blockSignals(False)
            self.btn_color = self.item.get_color()
            self.btn_color_btn.blockSignals(True)
            self.btn_color_btn.set_color(self.btn_color)
            self.btn_color_btn.blockSignals(False)

            self.text_line.textEdited.connect(self.modify_btn_text)
            self.font_size_spinb.valueChanged.connect(self.modify_btn_text_size)
            self.font_bold_checkb.stateChanged.connect(self.modify_btn_text_bold)
            self.font_color_btn.color_changed.connect(self.modify_btn_text_color)
            self.width_spinb.valueChanged.connect(self.modify_button_size)
            self.height_spinb.valueChanged.connect(self.modify_button_size)
            self.size_relation_btn.clicked.connect(self.modify_relation_size_status)
            self.roundness_spinb.valueChanged.connect(self.modify_button_roundness)
            self.btn_color_btn.color_changed.connect(self.modify_btn_color)

        else:
            self.edit_menu_shelf_wdg.setVisible(False)

    def modify_button_size(self):
        item_size = self.item.get_size()
        width_value = self.width_spinb.value()
        height_value = self.height_spinb.value()
        if not self.relation_size_status:
            self.item.set_size(size = (width_value, height_value))
            self.item.update_size_relation()
        else:
            size_relation = self.item.get_size_relation()
            height_value = int(width_value * size_relation)
            self.height_spinb.blockSignals(True)
            self.height_spinb.setValue(height_value)
            self.height_spinb.blockSignals(False)
            self.item.set_size(size=(width_value, height_value))
        self.modify_button_roundness()

    def modify_btn_text(self):
        self.btn_text = self.text_line.text()
        self.item.set_text(self.btn_text)

        self.modify_btn_text_size()

    def modify_btn_text_size(self):
        self.btn_font_size = self.font_size_spinb.value()
        self.item.set_font_size(self.btn_font_size)

    def modify_btn_text_color(self, new_color):
        self.item.set_font_color(new_color)

    def modify_btn_color(self, new_color):
        self.item.set_color(new_color)

    def modify_button_roundness(self):
        roundness_value = self.roundness_spinb.value()
        self.item.set_roundness(roundness_value)

    def modify_btn_text_bold(self, status):
        self.item.set_font_bold(status)

    def modify_relation_size_status(self):
        if self.relation_size_status:
            self.relation_size_status = False
            self.height_spinb.setEnabled(True)
            self.item.update_size_relation()

        else:
            self.relation_size_status = True
            self.height_spinb.setEnabled(False)
            self.item.update_size_relation()

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
