from PyQt5.QtCore import QModelIndex, Qt, QPoint
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from poster_ocr.gui.panel.cover.cover_display_render import Render
from poster_ocr.gui.panel.result.movie_list import MoviesTableView, MoviesTableModel, MovieFilterProxyModel
from poster_ocr.vo.douban_movie import DoubanMovieInfo


class ResDisplayWidget(QWidget):
    def __init__(self, parent=None):
        super(ResDisplayWidget, self).__init__(parent=parent)
        self.setObjectName("ResDisplayWidget")

        with open('../qss/ClientWidgetQSS.qss', 'r') as f:
            self.list_style = f.read()

        self.result_display_table = MoviesTableView(self)
        self.render = Render(parent=self)

        self.setMouseTracking(True)
        self._mouse_relative_y = -1

        self._model = None

        self._setup_ui()

    def _setup_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self.result_display_table)

        self._layout.addStretch(0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

    def _bind_signals(self):
        self.result_display_table.activated.connect(self._on_table_activated)

    def _on_table_activated(self, index: QModelIndex):
        movie = index.data(Qt.UserRole)
        assert isinstance(movie, DoubanMovieInfo)
        self.render.pop_new_bubble(QPoint(self.width() + 20, self._mouse_relative_y), movie.photo_url)
        # TODO 理论上这样会画到 parent 外，如果不行就换全局坐标试一试

    def show_results(self, lx: [DoubanMovieInfo]):
        model = MoviesTableModel(self.result_display_table)
        model.append_data(lx)
        self._model = model
        filter_mode = MovieFilterProxyModel(self.result_display_table)
        filter_mode.setSourceModel(model)
        self.result_display_table.setModel(filter_mode)
        self.result_display_table.scrollToTop()

    def dump_results(self) -> [DoubanMovieInfo]:
        return self._model.fetch_data()

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        super(ResDisplayWidget, self).mouseMoveEvent(a0)
        self._mouse_relative_y = a0.y()
