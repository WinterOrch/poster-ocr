from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QLabel


class ResDisplayWidget(QWidget):
    def __init__(self):
        super(ResDisplayWidget, self).__init__()
        self.setObjectName("ResDisplayWidget")

        with open('../qss/QListWidgetQSS.qss', 'r') as f:
            self.list_style = f.read()

        self.main_layout = QScrollArea(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setHorizontalScrollBarPolicy()

        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout.setLayout(self.content_layout)