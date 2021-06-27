import os


def read_qss_resource(filename):
    filepath = os.path.abspath(__file__)
    dirname = os.path.dirname(filepath)
    qss_filepath = os.path.join(dirname, '../themes/{}'.format(filename))
    with open(qss_filepath, encoding='UTF-8') as f:
        s = f.read()
    return s


def get_icon_resource(iconname):
    filepath = os.path.abspath(__file__)
    dirname = os.path.dirname(filepath)
    return os.path.join(dirname, '../icon/{}'.format(iconname))
