from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QListWidget, QListWidgetItem

from gui.theme import read_qss_resource, get_icon_resource
from poster_ocr.gui.result_display_widget import ResDisplayWidget
from poster_ocr.gui.right_panel import RightPanel
from poster_ocr.vo.douban_movie import DoubanMovieInfo
from poster_ocr.vo.history_item import HistoryItemInfo

ICON_SIZE = QSize(55, 55)


class ClientWidget(QWidget):
    crawl_for_listed_tags_needed = pyqtSignal([str])
    """Invoke display_douban_results() to display douban results
    
    You can also dump current results by invoking dump_current_results()
    """

    ocr_for_cover_file_needed = pyqtSignal(str)
    """Invoke add_new_tags() to display all tags on tag panel
    
    You can also dump and load tags in json form by invoking
    dump_tags() and load_tags()
    """

    show_history_records_for_current_user_needed = pyqtSignal()
    """Invoke show_history() to show all history records for the user
    
    You can also invoke add_new_record_for_user() if you are trying
    to insert a new one
    
    and invoke get_all_history_items() to get all history items for
    current user
    """

    def __init__(self):
        super(ClientWidget, self).__init__()
        self.setObjectName("ClientWidget")

        self.setWindowTitle('Poster OCR')
        self.list_style = read_qss_resource('ClientWidgetQSS.qss')

        self.left_widget = QListWidget()
        self.left_widget.setStyleSheet(self.list_style)

        self.middle_widget = ResDisplayWidget(self)

        self.right_widget = RightPanel(self)

        self._set_ui()

    def _set_ui(self):
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        # Left Side Widget
        self.left_widget.setFrameShape(QListWidget.NoFrame)
        self.left_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.left_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.left_widget.setIconSize(ICON_SIZE)
        self.left_widget.setViewMode(QtWidgets.QListView.IconMode)

        icon_url_list = ['cancel.png', 'cloud-computing.png', 'info.png']
        item_str_list = ['Back', 'Recognize', 'Load History']

        for icon_url, item_str in zip(icon_url_list, item_str_list):
            item = QListWidgetItem()
            if icon_url is not None:
                icon = QIcon()
                icon.addPixmap(
                    QPixmap(get_icon_resource(icon_url)).scaled(ICON_SIZE, transformMode=Qt.SmoothTransformation)
                )
                item.setIcon(icon)
            item.setText(item_str)
            item.setSizeHint(QSize(110, 90))
            item.setTextAlignment(Qt.AlignCenter)
            self.left_widget.addItem(item)

        # Combined Layout
        self.combined_widget = QWidget(self)
        combined_layout = QHBoxLayout(self.combined_widget)
        combined_layout.setContentsMargins(0, 0, 0, 0)

        self.middle_widget.setMinimumWidth(500)
        self.right_widget.setMinimumWidth(300)

        combined_layout.addWidget(self.middle_widget)
        combined_layout.addWidget(self.right_widget)

        self._layout.addWidget(self.left_widget)
        self._layout.addWidget(self.combined_widget)

    def _bind_signals(self):
        self.left_widget.currentRowChanged.connect(self.on_func_button_pushed)
        self.right_widget.cover_ocr_needed.connect(self.on_ocr_needed)

    @staticmethod
    def warning(info):
        msg_box = QtWidgets.QMessageBox()

        msg_box.setWindowTitle('Tips')
        msg_box.setIcon(QtWidgets.QMessageBox.Warning)
        msg_box.setText('Information')
        msg_box.setInformativeText(info)
        msg_box.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)

        msg_box.exec()

    def on_ocr_needed(self, path: str):
        self.ocr_for_cover_file_needed.emit(path)

    def on_func_button_pushed(self, index):
        if index == 0:
            # TODO CLose Client and return
            pass
        elif index == 1:
            """Call for crawling"""
            tag_list = self.right_widget.flow_tag_panel.get_selected_tags()
            if tag_list:
                self.crawl_for_listed_tags_needed.emit(tag_list)
            else:
                self.warning("Choose some tags you're interested in please.")
                self.right_widget.flow_tag_panel.shine()

        elif index == 2:
            """Load history records for current user"""
            self.show_history_records_for_current_user_needed.emit()

    """         History Pane Concerned Methods          """
    def show_history(self, info_list: [HistoryItemInfo]):
        self.right_widget.history_panel.load_all_history_items(info_list)

    def add_new_record_for_user(self, info: HistoryItemInfo):
        self.right_widget.history_panel.try_add_item(info, True)

    def get_all_history_items(self) -> [HistoryItemInfo]:
        return self.right_widget.history_panel.get_all_history_items()
    """      End for History Pane Concerned Methods     """

    """         Flow Tag Pane Concerned Methods         """
    def add_new_tags(self, tags: [str]):
        for tag in tags:
            self.right_widget.flow_tag_panel.add_new_tag(tag)

    def load_tags(self, json_str: str):
        self.right_widget.flow_tag_panel.load_all_tags(json_str)

    def dump_tags(self) -> str:
        return self.right_widget.flow_tag_panel.dump_all_tags()
    """    End for Flow Tag Pane Concerned Methods      """

    """      Result Display Pane Concerned Methods      """
    def display_douban_results(self, lx: [DoubanMovieInfo]):
        self.middle_widget.show_results(lx)

    def dump_current_results(self) -> [DoubanMovieInfo]:
        return self.middle_widget.dump_results()
    """  End for Result Display Pane Concerned Methods  """
