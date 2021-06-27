import os
import time

from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QLinearGradient, QGradient, QColor, QBrush, QFont, QPainter, QIcon
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QGridLayout, QPushButton, QListWidgetItem, QFrame

from poster_ocr.gui.animation.shadow_effect import AnimationShadowEffect
from poster_ocr.vo.history_item import HistoryItemInfo

COVER_WIDTH = 220
COVER_HEIGHT = 308
ITEM_HEIGHT = 380


class CoverLabel(QLabel):
    def __init__(self, cover_dir, cover_title=""):
        super(CoverLabel, self).__init__()

        self.setCursor(Qt.PointingHandCursor)
        self.setScaledContents(True)
        self.setMinimumSize(COVER_WIDTH, COVER_HEIGHT)
        self.setMaximumSize(COVER_WIDTH, COVER_HEIGHT)
        self._cover_dir = cover_dir
        self._cover_title = cover_title

        self.setPixmap(QPixmap(self._cover_dir))

    def set_cover_dir(self, cover_dir):
        self._cover_dir = cover_dir

    def mouseReleaseEvent(self, ev) -> None:
        """Open Picture with os explorer.exe by Windows
        """
        super(CoverLabel, self).mouseReleaseEvent(ev)
        os.system('explorer.exe "{}"'.format(self._cover_dir))

    def paintEvent(self, event):
        super(CoverLabel, self).paintEvent(event)
        if hasattr(self, "cover_title") and self.cover_title != "":
            # 底部绘制文字
            painter = QPainter(self)
            rect = self.rect()
            # 粗略字体高度
            painter.save()
            font_height = self.fontMetrics().height()
            # 底部矩形框背景渐变颜色
            bottom_rect_color = QLinearGradient(
                rect.width() / 2, rect.height() - 24 - font_height,
                rect.width() / 2, rect.height())
            bottom_rect_color.setSpread(QGradient.PadSpread)
            bottom_rect_color.setColorAt(0, QColor(255, 255, 255, 70))
            bottom_rect_color.setColorAt(1, QColor(0, 0, 0, 50))
            # 画半透明渐变矩形框
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(bottom_rect_color))
            painter.drawRect(rect.x(), rect.height() - 24 - font_height, rect.width(), 24 + font_height)
            painter.restore()
            # 距离底部一定高度画文字
            font = self.font() or QFont()
            font.setPointSize(8)
            painter.setFont(font)
            painter.setPen(Qt.white)
            rect.setHeight(rect.height() - 12)  # 底部减去一定高度
            painter.drawText(rect, Qt.AlignHCenter | Qt.AlignBottom, self.cover_title)


class ItemWidget(QFrame):
    cover_ocr_needed = pyqtSignal(str)
    deleting_needed = pyqtSignal(str, QListWidgetItem)

    def __init__(self, cover_dir, cover_title, history_time: time,
                 rec_icon: QIcon, del_icon: QIcon, item: QListWidgetItem,
                 is_shiny=True, parent=None):
        super(ItemWidget, self).__init__(parent=parent)
        self.setObjectName("ItemWidget")

        self.setMinimumSize(COVER_WIDTH + 5, ITEM_HEIGHT + 5)
        self.setMaximumSize(COVER_WIDTH + 5, ITEM_HEIGHT + 5)

        self._item = item

        self._layout = QVBoxLayout(self)

        self._cover_dir = cover_dir
        self._cover_title = cover_title
        self._time = history_time

        if not self._cover_dir:
            self._label_cover = CoverLabel(self._cover_dir)
        else:
            self._label_cover = CoverLabel(self._cover_dir, self._cover_title)

        self._setup_ui(rec_icon, del_icon)

        if is_shiny:
            self._animation_shadow = AnimationShadowEffect(Qt.cyan, loop_count=5)
            self.shadow_start()
        self._is_new = is_shiny

    def _setup_ui(self, rec_icon: QIcon, del_icon: QIcon):
        self._layout.setContentsMargins(2, 2, 2, 6)
        self._layout.addWidget(self._label_cover)

        filepath, filename = os.path.split(self._cover_dir)
        label = QLabel(filename, self)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self._layout.addWidget(label)
        label = QLabel(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self._time)), self)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self._layout.addWidget(label)

        # Add buttons and bind signal
        button_layout = QGridLayout()
        rec_button = QPushButton()
        rec_button.setIcon(rec_icon)
        rec_button.clicked.connect(self._recognize_me)
        del_button = QPushButton()
        del_button.setIcon(del_icon)
        del_button.clicked.connect(self._delete_me)
        button_layout.addWidget(rec_button, 0, 0)
        button_layout.addWidget(del_button, 0, 1)
        self._layout.addLayout(button_layout)

    def sizeHint(self):
        return QSize(COVER_WIDTH, ITEM_HEIGHT)

    def shadow_start(self):
        self.setGraphicsEffect(self._animation_shadow)
        self._animation_shadow.start()

    def mousePressEvent(self, a0) -> None:
        """Stop shadow animation when pressed
        """
        super().mouseReleaseEvent(a0)

        if self._is_new:
            self._animation_shadow.stop()

    def _recognize_me(self):
        self.cover_ocr_needed.emit(self._cover_dir)

    def _delete_me(self):
        self.deleting_needed.emit(self._cover_dir, self._item)

    def get_history_item_info(self) -> HistoryItemInfo:
        return HistoryItemInfo(self._cover_dir, self._cover_title, self._time)
