from firebase import Firebase
import json
import time


def stream_handler(message):
    print(message)


if __name__ == '__main__':
    config = json.load(open("firebase.cfg"))
    fb = Firebase(config)
    auth = fb.auth()
    resp = auth.sign_in_with_email_and_password('alexandru.nagy@gmail.com', 'ipfsdrive')

    uid = resp['localId']
    token = resp['idToken']

    db = fb.database()

    my_stream = db.child("content").child(uid).stream(stream_handler, token=token)
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        my_stream.close()
