import base64


class Db:
    def __init__(self, firebase_db, uid, token):
        self._db = firebase_db
        self._uid = uid
        self._token = token

    def add_content(self, path, hash):
        b64_path = base64.b64encode(path.encode()).decode()
        self._db.child("content").child(self._uid).child(b64_path).set(hash, token=self._token)

    def remove_content(self, path):
        b64_path = base64.b64encode(path.encode()).decode()
        self._db.child("content").child(self._uid).child(b64_path).remove(token=self._token)

    def get_content(self):
        return self._db.child("content").child(self._uid).get(token=self._token).val()

    def get_stream(self, stream_handler):
        return self._db.child("content").child(self._uid).stream(stream_handler, token=self._token)
