import itertools
import logging

from PyQt5.QtCore import pyqtSignal, QModelIndex, QAbstractListModel, QSize, Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import QApplication

from poster_ocr.gui.util import aio

logger = logging.getLogger(__name__)


class ReaderFetchMoreMixin:
    """
    The class should implement

    1. _reader
    2. _items
    3. _fetch_more_step
    4. _is_fetching
    """
    no_more_item = pyqtSignal()

    def canFetchMore(self, _=None):
        return self.can_fetch_more()

    def fetchMore(self, _=None):
        if self._is_fetching is False:
            self._is_fetching = True
            self.fetch_more_impl()

    def can_fetch_more(self, _=None):
        reader = self._reader

        count, offset = reader.count, reader.offset
        if count is not None:
            return count > offset + 1

        # The reader sets the count when it has no more items,
        # so it is safe to return True here
        return True

    def fetch_more_impl(self):
        """fetch more items from reader
        """
        reader = self._reader
        step = self._fetch_more_step

        if reader.is_async:
            async def fetch():
                items = []
                count = 0
                async for item in reader:
                    items.append(item)
                    count += 1
                    if count == step:
                        break
                return items
            future = aio.create_task(fetch())
            future.add_done_callback(self._async_fetch_cb)
        else:
            try:
                items = list(itertools.islice(reader, step))
            except:
                logger.exception('fetch more items failed')
                self._fetch_more_cb(None)
            else:
                self._fetch_more_cb(items)

    def on_items_fetched(self, items):
        begin = len(self._items)
        end = begin + len(items) - 1
        self.beginInsertRows(QModelIndex(), begin, end)
        self._items.extend(items)
        self.endInsertRows()

    def _fetch_more_cb(self, items):
        self._is_fetching = False
        if items is None:
            return
        self.on_items_fetched(items)

    def _async_fetch_cb(self, future):
        try:
            items = future.result()
        except:  # noqa
            logger.exception('async fetch more items failed')
            self._fetch_more_cb(None)
        else:
            self._fetch_more_cb(items)


class ItemViewNoScrollMixin:
    """
    `no_scroll_v` means that the itemview's size(height) is always enough to hold
    all fetched items. When new items are fetched, the itemview size is
    automatically adjueted.

    The itemview with no_scroll_v=True is usually used with an outside ScrollArea.
    """
    def __init__(self, *args, no_scroll_v=True, row_height=0, least_row_count=0,
                 reserved=30, **kwargs):
        """
        :params no_scroll_v: enable on no_scroll_v feature or not

        .. versionadded:: 3.7.8
           The *row_height*, *least_row_count*, *reserved* parameter were added.
        """
        self._least_row_count = least_row_count
        self._row_height = row_height
        self._reserved = reserved

        self._min_height = 0

        self._no_scroll_v = no_scroll_v

    def initialize(self):
        """
        .. versionadded:: 3.7.7
        """
        if self._no_scroll_v is True:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    # def set_no_scroll_v(self, no_scroll_v):
    #     """
    #     .. versionadded:: 3.7.7
    #     """
    #     self._no_scroll_v = no_scroll_v
    #     if no_scroll_v is True:
    #         self.adjust_height()
    #         self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def adjust_height(self):
        if self.model() is None:
            return

        if self.model().canFetchMore(QModelIndex()):
            # according to QAbstractItemView source code,
            # qt will trigger fetchMore when the last row is
            # inside the viewport, so we always hide the last
            # two row to ensure fetch-more will not be
            # triggered automatically
            index = self._last_index()
            rect = self.visualRect(index)
            height = self.sizeHint().height() - int(rect.height() * 1.5) - self._reserved
            self.setFixedHeight(max(height, self.min_height()))
        else:
            height = self.sizeHint().height()
            self.setFixedHeight(height)
        self.updateGeometry()

    def on_rows_changed(self, *args):
        if self._no_scroll_v is True:
            self.adjust_height()

    def setModel(self, model):
        super().setModel(model)
        if model is None:
            return
        model.rowsInserted.connect(self.on_rows_changed)
        model.rowsRemoved.connect(self.on_rows_changed)
        if isinstance(model, QSortFilterProxyModel):
            srcModel = model.sourceModel()
            if isinstance(srcModel, ReaderFetchMoreMixin):
                srcModel.no_more_item.connect(self.on_rows_changed)
        self.on_rows_changed()

    def wheelEvent(self, e):
        if self._no_scroll_v is True:
            if abs(e.angleDelta().x()) > abs(e.angleDelta().y()):
                QApplication.sendEvent(self.horizontalScrollBar(), e)
            else:
                e.ignore()  # let parents handle it
        else:
            super().wheelEvent(e)

    def sizeHint(self):
        super_size_hint = super().sizeHint()
        if self._no_scroll_v is False:
            return super_size_hint

        height = min_height = self.min_height()
        if self.model() is not None:
            index = self._last_index()
            rect = self.visualRect(index)
            height = rect.y() + rect.height() + self._reserved
            height = max(min_height, height)
        return QSize(super_size_hint.width(), height)

    def _last_index(self):
        source_model = self.model()
        row_count = source_model.rowCount()
        if isinstance(source_model, QAbstractListModel):
            column_count = 1
        else:
            column_count = source_model.columnCount()
        # can't use createIndex here, why?
        return source_model.index(row_count - 1, column_count - 1)

    def min_height(self):
        default = self._row_height * self._least_row_count + self._reserved
        return max(self._min_height, default)

    def suggest_min_height(self, height):
        """
        parent should call this method where it's size changed
        """
        self._min_height = height
