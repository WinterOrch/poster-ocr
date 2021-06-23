from PyQt5.QtCore import Qt, QParallelAnimationGroup, QPoint, QPropertyAnimation, QEasingCurve, QRectF
from PyQt5.QtGui import QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication

BUBBLE_MIN_WIDTH = 200
BUBBLE_MIN_HEIGHT = 80

BUBBLE_WRAPPER_RADIUS = 3

BACKGROUND_COLOR = QColor()


class BubbleWrapperWidget(QWidget):
    def __init__(self, display: QLabel, des_pos: QPoint, parent=None):
        super(BubbleWrapperWidget, self).__init__(parent=parent)

        with open('../qss/QListWidgetQSS.qss', 'r') as f:
            self.list_style = f.read()

        # Set Borderless
        self.setWindowFlags(
            Qt.Window | Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        # Set Min Width and Height
        self.setMinimumSize(BUBBLE_MIN_WIDTH, BUBBLE_MIN_HEIGHT)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._layout = QVBoxLayout(self)
        self._label = display

        self._pos = des_pos

        self._animationGroup = QParallelAnimationGroup(self)

        self._desktop = QApplication.instance().desktop()

    def _setup_ui(self):
        self._layout.setContentsMargins(2, 2, 2, 2)
        self._layout.addWidget(self._label)

    def switch_label(self, display: QLabel):
        for item in range(self._layout.count()):
            self._layout.itemAt(i).widget().deleteLater()

        self._label = display
        self._layout.addWidget(self._label)

    def stop_animation(self):
        self.hide()
        self._animationGroup.stop()
        self.close()

    def show(self):
        super(BubbleWrapperWidget, self).show()
        # 开始位置
        start_position = QPoint(self._pos.x() - 80, self._pos.y())
        end_position = QPoint(self._pos.x(), self._pos.y())
        self.move(start_position)

    def move_animation(self, start_pos: QPoint, end_pos: QPoint, dura_mov=2000,
                       start_opa=0.0, end_opa=0.0, dura_opa=2000):
        self._animationGroup = None

        if start_opa != end_opa:
            opacity_anima = QPropertyAnimation(self, b"opacity")
            opacity_anima.setStartValue(start_opa)
            opacity_anima.setEndValue(end_opa)

            opacity_anima.setEasingCurve(QEasingCurve.InQuad)
            opacity_anima.setDuration(dura_opa)

            self._animationGroup = QParallelAnimationGroup(self)
            self._animationGroup.addAnimation(opacity_anima)

        if not (start_pos.x() != end_pos.y() or start_pos.y() != end_pos.y()):
            move_anima = QPropertyAnimation(self, b"pos")
            move_anima.setStartValue(start_pos)
            move_anima.setEndValue(end_pos)
            move_anima.setEasingCurve(QEasingCurve.InQuad)
            move_anima.setDuration(dura_mov)

            if self._animationGroup is None:
                self._animationGroup = QParallelAnimationGroup(self)

            self._animationGroup.addAnimation(move_anima)

        if self._animationGroup is not None:
            self._animationGroup.start()

    def paintEvent(self, a0) -> None:
        super(BubbleWrapperWidget, self).paintEvent(a0)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect_path = QPainterPath()  # Rectangle
        tri_path = QPainterPath()   # Triangle

        width = self.width() - 8
        rect_path.addRoundedRect(QRectF(8, 0, width, self.height()), BUBBLE_WRAPPER_RADIUS, BUBBLE_WRAPPER_RADIUS)
        y = self.height() / 4 * 1
        tri_path.moveTo(8, y)

        # Draw
        tri_path.lineTo(0, y + 6)
        tri_path.lineTo(8, y + 12)

        rect_path.addPath(tri_path)

        # 边框画笔
        painter.setPen(QPen(, 1, Qt.SolidLine,
                            Qt.RoundCap, Qt.RoundJoin))
        # 背景画刷
        painter.setBrush(self.BackgroundColor)
        # 绘制形状
        painter.drawPath(rectPath)
        # 三角形底边绘制一条线保证颜色与背景一样
        painter.setPen(QPen(self.BackgroundColor, 1,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(x, height, x + 12, height)
