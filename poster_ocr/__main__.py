import logging, time

from PyQt5.QtWidgets import QApplication

from poster_ocr.gui.client_widget import ClientWidget
from vo.douban_movie import DoubanMovieInfo
from vo.history_item import HistoryItemInfo


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

    application_window.add_new_tags(["挺好挺好，整挺好", "不是吧不是吧，不会真的有人觉得挺好吧",
    "唉，你觉得挺好，那也不是不能挺好"])
    application_window.add_new_record_for_user(HistoryItemInfo(r"C:\Users\user\Pictures\PIXIVEL\[ArseniXC]57915845.jpg",
                                                               "好耶！", time.time()))
    application_window.add_new_record_for_user(HistoryItemInfo(r"C:\Users\user\Pictures\PIXIVEL\新建文件夹\["
                                                               r"雨傘ゆん]78838119.jpg",
                                                               "好耶！", time.time()))

    movie_list = [
        DoubanMovieInfo("Bastard Asshole", "张艺谋", "https://img1.doubanio.com/view/photo/s_ratio_poster/public/p2575043939.webp",
                        "2009-05-20(戛纳电影节)", "8.6", {}),
        DoubanMovieInfo("Fake it", "温子仁",
                        "https://img1.doubanio.com/view/photo/s_ratio_poster/public/p2575043939.webp",
                        "2009-05-20(戛纳电影节)", "8.6", {}),
        DoubanMovieInfo("Luuu", "姜文",
                        "https://img1.doubanio.com/view/photo/s_ratio_poster/public/p2575043939.webp",
                        "2009-05-20(戛纳电影节)", "8.6", {})
    ]

    try:
        application_window.display_douban_results(movie_list)
    except Exception as e:
        print(e)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
