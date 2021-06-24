from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from poster_ocr.gui.panel.history.history_panel import HistoryPanel
from poster_ocr.gui.panel.tag.flow_tag import FlowTagPane


class RightPanel(QWidget):
    cover_ocr_needed = pyqtSignal(str)

    def __init__(self, parent=None):
        super(RightPanel, self).__init__(parent=parent)
        self.setWindowFlags(
            Qt.Window | Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)

        self._layout = QVBoxLayout(self)

        self.history_panel = HistoryPanel(self)
        self.flow_tag_panel = FlowTagPane(self)

    def _setup_ui(self):
        self._layout.setStretch(0, 3)   # History Panel should be bigger
        self._layout.setStretch(1, 2)

        self._layout.addWidget(self.history_panel)
        self._layout.addWidget(self.flow_tag_panel)

    def _bind_signals(self):
        self.history_panel.cover_ocr_needed.connect(self._call_for_ocr)

    def _call_for_ocr(self, path: str):
        self.cover_ocr_needed(str).emit(path)
