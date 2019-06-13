from gui.custom_frame import CustomFrame
from tkinter import *


class Registration(CustomFrame):
    def __init__(self, master):
        super().__init__(master)

        Label(self, text="Please enter details below to register").pack()
        Label(self, text="").pack()

        self.email_var = StringVar()
        self.password_var = StringVar()
        self.repeat_password_var = StringVar()

        Label(self, text="E-mail:").pack()
        Entry(self, textvariable=self.email_var, width=30).pack()

        Label(self, text="Password:").pack()
        Entry(self, textvariable=self.password_var, show='*', width=30).pack()

        Label(self, text="Repeat password:").pack()
        Entry(self, textvariable=self.repeat_password_var, show='*', width=30).pack()

        Label(self, text="").pack()
        self.sign_up_button = Button(self, text="Sign up", width=10, height=1)
        self.sign_up_button.pack()