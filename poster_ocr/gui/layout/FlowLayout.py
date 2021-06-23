from PyQt5.QtCore import Qt, QRect, QSize, QPoint
from PyQt5.QtWidgets import QLayout, QSizePolicy


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
            self.setSpacing(spacing)
            self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
            margin, _, _, _ = self.getContentsMargins()
            size += QSize(2 * margin, 2 * margin)
        return size

    def doLayout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0

        for item in self.itemList:
            wid = item.widget()
            space_x = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton,
                                                                 QSizePolicy.PushButton, Qt.Horizontal)
            space_y = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton,
                                                                 QSizePolicy.PushButton, Qt.Vertical)

            next_x = x + item.sizeHint().width() + space_x

            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
                x = next_x
                line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()