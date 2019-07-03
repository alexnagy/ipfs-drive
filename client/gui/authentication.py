from gui.custom_frame import CustomFrame
from tkinter import *


class Authentication(CustomFrame):
    def __init__(self, master):
        super().__init__(master)

        Label(self, text="Please enter details below to login").pack()
        Label(self, text="").pack()

        self.email_var = StringVar()
        self.password_var = StringVar()

        Label(self, text="E-mail:").pack()
        Entry(self, textvariable=self.email_var, width=40).pack()

        Label(self, text="").pack()

        Label(self, text="Password:").pack()
        Entry(self, textvariable=self.password_var, show='*', width=40).pack()

        Label(self, text="").pack()

        self.sign_in_button = Button(self, text="Sign in", width=15, height=1)
        self.sign_in_button.pack()

        Label(self, text="").pack()

        Label(self, text="Don't have an account?").pack()
        self.register_button = Button(self, text="Register", height=1, width=15)
        self.register_button.pack()

        Label(self, text="").pack()