from PyQt5.QtWidgets import QWidget, QHBoxLayout, QListWidget

from poster_ocr.gui.result_display_widget import ResDisplayWidget


class ClientWidget(QWidget):
    def __init__(self):
        super(ClientWidget, self).__init__()
        self.setObjectName("ClientWidget")

        self.setWindowTitle('Poster OCR')
        with open('../qss/QListWidgetQSS.qss', 'r') as f:
            self.list_style = f.read()

        self.left_widget = QListWidget()
        self.left_widget.setStyleSheet(self.list_style)

        self.middle_widget = ResDisplayWidget()

    def _set_ui(self):
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._layout.addLayout(self.left_widget)
        self._layout.addLayout(self.middle_widget)

        self.setLayout(self._layout)
