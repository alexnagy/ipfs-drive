from tkinter import Frame, messagebox

import logging


class CustomFrame(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller
        self._logger = logging.getLogger()
        self._next = None
        self._prev = None

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, next):
        self._next = next

    @property
    def prev(self):
        return self._prev

    @prev.setter
    def prev(self, prev):
        self._prev = prev

    def show_next(self):
        self._controller.show_frame(self._next)

    def show_prev(self):
        self._controller.show_frame(self._prev)

    @staticmethod
    def show_info(message):
        messagebox.showinfo("Info", message)

    @staticmethod
    def show_error(message):
        messagebox.showerror("Error", message)

    @staticmethod
    def close():
        return messagebox.askokcancel("Quit", "Are you sure you want to quit?")
