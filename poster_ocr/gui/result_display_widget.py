from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QVBoxLayout, QSizePolicy, QFrame, QAbstractScrollArea

from gui.theme import read_qss_resource
from poster_ocr.gui.panel.cover.cover_display_render import Render
from poster_ocr.gui.panel.result.movie_list import MoviesTableView, MoviesTableModel
from poster_ocr.vo.douban_movie import DoubanMovieInfo

StyleSheet = read_qss_resource('ResultDisplayPaneQSS.qss')


class ResDisplayWidget(QFrame):
    def __init__(self, parent=None):
        super(ResDisplayWidget, self).__init__(parent=parent)
        self.setObjectName("ResDisplayWidget")
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self.result_display_table = MoviesTableView(self)

        self.result_display_table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.render = Render(parent=self)

        self._model = None

        self._setup_ui()
        self._bind_signals()

    def _setup_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self.result_display_table)

        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(8)

        self.setStyleSheet(StyleSheet)

    def _bind_signals(self):
        self.result_display_table.pop_up_poster.connect(self._on_table_activated)

    def _on_table_activated(self, info: str, mouse_relative_y: int):
        self.render.pop_new_bubble(QPoint(self.width() + 20, mouse_relative_y), info)
        # TODO 理论上这样会画到 parent 外，如果不行就换全局坐标试一试

    def show_results(self, lx: [DoubanMovieInfo]):
        model = MoviesTableModel(self.result_display_table)
        model.append_data_list(lx)
        self._model = model
        self.result_display_table.setModel(self._model)
        self.result_display_table.modify_size()

    def dump_results(self) -> [DoubanMovieInfo]:
        return self._model.fetch_data()