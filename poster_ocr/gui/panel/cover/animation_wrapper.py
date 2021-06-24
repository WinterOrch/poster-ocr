from PyQt5.QtCore import Qt, QParallelAnimationGroup, QPoint, QPropertyAnimation, QEasingCurve, QRectF, pyqtProperty
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QColor
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication

BUBBLE_MIN_WIDTH = 200
BUBBLE_MIN_HEIGHT = 800

BUBBLE_WRAPPER_RADIUS = 3

BACKGROUND_COLOR = QColor(195, 195, 195)
BORDER_COLOR = QColor(150, 150, 150)


class BubbleWrapperWidget(QWidget):
    """Bubble Widget displaying cover for crawled movies

    Attributes:
        display:    QLabel which holds the cover graphic
        des_pos:    Position where the bubble widget should stay after entrance
    """

    def __init__(self, des_pos: QPoint, parent=None, style_sheet=None):
        super(BubbleWrapperWidget, self).__init__(parent=parent)

        if style_sheet is not None:
            self.setStyleSheet(style_sheet)

        # Set Borderless
        self.setWindowFlags(
            Qt.Window | Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        # Set Min Width and Height
        self.setMinimumSize(BUBBLE_MIN_WIDTH, BUBBLE_MIN_HEIGHT)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._layout = QVBoxLayout(self)
        self._loadGraph = None
        self._label = None

        self._pos = des_pos

        self._animationGroup = QParallelAnimationGroup(self)
        self._isAnimated = False

        self._desktop = QApplication.instance().desktop()

    def _setup_ui(self):
        self._layout.setContentsMargins(2, 2, 2, 2)

        if self._label is not None:
            self._layout.addWidget(self._label)

    def set_loading(self, display: QSvgWidget):
        self._loadGraph = display
        self._loadGraph.setVisible(False)
        self._layout.addWidget(self._loadGraph)

    def switch_label(self, display: QLabel):
        for i in range(self._layout.count()):
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
        duration = 600
        self.move(start_position)
        if isinstance(self._loadGraph, QSvgWidget):
            self._loadGraph.setVisible(True)
        self.move_animation(start_position, end_position, dura_mov=duration,
                            start_opa=0.0, end_opa=1.0, dura_opa=duration)

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
            self._isAnimated = True
            self._animationGroup.finished.connect(self.animation_finished)
            self._animationGroup.start()

    def animation_finished(self):
        self._isAnimated = False

    def quickly_fade_away(self, duration):
        """Quickly fade away when called to be terminated
        """
        self._animationGroup = QParallelAnimationGroup(self)
        opacity_anima = QPropertyAnimation(self, b"opacity")
        opacity_anima.setStartValue(1.0)
        opacity_anima.setEndValue(0.0)
        opacity_anima.setEasingCurve(QEasingCurve.InQuad)
        opacity_anima.setDuration(duration)

        move_anima = QPropertyAnimation(self, b"pos")
        move_anima.setStartValue(self._pos)
        move_anima.setEndValue(QPoint(self._pos.x() - 80, self._pos.y()))
        move_anima.setEasingCurve(QEasingCurve.InQuad)
        move_anima.setDuration(duration)

        self._animationGroup.addAnimation(opacity_anima)
        self._animationGroup.addAnimation(move_anima)
        self._animationGroup.finished().connect(self.close)
        self._animationGroup.start()

    def terminate(self):
        if self._isAnimated:
            self.stop_animation()   # TODO 暴力关闭，可以优化为快速结束
        else:
            self.quickly_fade_away(300)

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
        painter.setPen(QPen(BORDER_COLOR, 1, Qt.SolidLine,
                            Qt.RoundCap, Qt.RoundJoin))
        # 背景画刷
        painter.setBrush(BACKGROUND_COLOR)
        # 绘制形状
        painter.drawPath(rect_path)
        # 三角形底边绘制一条线保证颜色与背景一样
        painter.setPen(QPen(BACKGROUND_COLOR, 1,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(8, y, 8, 12)

    def windowOpacity(self) -> float:
        return super(BubbleWrapperWidget, self).windowOpacity()

    def setWindowOpacity(self, level: float) -> None:
        super(BubbleWrapperWidget, self).setWindowOpacity(level)

    opacity = pyqtProperty(float, windowOpacity, setWindowOpacity)
