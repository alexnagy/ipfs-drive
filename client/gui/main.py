from gui.custom_frame import CustomFrame
from tkinter import *
from tkinter import ttk


class Main(CustomFrame):
    def __init__(self, master):
        super().__init__(master)
        self.root_dir_label = Label(self, text="")

        self.listbox = Listbox(self, width=40, height=15, activestyle=NONE)
        self.listbox.pack()

        self.progress_bar = ttk.Progressbar(self, orient=HORIZONTAL, length=230, mode='indeterminate')

        Label(self, text="").pack()

        self.ipfs_label = Label(self, text="")
        self.add_root_dir_label = Label(self, text="", width=50)
        self.sync_label = Label(self, text="")
