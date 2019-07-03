from gui.custom_frame import CustomFrame
from tkinter import *
from tkinter import ttk


class Start(CustomFrame):
    def __init__(self, master):
        super().__init__(master)
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

        self.start_button = Button(self, text="Start", height=1, width=15)
        self.start_button.pack()


