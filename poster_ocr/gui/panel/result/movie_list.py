from enum import IntEnum

from PyQt5.QtCore import QSortFilterProxyModel, Qt, QPoint, QSize, pyqtSignal, QModelIndex, QRect, QEvent, \
    QAbstractListModel, QAbstractTableModel, QVariant
from PyQt5.QtGui import QPalette, QPen, QPainter, QMouseEvent
from PyQt5.QtWidgets import QStyledItemDelegate, QListView, QTableView, QFrame, QAbstractItemView, QAction, QHeaderView, \
    QMenu, QStyle, QSizePolicy

from poster_ocr.gui.util.dispatch import Signal
from poster_ocr.gui.util.helpers import ItemViewNoScrollMixin, ReaderFetchMoreMixin
from poster_ocr.vo.douban_movie import DoubanMovieInfo


class Column(IntEnum):
    INDEX = 0
    MOVIE = 1
    DATE = 2
    STAFF = 3
    RATE = 4
    DESCRIPTION = 5


class MovieListModel(QAbstractListModel, ReaderFetchMoreMixin):
    def __init__(self, reader, parent=None):
        super().__init__(parent)

        self._reader = reader
        self._fetch_more_step = 10
        self._items = []
        self._is_fetching = False

    def rowCount(self, _=QModelIndex()):
        return len(self._items)

    def flags(self, index):
        if not index.isValid():
            return 0
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        return flags

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if role == Qt.DisplayRole:
            return self._items[row].title_display
        elif role == Qt.UserRole:
            return self._items[row]
        return None


class MovieListDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent=parent)

        # the rect.x the number text
        self.number_rect_x = 20
        self.play_btn_pressed = False

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        movie = index.data(Qt.UserRole)
        top = option.rect.top()
        bottom = option.rect.bottom()
        no_x = self.number_rect_x
        date_width = 100
        staffs_display = 150

        # Draw date
        duration_x = option.rect.topRight().x() - date_width
        duration_rect = QRect(QPoint(duration_x, top), option.rect.bottomRight())
        painter.drawText(duration_rect, Qt.AlignRight | Qt.AlignVCenter,
                         movie.duration_ms_display)

        # Draw staffs
        artists_name_x = option.rect.topRight().x() - date_width - staffs_display
        artists_name_rect = QRect(QPoint(artists_name_x, top),
                                  QPoint(duration_x, bottom))
        painter.drawText(artists_name_rect, Qt.AlignRight | Qt.AlignVCenter,
                         movie.artists_name_display)

        # Draw song number or play_btn when it is hovered
        no_bottom_right = QPoint(no_x, bottom)
        no_rect = QRect(option.rect.topLeft(), no_bottom_right)
        if option.state & QStyle.State_MouseOver:
            painter.drawText(no_rect, Qt.AlignLeft | Qt.AlignVCenter, '►')
        else:
            painter.drawText(no_rect, Qt.AlignLeft | Qt.AlignVCenter,
                             str(index.row() + 1))

        # Draw title
        title_rect = QRect(QPoint(no_x, top), QPoint(artists_name_x, bottom))
        painter.drawText(title_rect, Qt.AlignVCenter, movie.title_display)

        painter.restore()

    def editorEvent(self, event, model, option, index):
        if event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease):
            no_bottom_right = QPoint(self.number_rect_x, option.rect.bottom())
            no_rect = QRect(option.rect.topLeft(), no_bottom_right)
            mouse_event = QMouseEvent(event)
            if no_rect.contains(mouse_event.pos()):
                if event.type() == QEvent.MouseButtonPress:
                    self.play_btn_pressed = True
                if event.type() == QEvent.MouseButtonRelease:
                    if self.play_btn_pressed is True:
                        self.parent().play_song_needed.emit(index.data(Qt.UserRole))
            if event.type() == QEvent.MouseButtonRelease:
                self.play_btn_pressed = False
        return super().editorEvent(event, model, option, index)

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        if index.isValid():
            return QSize(size.width(), 36)
        return size


class MovieListView(ItemViewNoScrollMixin, QListView):

    movie_list_activated = pyqtSignal([object])

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        QListView.__init__(self, parent)

        self.delegate = MovieListDelegate(self)
        self.setItemDelegate(self.delegate)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setMouseTracking(True)
        self.setFrameShape(QFrame.NoFrame)
        self.activated.connect(self._on_activated)

    def _on_activated(self, index):
        self.movie_list_activated.emit(index.data(Qt.UserRole))


class MoviesTableModel(QAbstractTableModel, ReaderFetchMoreMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fetch_more_step = 30
        self._items = []
        self._is_fetching = False

    def append_data(self, x):
        self._items.append(x)
        self.layoutChanged.emit()

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
                widths = (0.05, 0.1, 0.25, 0.1, 0.2, 0.2)
                width = self.parent().width()
                w = int(width * widths[section])
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
                return movie.description_display
        elif role == Qt.TextAlignmentRole:
            if index.column() == Column.index:
                return Qt.AlignCenter | Qt.AlignVCenter
            elif index.column() == Column.source:
                return Qt.AlignCenter | Qt.AlignBaseline
        elif role == Qt.EditRole:
            return 1
        elif role == Qt.UserRole:
            return movie
        return QVariant()


class StaffsSelectionView(QListView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.FramelessWindowHint)
        self.setObjectName('staffs_selection_view')


class MoviesTableDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)
        self.view = parent

    def createEditor(self, parent, option, index):
        if index.column() == Column.STAFF:
            editor = StaffsSelectionView(parent)
            editor.clicked()                    # TODO Popup
            editor.move(parent.mapToGlobal(option.rect.bottomLeft()))
            editor.setFixedWidth(option.rect.width())
            return editor

    def setEditorData(self, editor, index):
        super().setEditorData(editor, index)
        # TODO Popup

    def paint(self, painter, option, index):
        super().paint(painter, option, index)

        # draw a line under each row
        text_color = option.palette.color(QPalette.Text)
        if text_color.lightness() > 150:
            non_text_color = text_color.darker(140)
        else:
            non_text_color = text_color.lighter(150)
        non_text_color.setAlpha(30)
        pen = QPen(non_text_color)
        painter.setPen(pen)
        bottom_left = option.rect.bottomLeft()
        bottom_right = option.rect.bottomRight()
        if index.model().columnCount() - 1 == index.column():
            bottom_right = QPoint(bottom_right.x() - 10, bottom_right.y())
        if index.column() == 0:
            bottom_left = QPoint(bottom_left.x() + 10, bottom_right.y())
        painter.drawLine(bottom_left, bottom_right)

    def sizeHint(self, option, index):
        # set proper width for each column
        if index.isValid() and self.parent() is not None:
            widths = (0.05, 0.1, 0.25, 0.1, 0.2, 0.3)
            width = self.parent().width()
            w = int(width * widths[index.column()])
            h = option.rect.height()
            return QSize(w, h)
        return super().sizeHint(option, index)

    def editorEvent(self, event, model, option, index):
        super().editorEvent(event, model, option, index)
        return False

    def updateEditorGeometry(self, editor, option, index):
        if index.column() != Column.artist:
            super().updateEditorGeometry(editor, option, index)


class MovieFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None, text=''):
        super().__init__(parent)
        self.text = text

    def filter_by_text(self, text):
        self.text = text or ''
        # Empty Text means show all movies
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.text:
            return super().filterAcceptsRow(source_row, source_parent)

        source_model = self.sourceModel()
        index = source_model.index(source_row, Column.MOVIE, parent=source_parent)
        movie = index.data(Qt.UserRole)
        text = self.text.lower()
        ctx = movie.title_display.lower() + movie.date_display.lower() + movie.staffs_display.lower()
        return text in ctx


class MoviesTableView(ItemViewNoScrollMixin, QTableView):
    play_song_needed = pyqtSignal([object])
    add_to_list_needed = pyqtSignal(list)

    show_poster_needed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        QTableView.__init__(self, parent)

        # override ItemViewNoScrollMixin variables
        self._least_row_count = 6
        self._row_height = 40

        # slot functions
        self.remove_song_func = None

        self.delegate = MoviesTableDelegate(self)
        self.setItemDelegate(self.delegate)
        self.about_to_show_menu = Signal()

        self._setup_ui()

    def _setup_ui(self):
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # FIXME: PyQt5 seg fault
        # self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(self._row_height)
        self.setWordWrap(False)
        self.setTextElideMode(Qt.ElideRight)
        self.setMouseTracking(True)
        self.setEditTriggers(QAbstractItemView.SelectedClicked)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setShowGrid(False)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragOnly)

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

        # .. versionadded: v3.7
        #   The context key *models*
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

    def show_poster_by_url(self, index):
        self.show_poster_needed(self.model().data(index, Qt.UserRole).photo_url)
