from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QLabel

from poster_ocr.gui.result.movie_list import MoviesTableView, MoviesTableModel, MovieFilterProxyModel
from poster_ocr.vo.douban_movie import DoubanMovieInfo


class ResDisplayWidget(QWidget):
    def __init__(self):
        super(ResDisplayWidget, self).__init__()
        self.setObjectName("ResDisplayWidget")

        with open('../qss/QListWidgetQSS.qss', 'r') as f:
            self.list_style = f.read()

        self.result_display_table = MoviesTableView(self)

        self._setup_ui()

    def _setup_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self.result_display_table)

        self._layout.addStretch(0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

    def _show_results(self, lx: [DoubanMovieInfo]):
        model = MoviesTableModel(self.result_display_table)
        model.append_data(lx)
        filter_mode = MovieFilterProxyModel(self.result_display_table)
        filter_mode.setSourceModel(model)
        self.result_display_table.setModel(filter_mode)
        self.result_display_table.scrollToTop()
