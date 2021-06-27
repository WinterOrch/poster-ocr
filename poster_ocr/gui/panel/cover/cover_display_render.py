from PyQt5.QtCore import QUrl, QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

import logging

from PyQt5.QtSvg import QSvgWidget

from poster_ocr.gui.animation.svg_icon import LoadingIcon
from poster_ocr.gui.panel.cover.animation_wrapper import BubbleWrapperWidget
from poster_ocr.gui.panel.cover.cover_label import CoverLabel
from poster_ocr.gui.util.excpetion import NetworkRequestingErrorException


class Render:
    def __init__(self, cache_path="../../../../cache/", parent=None):
        self._parent = parent

        self._existing_bubbles = {}

        self._na_manager = QNetworkAccessManager()
        self._na_manager.finished.connect(self.handle_response)

        self._current_filename = []
        self._current_url = []
        self._load_started = False

        self._cover_width = 250
        self._cover_height = 360

        self._cache_path = cache_path

    def pop_new_bubble(self, pos: QPoint, url: str):
        """Call all other existing bubbles to fade away and create a new one
        """
        for k in self._existing_bubbles.keys():
            item = self._existing_bubbles.pop(k)
            if isinstance(item, BubbleWrapperWidget):
                item.terminate()

        new_bubble = BubbleWrapperWidget(pos, parent=self._parent)
        self._existing_bubbles[url] = new_bubble
        load_widget = QSvgWidget(parent=new_bubble, minimumHeight=120, minimumWidth=120, visible=False)
        load_widget.load(LoadingIcon.grid())
        new_bubble.set_loading(load_widget)
        new_bubble.show()

        try:
            data_dir = self._cache_path + QUrl(url).fileName()
            f = open(data_dir)
            f.close()
            self.set_cover(url)
        except FileNotFoundError:
            # Start requesting for img
            self.do_request(url)

    def do_request(self, url: str):
        url_obj = QUrl(url)

        self._current_filename.append(self._cache_path + url_obj.fileName())
        self._current_url.append(url)
        req = QNetworkRequest(url_obj)

        logging.debug("Start request for {}", url)
        self._load_started = True
        self._na_manager.get(req)

    def handle_response(self, reply: QNetworkReply):
        self._load_started = False

        file_name = self._current_filename.pop(0)
        url = self._current_url.pop(0)
        error = reply.error()

        if error == QNetworkReply.NoError:
            self.save_file(reply.readAll().data(), file_name, url)
        else:
            logging.error("Request failed for {}", file_name)
            raise NetworkRequestingErrorException

        reply.deleteLater()
        del reply

    def save_file(self, data, write_dir, url):
        if data:
            f = open(write_dir, 'wb')
            with f:
                f.write(data)

            if data and write_dir and url:
                # Graphic is downloaded
                self.set_cover(write_dir, url)
        else:
            logging.error("Data fetching failed {}", write_dir)

    def set_cover(self, data_dir, url):
        """Replace SVG placeholder on Bubble with the picture for cover
        """
        if self._existing_bubbles.__contains__(url):
            bubble = self._existing_bubbles[url]
            assert isinstance(bubble, BubbleWrapperWidget)
            cover_label = CoverLabel(self._cover_width, self._cover_height, bubble, QPixmap(data_dir))
            bubble.switch_label(cover_label)
