from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QEvent, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

import json

from poster_ocr.gui.layout.flow_layout import FlowLayout
from poster_ocr.gui.util.excpetion import JsonDumpException, JsonLoadException


class FlowTagPane(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._layout = FlowLayout(self, 3, 2)

        self._flow_tag_dict = {}
        self._tag_selected_list = []

    def _setup_ui(self):
        self.setLayout(self._layout)

    def add_new_tag(self, tag_text: str):
        if not self._flow_tag_dict.__contains__(tag_text):
            new_tag = FlowTag(tag_text, self)
            self._flow_tag_dict[tag_text] = new_tag
            self._layout.addWidget(new_tag)

            # Bind Signals
            new_tag.tag_need_deleting(str).connect(self._delete_flow_tag)
            new_tag.tag_selected(str, bool).connect(self._select_flow_tag)

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

        for tag_text in tag_text_list:
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


class FlowTag(QWidget):
    tag_selected = pyqtSignal(str, bool)
    tag_need_deleting = pyqtSignal(str)

    def __init__(self, text="", parent=None):
        super().__init__(parent)

        self._tag_text = text
        self._is_selected = False

        self.setWindowTitle('TerminalDemo')
        with open('../../qss/FlowTagPaneQSS.qss', 'r') as f:
            self._style_sheet = f.read()
        self.setStyleSheet(self._style_sheet)

        self._label = QLabel(self._tag_text, self)
        self._delete_button = QPushButton()

        self._setup_ui()
        self._bind_signal()

    def _setup_ui(self):
        pix_img = QtGui.QPixmap(QtGui.QImage(r'../../icon/cancel.png'))
        fit_pixmap = pix_img.scaled(36, 36, QtCore.Qt.IgnoreAction, QtCore.Qt.SmoothTransformation)
        delete_icon = QtGui.QIcon(fit_pixmap)
        self._delete_button.setIcon(delete_icon)

        self._layout = QVBoxLayout()
        self._layout.addStretch(0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._layout.addWidget(self._label)
        self._delete_button.hide()
        self._layout.addWidget(self._delete_button)

        self.setLayout(self._label)

    def _bind_signal(self):
        self._delete_button.clicked.connect(self._delete_me)
        self.setMouseTracking(True)

    def enterEvent(self, a0: QEvent) -> None:
        if not self._is_selected:
            self.setStyleSheet("""
                        {
                            border:10px;
                            background: rgb(39, 41, 42);
                            dashed #242424;
                        }
                        """)
        else:
            self.setStyleSheet("""
                                    {
                                        border:10px;
                                        background: rgb(51, 53, 55);
                                        dashed #242424;
                                    }
                                    """)
        self._delete_button.show()

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        if not self._is_selected:
            self.setStyleSheet("""
                                    {
                                        border:10px;
                                        background: rgb(60, 63, 65);
                                        dashed #242424;
                                    }
                                    """)
        else:
            self.setStyleSheet("""
                                    {
                                        border:10px;
                                        background: rgb(78, 82, 84);
                                        dashed #242424;
                                    }
                                    """)
        self._delete_button.hide()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._tag_selected()

    def _delete_me(self):
        self.tag_need_deleting(str).emit(self._tag_text)

    def _tag_selected(self):
        if self._is_selected:
            self._is_selected = False
            self.tag_selected(str, bool).emit(self._tag_text, self._is_selected)
        else:
            self._is_selected = True
            self.tag_selected(str, bool).emit(self._tag_text, self._is_selected)
