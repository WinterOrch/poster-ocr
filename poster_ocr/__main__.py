from PyQt5.QtWidgets import QApplication

from poster_ocr.gui.client_widget import ClientWidget


def main():
    import sys
    app = QApplication(sys.argv)
    app.setStyle("macintosh")

    application_window = ClientWidget()
    application_window.resize(1600, 900)
    application_window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
