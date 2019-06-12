import json

from tkinter import *
from tkinter import messagebox
from requests.exceptions import HTTPError


class Registration(Frame):
    def __init__(self, parent, controller, firebase_auth):
        super().__init__(parent)
        self._controller = controller
        self._firebase_auth = firebase_auth

        Label(self, text="Please enter details below to register").pack()
        Label(self, text="").pack()

        self._username = StringVar()
        self._password = StringVar()
        self._repeat_password = StringVar()

        Label(self, text="Username:").pack()
        Entry(self, textvariable=self._username).pack()
        
        Label(self, text="Password:").pack()
        Entry(self, textvariable=self._password, show='*').pack()

        Label(self, text="Repeat password:").pack()
        Entry(self, textvariable=self._repeat_password, show='*').pack()
        
        Label(self, text="").pack()
        Button(self, text="Register", width=10, height=1, command=self._signup).pack()

    def _signup(self):
        if self._repeat_password.get() != self._password.get():
            messagebox.showerror("Error", "Passwords do not match!")
            return

        try:
            self._firebase_auth.create_user_with_email_and_password(self._username.get(), self._password.get())
            messagebox.showinfo("Success", "Registration completed successfully!")
            self._controller.show_frame("Authentication")
        except HTTPError as http_err:
            reason = json.loads(http_err.args[1])['error']['message']
            print(reason)
            if reason == 'EMAIL_EXISTS':
                messagebox.showerror("Error", "An account with this e-mail already exists!")
            elif reason == 'INVALID_EMAIL':
                messagebox.showerror("Error", "The e-mail address is invalid!")
            elif reason.startswith('WEAK_PASSWORD'):
                messagebox.showerror("Error", "Password should be at least 6 characters!")
        
        
class Authentication(Frame):
    def __init__(self, parent, controller, firebase_auth):
        super().__init__(parent)
        self._controller = controller
        self._firebase_auth = firebase_auth

        Label(self, text="Please enter details below to login").pack()
        Label(self, text="").pack()

        self._username = StringVar()
        self._password = StringVar()

        Label(self, text="Username:").pack()
        Entry(self, textvariable=self._username).pack()
        
        Label(self, text="").pack()

        Label(self, text="Password:").pack()
        Entry(self, textvariable=self._password, show='*').pack()
        
        Label(self, text="").pack()

        Button(self, text="Login", width=10, height=1, command=self._login).pack()

        Label(self, text="").pack()

        Label(self, text="Don't have an account?").pack()
        Button(self, text="Register", height=1, width=10, command=lambda: controller.show_frame("Registration")).pack()

        Label(self, text="").pack()

    def _login(self):
        try:
            user = self._firebase_auth.sign_in_with_email_and_password(self._username.get(), self._password.get())
            self._uid = user['localId']
            self._controller.show_frame("StartPage")
        except HTTPError as http_err:
            reason = json.loads(http_err.args[1])['error']['message']
            print(reason)
            if reason == 'INVALID_EMAIL':
                messagebox.showerror("Error", "No account with this e-mail found!")
            elif reason == 'INVALID_PASSWORD':
                messagebox.showerror("Error", "The password is invalid!")
