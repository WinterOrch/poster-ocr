from PyQt5.QtWidgets import QWidget, QHBoxLayout, QListWidget

from poster_ocr.gui.result_display_widget import ResDisplayWidget
from poster_ocr.gui.right_panel import RightPanel


class ClientWidget(QWidget):
    def __init__(self):
        super(ClientWidget, self).__init__()
        self.setObjectName("ClientWidget")

        self.setWindowTitle('Poster OCR')
        with open('../qss/QListWidgetQSS.qss', 'r') as f:
            self.list_style = f.read()

        self.left_widget = QListWidget()
        self.left_widget.setStyleSheet(self.list_style)

        self.middle_widget = ResDisplayWidget(self)

        self.right_widget = RightPanel(self)

    def _set_ui(self):
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        combined_layout = QHBoxLayout(self._layout)
        combined_layout.setContentsMargins(0, 0, 0, 0)
        combined_layout.setStretch(0, 5)
        combined_layout.setStretch(1, 2)
        combined_layout.addWidget(self.middle_widget)
        combined_layout.addWidget(self.right_widget)

        self._layout.addWidget(self.left_widget)
        self._layout.addLayout(combined_layout)

    def _bind_signals(self):
        self.right_widget.cover_ocr_needed.connect(self.on_ocr_needed)

    def on_ocr_needed(self, path: str):
        pass
        # TODO OCR API call
