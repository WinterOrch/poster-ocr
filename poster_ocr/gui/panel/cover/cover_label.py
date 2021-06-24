from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPixmap, QBrush
from PyQt5.QtWidgets import QLabel, QSizePolicy

from poster_ocr.vo.douban_movie import DoubanMovieInfo

COVER_LABEL_RADIUS = 3


class CoverLabel(QLabel):
    def __init__(self, width, height, parent=None, pixmap=None):
        super().__init__(parent=parent)

        self._pixmap = pixmap
        self.setMinimumSize(width, height)
        self.setMaximumSize(width, height)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

    def show_pixmap(self, pixmap):
        self._pixmap = pixmap
        self.updateGeometry()

    def paintEvent(self, a0) -> None:
        """ draw pixmap with border radius
        """
        if self._pixmap is None:
            return
        assert isinstance(self._pixmap, QPixmap) is True
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        scaled_pixmap = self._pixmap.scaledToWidth(self.width(), mode=Qt.SmoothTransformation)
        size = scaled_pixmap.size()
        painter.setBrush(QBrush(scaled_pixmap))
        painter.setPen(Qt.NoPen)
        y = (size.height() - self.height()) // 2
        painter.save()
        painter.translate(0, -y)

        rect = QRect(0, y, self.width(), self.height())
        painter.drawRoundedRect(rect, COVER_LABEL_RADIUS, COVER_LABEL_RADIUS)
        painter.restore()
        painter.end()

    async def show_cover(self, movie_info: DoubanMovieInfo):
        pixmap = await movie_info.load_photo()
        if not pixmap.isNull():
            self.show_pixmap(pixmap)

    def resizeEvent(self, a0) -> None:
        super().resizeEvent(a0)
        self.updateGeometry()
