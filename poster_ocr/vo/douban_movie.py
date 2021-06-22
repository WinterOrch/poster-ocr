import requests
from PyQt5.QtGui import QPixmap


class DoubanMovieInfo:
    def __init__(self, movie_title: str, photo_url: str, show_time: str, other_des: dict):
        self.title = movie_title
        self.photo_url = photo_url
        self.show_time = show_time
        self.other_description = other_des

    def load_photo(self) -> QPixmap:
        req = requests.get(self.photo_url)
        photo = QPixmap()
        photo.loadFromData(req.content)
        return photo
