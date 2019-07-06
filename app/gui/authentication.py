from gui.custom_frame import CustomFrame
from tkinter import *
from requests import HTTPError
from gui.start import Start
from gui.registration import Registration

import json


class Authentication(CustomFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

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

        self.sign_in_button = Button(self, text="Sign in", command=self._sign_in, width=15, height=1)
        self.sign_in_button.pack()

        Label(self, text="").pack()

        Label(self, text="Don't have an account?").pack()
        self.register_button = Button(self, text="Register", command=lambda: self._controller.show_frame(Registration),
                                      height=1, width=15)
        self.register_button.pack()

        Label(self, text="").pack()
        
    def _sign_in(self):
        email = self.email_var.get()
        password = self.password_var.get()

        try:
            response = self._controller.get_auth().sign_in_with_email_and_password(email, password)
            uid = response['localId']
            token = response['idToken']
            self._controller.init_db(uid, token)
            self._controller.show_frame(Start)
        except HTTPError as http_err:
            reason = json.loads(http_err.args[1])['error']['message']
            if reason == 'INVALID_EMAIL':
                self.show_error("The e-mail address is invalid!")
            elif reason == 'EMAIL_NOT_FOUND':
                self.show_error("No account with this e-mail found!")
            elif reason == 'INVALID_PASSWORD':
                self.show_error("The password is invalid!")
            else:
                self._logger.error(reason)