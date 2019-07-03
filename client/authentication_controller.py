from gui.start import Start
from gui.authentication import Authentication
from gui.registration import Registration
from database import Db
from requests import HTTPError

import logging
import json


class AuthenticationController:
    def __init__(self, root, firebase_db, firebase_auth):
        self._root = root
        self._fbs_db = firebase_db
        self._fbs_auth = firebase_auth

        self._db = None
        
        self._logger = logging.getLogger()

        self._root.get_frame(Authentication).sign_in_button.config(command=self._sign_in)
        self._root.get_frame(Authentication).register_button.config(command=lambda: self._root.show_frame(Registration))
    
    def _sign_in(self):
        email = self._root.current_frame.email_var.get()
        password = self._root.current_frame.password_var.get()

        try:
            response = self._fbs_auth.sign_in_with_email_and_password(email, password)
            uid = response['localId']
            token = response['idToken']
            self._db = Db(self._fbs_db, uid, token)
            self._root.show_frame(Start)
        except HTTPError as http_err:
            reason = json.loads(http_err.args[1])['error']['message']
            if reason == 'INVALID_EMAIL':
                self._root.current_frame.show_error("The e-mail address is invalid!")
            elif reason == 'EMAIL_NOT_FOUND':
                self._root.current_frame.show_error("No account with this e-mail found!")
            elif reason == 'INVALID_PASSWORD':
                self._root.current_frame.show_error("The password is invalid!")
            else:
                self._logger.error(reason)
