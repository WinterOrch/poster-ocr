from PyQt5.QtWidgets import QWidget, QHBoxLayout, QListWidget

from poster_ocr.gui.result_display_widget import ResDisplayWidget


class ClientWidget(QWidget):
    def __init__(self):
        super(ClientWidget, self).__init__()
        self.setObjectName("ClientWidget")

        self.setWindowTitle('Poster OCR')
        with open('../qss/QListWidgetQSS.qss', 'r') as f:
            self.list_style = f.read()

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.left_widget = QListWidget()
        self.left_widget.setStyleSheet(self.list_style)
        self.main_layout.addWidget(self.left_widget)

        self.middle_widget = ResDisplayWidget()
