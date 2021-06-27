from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from poster_ocr.gui.panel.history.history_panel import HistoryPanel
from poster_ocr.gui.panel.tag.flow_tag import FlowTagPane


class RightPanel(QWidget):
    cover_ocr_needed = pyqtSignal(str)

    def __init__(self, parent=None):
        super(RightPanel, self).__init__(parent=parent)

        self._layout = QVBoxLayout(self)

        self.history_panel = HistoryPanel(self)
        self.flow_tag_panel = FlowTagPane(self)

        self._setup_ui()
        self._bind_signals()

    def _setup_ui(self):

        self.history_panel.setMinimumHeight(500)
        self.flow_tag_panel.setMinimumHeight(300)

        self._layout.addWidget(self.history_panel)
        self._layout.addWidget(self.flow_tag_panel)

    def _bind_signals(self):
        self.history_panel.cover_ocr_needed.connect(self._call_for_ocr)

    def _call_for_ocr(self, path: str):
        if self.warning("Would you like to clear existing tags before adding new ones?"):
            self.flow_tag_panel.clear_all_tags()
        self.cover_ocr_needed.emit(path)

    @staticmethod
    def warning(info):
        msg_box = QtWidgets.QMessageBox()

        msg_box.setWindowTitle('Info')
        msg_box.setIcon(QtWidgets.QMessageBox.Warning)
        msg_box.setText('Information')
        msg_box.setInformativeText(info)
        msg_box.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)
        no = msg_box.addButton('No', QtWidgets.QMessageBox.RejectRole)
        msg_box.setDefaultButton(no)

        reply = msg_box.exec()
        if reply == QtWidgets.QMessageBox.AcceptRole:
            return True
        else:
            return False
