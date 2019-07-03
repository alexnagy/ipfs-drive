from gui.authentication import Authentication
from gui.registration import Registration
from requests import HTTPError

import logging
import json


class RegistrationController:
    def __init__(self, root, firebase_auth):
        self._root = root
        self._fbs_auth = firebase_auth

        self._logger = logging.getLogger()

        self._root.get_frame(Registration).sign_up_button.config(command=self._sign_up)
        
    def _sign_up(self):
        email = self._root.current_frame.email_var.get()
        password = self._root.current_frame.password_var.get()
        repeat_password = self._root.current_frame.repeat_password_var.get()

        if password != repeat_password:
            self._root.current_frame.show_error("Passwords do not match!")

        try:
            self._fbs_auth.create_user_with_email_and_password(email, password)
            self._root.current_frame.show_info("Registration completed successfully!")
            self._root.show_frame(Authentication)
        except HTTPError as http_err:
            reason = json.loads(http_err.args[1])['error']['message']
            if reason == 'EMAIL_EXISTS':
                self._root.current_frame.show_error("An account with this e-mail already exists!")
            elif reason == 'INVALID_EMAIL':
                self._root.current_frame.show_error("The e-mail address is invalid!")
            elif reason.startswith('WEAK_PASSWORD'):
                self._root.current_frame.show_error("Password should be at least 6 characters!")
            else:
                self._logger.error(reason)