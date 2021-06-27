import requests
from PyQt5.QtGui import QPixmap


class DoubanMovieInfo:
    def __init__(self, movie_title: str, staffs_display: str, photo_url: str, show_time: str, rate: str, other_des: dict):
        self.title_display = movie_title
        self.staffs_display = staffs_display

        self.photo_url = photo_url
        self.date_display = show_time
        self.rate_display = rate
        self.description_display = other_des

    def load_photo(self) -> QPixmap:
        req = requests.get(self.photo_url)
        photo = QPixmap()
        photo.loadFromData(req.content)
        return photo
