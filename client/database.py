import base64


class Db:
    def __init__(self, firebase_db, uid):
        self._db = firebase_db
        self._uid = uid

    def add_content(self, path, hash):
        self._db.child("content").child(self._uid).child(base64.b64encode(path.encode()).decode()).set(hash)

    def add_content_list(self, content_list):
        for path, hash in content_list:
            self.add_content(path, hash)

    def remove_content(self, path):
        self._db.child("content").child(self._uid).child(base64.b64encode(path.encode()).decode()).remove()

    def get_content(self):
        return self._db.child("content").child(self._uid).get().val()
