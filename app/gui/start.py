from gui.custom_frame import CustomFrame
from tkinter import *

import time


class Start(CustomFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._controller = controller

        self.root_dir_var = StringVar()
        Label(self, text="Root directory:").pack()
        Entry(self, textvariable=self.root_dir_var, width=40).pack()

        Label(self, text="").pack()

        self.encryption_password_var = StringVar()
        Label(self, text="Encryption password:").pack()
        Entry(self, textvariable=self.encryption_password_var, show='*', width=40).pack()

        Label(self, text="").pack()

        self.repeat_encryption_password_var = StringVar()
        Label(self, text="Repeat encryption password:").pack()
        Entry(self, textvariable=self.repeat_encryption_password_var, show='*', width=40).pack()

        Label(self, text="").pack()

        self.add_root_dir_var = IntVar()
        Checkbutton(self, text="Add root directory to IPFS-Drive", variable=self.add_root_dir_var).pack()

        self.sync_var = IntVar()
        Checkbutton(self, text="Synchronize", variable=self.sync_var).pack()

        Label(self, text="").pack()

        self.start_button = Button(self, text="Start", command=self._start, height=1, width=15)
        self.start_button.pack()
        
    def _start(self):
        if not self.root_dir_var.get():
            self.show_error("Root dir can not be empty!")
            return

        if not self.encryption_password_var.get():
            self.show_error("Encryption password can not be empty!")
            return

        if self.encryption_password_var.get() != self.repeat_encryption_password_var.get():
            self.show_error("Encryption passwords do not match!")
            return

        self._controller.set_root_dir_path(self.root_dir_var.get())

        self._controller.init_content()

        self._controller.init_cipher_key(self.encryption_password_var.get())

        self._controller.init_sync()

        self._controller.show_frame(self.next)


