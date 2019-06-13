import ctypes
import os

from controller import Controller
from gui.gui import GUI


def create_working_dir():
    working_dir_path = os.path.join(os.getcwd(), "working_dir")
    if not os.path.exists(working_dir_path):
        os.mkdir(working_dir_path)
        ctypes.windll.kernel32.SetFileAttributesW(working_dir_path, 2)
    return working_dir_path


if __name__ == '__main__':
    working_dir_path = create_working_dir()
    c = Controller(working_dir_path)
