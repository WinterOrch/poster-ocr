from PyQt5 import QtQml
from PyQt5.QtCore import pyqtProperty, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtQuick import QQuickView


class MyClass(QObject):
    @pyqtSlot(str)  # 输入参数为str类型
    def output_str(self, string):
        print(string)


if __name__ == '__main__':
    import sys

    app = QGuiApplication(sys.argv)

    path = 'qml/application.qml'  # 加载的QML文件
    con = MyClass()

    engine = QQmlApplicationEngine()
    ctx = engine.rootContext()
    ctx.setContextProperty("qmlapp", engine)  # the string can be anything
    engine.load(path)
    win = engine.rootObjects()[0]
    win.show()

    app.exec_()
