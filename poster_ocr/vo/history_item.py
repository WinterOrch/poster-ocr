import time


class HistoryItemInfo:
    def __init__(self, cover_dir: str, cover_title: str, history_time: time):
        self.cover_dir = cover_dir
        self.cover_title = cover_title
        self.history_time = history_time
