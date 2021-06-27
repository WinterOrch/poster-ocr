from enum import IntEnum

from PyQt5.QtCore import Qt, QSize, pyqtSignal, QModelIndex, QAbstractTableModel, QVariant
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QTableView, QFrame, QAbstractItemView, QAction, QHeaderView, \
    QMenu

from poster_ocr.gui.util.dispatch import Signal
from poster_ocr.vo.douban_movie import DoubanMovieInfo


class Column(IntEnum):
    INDEX = 0
    MOVIE = 1
    DATE = 2
    STAFF = 3
    RATE = 4
    DESCRIPTION = 5


class MoviesTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fetch_more_step = 30
        self._items = []
        self._is_fetching = False

    def append_data_list(self, x: [DoubanMovieInfo]):
        self.beginResetModel()
        for info in x:
            self._items.append(info)
        self.endResetModel()

    def fetch_data(self) -> [DoubanMovieInfo]:
        return self._items

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        while count > 0:
            self._items.pop(row)
            count -= 1
        self.endRemoveRows()
        return True

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def columnCount(self, _=QModelIndex()):
        return 6

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        sections = ('', '电影', '上映时间', '演职人员', '评分', '描述')
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section < len(sections):
                    return sections[section]
                return ''
            elif role == Qt.SizeHintRole and self.parent() is not None:
                # we set height to 25 since the header can be short under macOS.
                # HELP: set height to fixed value manually is not so elegant
                height = 25
                # HELP: the last column width percent should be 1-others.
                # 0.3 may cause the header wider than the tableview
                # (for example, under KDE Plasma 5.15.5 with QT 5.12.3),
                # which is unacceptable. In fact, the width percent can be 0.2
                # or even less since we have enabled StretchLastSection.
                widths = (0, 0.3, 0.15, 0.2, 0.1, 0.2)
                width = self.parent().width()
                w = int(width * widths[section])
                print("" + section.__str__() + ": " + w.__str__())
                return QSize(w, height)
        else:
            if role == Qt.DisplayRole:
                return section
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignRight
        return QVariant()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        if index.row() >= len(self._items) or index.row() < 0:
            return QVariant()

        movie = self._items[index.row()]
        if role in (Qt.DisplayRole, Qt.ToolTipRole):
            if index.column() == Column.INDEX:
                return index.row() + 1
            elif index.column() == Column.MOVIE:
                return movie.title_display
            elif index.column() == Column.DATE:
                return movie.date_display
            elif index.column() == Column.STAFF:
                return movie.staffs_display
            elif index.column() == Column.RATE:
                return movie.rate_display
            elif index.column() == Column.DESCRIPTION:
                return "description"
        elif role == Qt.TextAlignmentRole:
            if index.column() == Column.INDEX:
                return Qt.AlignCenter | Qt.AlignVCenter
            elif index.column() == Column.STAFF:
                return Qt.AlignCenter | Qt.AlignVCenter
            elif index.column() == Column.RATE:
                return Qt.AlignCenter | Qt.AlignVCenter
        elif role == Qt.EditRole:
            return 1
        elif role == Qt.UserRole:
            return movie
        return QVariant()


class MoviesTableView(QTableView):
    play_song_needed = pyqtSignal([object])
    add_to_list_needed = pyqtSignal(list)

    pop_up_poster = pyqtSignal(str, int)

    def __init__(self, parent=None):
        super(MoviesTableView, self).__init__(parent)

        # override ItemViewNoScrollMixin variables
        self._least_row_count = 6
        self._row_height = 30

        # slot functions
        self.remove_song_func = None

        self.about_to_show_menu = Signal()

        self._setup_ui()
        self._bind_signal()

        self._mouse_relative_y = 0
        self.setMouseTracking(True)

    def _setup_ui(self):
        # FIXME: PyQt5 seg fault
        # self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.verticalHeader().hide()
        # self.horizontalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(self._row_height)
        self.setWordWrap(False)
        self.setTextElideMode(Qt.ElideRight)
        self.setMouseTracking(True)
        self.setEditTriggers(QAbstractItemView.SelectedClicked)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setShowGrid(False)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragOnly)

    def _bind_signal(self):
        self.clicked.connect(self.on_click)

    def on_click(self, index: QModelIndex):
        print("OHYEAH" + index.data(Qt.UserRole).photo_url)
        self.pop_up_poster.emit(index.data(Qt.UserRole).photo_url, self._mouse_relative_y)

    def show_artists_by_index(self, index):
        self.edit(index)

    def contextMenuEvent(self, event):
        indexes = self.selectionModel().selectedIndexes()
        if len(indexes) <= 0:
            return

        menu = QMenu()

        # add to playlist action
        add_to_playlist_action = QAction('添加', menu)
        add_to_playlist_action.triggered.connect(lambda: self._add_to_playlist(indexes))
        menu.addAction(add_to_playlist_action)

        # remove song action
        if self.remove_song_func is not None:
            remove_song_action = QAction('移除歌曲', menu)
            remove_song_action.triggered.connect(
                lambda: self._remove_by_indexes(indexes))
            menu.addSeparator()
            menu.addAction(remove_song_action)

        model = self.model()
        models = [model.data(index, Qt.UserRole) for index in indexes]

        def add_action(text, callback):
            action = QAction(text, menu)
            menu.addSeparator()
            menu.addAction(action)
            action.triggered.connect(lambda: callback(models))

        self.about_to_show_menu.emit({'add_action': add_action, 'models': models})
        menu.exec(event.globalPos())

    def _add_to_playlist(self, indexes):
        model = self.model()
        songs = []
        for index in indexes:
            song = model.data(index, Qt.UserRole)
            songs.append(song)
        self.add_to_playlist_needed.emit(songs)

    def _remove_by_indexes(self, indexes):
        model = self.model()
        source_model = model.sourceModel()
        distinct_rows = set()
        for index in indexes:
            row = index.row()
            if row not in distinct_rows:
                song = model.data(index, Qt.UserRole)
                self.remove_song_func(song)
                distinct_rows.add(row)
        source_model.removeRows(indexes[0].row(), len(distinct_rows))

    def modify_size(self):
        widths = (0, 0.25, 0.17, 0.13, 0.08, 0.35)
        width = self.parent().width()

        for section in range(self._least_row_count):
            self.horizontalHeader().resizeSection(section, int(width * widths[section]))

    def on_rows_changed(self, *args):
        if self._no_scroll_v is True:
            self.adjust_height()

    def setModel(self, model):
        super(MoviesTableView, self).setModel(model)

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        super(MoviesTableView, self).mouseMoveEvent(a0)
        self._mouse_relative_y = a0.y()
