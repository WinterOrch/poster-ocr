import logging

from PyQt5.QtWidgets import QApplication

from poster_ocr.gui.client_widget import ClientWidget


def set_logger():
    logging.basicConfig(filename='../log/' + __name__ + '.log',
                        format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]', level=logging.DEBUG,
                        filemode='a', datefmt='%Y-%m-%d %I:%M:%S %p')


def main():
    import sys
    app = QApplication(sys.argv)
    app.setStyle("macintosh")

    set_logger()

    application_window = ClientWidget()
    application_window.resize(1600, 900)
    application_window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
