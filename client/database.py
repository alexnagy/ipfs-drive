import json
import base64

from firebase import Firebase


class Db:
    def __init__(self, email, password):
        config = json.load(open("firebase.cfg"))
        firebase = Firebase(config)
        auth = firebase.auth()
        self._user = auth.sign_in_with_email_and_password(email, password)
        self._db = firebase.database()

    def add_content(self, path, hash):
        self._db.child("content").child(self._user["localId"]).child(base64.b64encode(path.encode()).decode()).set(hash)

    def add_content_list(self, content_list):
        for path, hash in content_list:
            self.add_content(path, hash)

    def remove_content(self, path):
        self._db.child("content").child(self._user["localId"]).child(base64.b64encode(path.encode()).decode()).remove()

    def get_content(self):
        return self._db.child("content").child(self._user["localId"]).get().val()
