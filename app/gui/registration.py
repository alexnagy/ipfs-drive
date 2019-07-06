from gui.custom_frame import CustomFrame
from tkinter import *
from requests import HTTPError

import json


class Registration(CustomFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        Label(self, text="Please enter details below to register").pack()
        Label(self, text="").pack()

        self.email_var = StringVar()
        self.password_var = StringVar()
        self.repeat_password_var = StringVar()

        Label(self, text="E-mail:").pack()
        Entry(self, textvariable=self.email_var, width=40).pack()

        Label(self, text="Password:").pack()
        Entry(self, textvariable=self.password_var, show='*', width=40).pack()

        Label(self, text="Repeat password:").pack()
        Entry(self, textvariable=self.repeat_password_var, show='*', width=40).pack()

        Label(self, text="").pack()
        self.sign_up_button = Button(self, text="Sign up", command=self._sign_up, width=15, height=1)
        self.sign_up_button.pack()
        
    def _sign_up(self):
        email = self.email_var.get()
        password = self.password_var.get()
        repeat_password = self.repeat_password_var.get()

        if password != repeat_password:
            self.show_error("Passwords do not match!")

        try:
            self._controller.get_auth().create_user_with_email_and_password(email, password)
            self.show_info("Registration completed successfully!")
            self._controller.show_frame(self.next)
        except HTTPError as http_err:
            reason = json.loads(http_err.args[1])['error']['message']
            if reason == 'EMAIL_EXISTS':
                self.show_error("An account with this e-mail already exists!")
            elif reason == 'INVALID_EMAIL':
                self.show_error("The e-mail address is invalid!")
            elif reason.startswith('WEAK_PASSWORD'):
                self.show_error("Password should be at least 6 characters!")
            else:
                self._logger.error(reason)