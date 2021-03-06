from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from gui.theme import get_icon_resource, read_qss_resource
from poster_ocr.gui.panel.history.item_widget import ItemWidget
from poster_ocr.gui.util.excpetion import ListWidgetItemNotMatchedException
from poster_ocr.vo.history_item import HistoryItemInfo

HISTORY_PANEL_WIDTH = 700
HISTORY_PANEL_HEIGHT = 500

TESTING = True


StyleSheet = read_qss_resource('HistoryItemQSS.qss')


class HistoryPanel(QListWidget):
    cover_ocr_needed = pyqtSignal(str)

    def __init__(self, parent=None):
        super(HistoryPanel, self).__init__(parent=parent)
        self.setObjectName("HistoryPanel")
        self.setMinimumSize(HISTORY_PANEL_WIDTH, HISTORY_PANEL_HEIGHT)

        # The same as FlowLayout
        self.setFrameShape(QListWidget.NoFrame)
        self.setFlow(QListWidget.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(QListWidget.Adjust)

        self._setup_ui()
        self.setVisible(True)

        pix_img = QtGui.QPixmap(QtGui.QImage(get_icon_resource('garbage.png')))
        fit_pixmap = pix_img.scaled(12, 12, transformMode=Qt.SmoothTransformation)
        self._del_icon = QtGui.QIcon(fit_pixmap)
        pix_img = QtGui.QPixmap(QtGui.QImage(get_icon_resource('magnifying-glass.png')))
        fit_pixmap = pix_img.scaled(12, 12, transformMode=Qt.SmoothTransformation)
        self._rec_icon = QtGui.QIcon(fit_pixmap)

        self._cover_items_map = {}

        if TESTING:
            pass

    def _setup_ui(self):
        self.setSpacing(8)
        self.setContentsMargins(0, 8, 8, 8)

        self.setStyleSheet(StyleSheet)

    def try_add_item(self, info: HistoryItemInfo, is_new):
        """Try to add a history item into History Panel

        :param info:    Info VO Entity for History Item
        :param is_new:  Whether info is new to the panel, if true, its item widget will shine
        """
        if not self._cover_items_map.__contains__(info.cover_dir):
            self._do_add_item(info.cover_dir, info.cover_title, info.history_time, is_new)
        else:
            print(info.cover_dir + " already been added before")

    def _do_add_item(self, cover_dir: str, cover_title, history_time, is_new):
        item = QListWidgetItem(self)
        widget = ItemWidget(cover_dir, cover_title, history_time,
                            self._rec_icon, self._del_icon, item,
                            is_shiny=is_new, parent=self)
        widget.deleting_needed.connect(self._delete_item)
        widget.cover_ocr_needed.connect(self._call_for_ocr)
        item.setSizeHint(widget.sizeHint())
        self.setItemWidget(item, widget)
        self._cover_items_map[cover_dir] = widget

        self.repaint()

    def _call_for_ocr(self, cover_dir: str):
        self.cover_ocr_needed.emit(cover_dir)

    def _delete_item(self, cover_dir: str, item: QListWidgetItem):
        target = self._cover_items_map.pop(cover_dir)

        if target is not self.itemWidget(item):
            raise ListWidgetItemNotMatchedException
        else:
            self._do_delete_item(item)

    def _do_delete_item(self, item):
        self.takeItem(self.row(item))
        self.removeItemWidget(item)
        del item

    def _do_clear_items(self):
        """Destroy all item widgets and clear cover map
        """
        for _ in range(self.count()):
            item = self.takeItem(0)
            self.removeItemWidget(item)
            del item
        self._cover_items_map = {}

    def get_all_history_items(self) -> [HistoryItemInfo]:
        """Get all infos as a list for all items in the panel
        """
        res = []

        for k, v in self._cover_items_map.items():
            if isinstance(v, ItemWidget):
                res.append(v.get_history_item_info())

        return res

    def load_all_history_items(self, info_list: [HistoryItemInfo]):
        """Load and display all history items.

        :param info_list: List contains info for all history items to display
        """
        for info in info_list:
            if isinstance(info, HistoryItemInfo):
                self.try_add_item(info, False)
