import json

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QEvent, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QFrame

from gui.theme import read_qss_resource, get_icon_resource
from poster_ocr.gui.animation.shadow_effect import AnimationShadowEffect
from poster_ocr.gui.layout.flow_layout import FlowLayout
from poster_ocr.gui.util.excpetion import JsonDumpException, JsonLoadException

StyleSheet = read_qss_resource('FlowTagPaneQSS.qss')
StyleSheet_Hover = read_qss_resource('FlowTagPaneQSS_Hover.qss')
StyleSheet_Selected = read_qss_resource('FlowTagPaneQSS_Selected.qss')


class FlowTagPane(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FlowTagPane")

        self._layout = FlowLayout(self, 3, 2)

        self._flow_tag_dict = {}
        self._tag_selected_list = []

        self._setup_ui()

    def _setup_ui(self):
        self._layout.setSpacing(8)
        self.setContentsMargins(0, 8, 8, 8)
        self.setMinimumHeight(16)

        self.setStyleSheet(StyleSheet)

        pix_img = QtGui.QPixmap(QtGui.QImage(get_icon_resource("cancel.png")))
        self._delete_pixmap = pix_img.scaled(20, 20, transformMode=Qt.SmoothTransformation)

        """Shine"""
        self._animation_shadow = AnimationShadowEffect(Qt.yellow, loop_count=4)

    def add_new_tag(self, tag_text: str):
        if not self._flow_tag_dict.__contains__(tag_text):
            new_tag = FlowTag(self._delete_pixmap, tag_text, self)
            self._flow_tag_dict[tag_text] = new_tag
            self._layout.addWidget(new_tag)

            # Bind Signals
            new_tag.tag_need_deleting.connect(self._delete_flow_tag)
            new_tag.tag_selected.connect(self._select_flow_tag)

    def dump_all_tags(self) -> str:
        json_str = json.dumps(self._flow_tag_dict.keys(), indent=4)

        if json_str is None:
            raise JsonDumpException
        else:
            return json_str

    def load_all_tags(self, json_str: str):
        json_obj = json.loads(json_str)

        if isinstance(json_obj, list):
            for tag_text in json_obj:
                self.add_new_tag(tag_text)
        else:
            raise JsonLoadException

    def clear_all_tags(self):
        tag_text_list = self._flow_tag_dict.keys()

        for tag_text in list(tag_text_list):
            self._delete_flow_tag(tag_text)

        self._flow_tag_dict = {}
        self._tag_selected_list = []

    def _delete_flow_tag(self, tag_text: str):
        if self._flow_tag_dict.__contains__(tag_text):
            if tag_text in self._tag_selected_list:
                self._tag_selected_list.remove(tag_text)

            flow_tag = self._flow_tag_dict.pop(tag_text)
            self._layout.removeWidget(flow_tag)

    def _select_flow_tag(self, tag_text: str, is_selected: bool):
        if is_selected:
            if not self._tag_selected_list.__contains__(tag_text):
                self._tag_selected_list.append(tag_text)
        else:
            if self._tag_selected_list.__contains__(tag_text):
                self._tag_selected_list.remove(tag_text)

    def get_selected_tags(self) -> []:
        return self._tag_selected_list

    def shine(self):
        self.setGraphicsEffect(self._animation_shadow)
        self._animation_shadow.start()


class FlowTag(QWidget):
    tag_selected = pyqtSignal(str, bool)
    tag_need_deleting = pyqtSignal(str)

    def __init__(self, fit_pixmap: QPixmap, text="", parent=None):
        super().__init__(parent)
        self.setObjectName("FlowTag")

        self._tag_text = text
        self._is_selected = False

        self._is_to_delete = False

        self._label = TagLabel(self._tag_text, self)
        self._delete_button = QPushButton()

        self._setup_ui(fit_pixmap)
        self._bind_signal()

    def _setup_ui(self, fit_pixmap: QPixmap):
        delete_icon = QtGui.QIcon(fit_pixmap)
        self._delete_button.setIcon(delete_icon)

        self._layout = QHBoxLayout(self)
        self._layout.addStretch(0)
        self._layout.setContentsMargins(5, 5, 5, 5)
        self._layout.setSpacing(9)

        self._layout.addWidget(self._label)
        self._delete_button.hide()
        self._layout.addWidget(self._delete_button)

    def _bind_signal(self):
        self._delete_button.clicked.connect(self._delete_me)
        self._label.TagIsClicked.connect(self._tag_selected)

    def enterEvent(self, a0: QEvent) -> None:
        self.setStyleSheet(StyleSheet_Hover)
        self._delete_button.show()

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        if not self._is_selected:
            self.setStyleSheet(StyleSheet)
        else:
            self.setStyleSheet(StyleSheet_Selected)
        self._delete_button.hide()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._tag_selected()

    def _delete_me(self):
        self._is_to_delete = True
        self.tag_need_deleting.emit(self._tag_text)

    def _tag_selected(self):
        if self._is_selected:
            self._is_selected = False
            self.tag_selected.emit(self._tag_text, self._is_selected)
        else:
            self._is_selected = True
            self.tag_selected.emit(self._tag_text, self._is_selected)


class TagLabel(QLabel):
    """Custom Label with Mouse Click Event Signal
    """
    TagIsClicked = pyqtSignal()

    def __init__(self, text, parent):
        super(TagLabel, self).__init__(text, parent)
        self.setObjectName("TagLabel")
        self._is_pressed = False

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        self._is_pressed = True

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self._is_pressed:
            self.TagIsClicked.emit()
            self._is_pressed = False
