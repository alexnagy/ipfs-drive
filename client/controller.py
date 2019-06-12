import json
import time
import os
import threading
import shutil
import ctypes

from firebase import Firebase
from requests.exceptions import HTTPError
from ipfs import IPFS
from ipfs_client import IPFSClient
from database import Db
from content import Content
from sync import Sync
from encryption.aes_cipher import AESCipher
from event_handler import EventHandler
from watchdog.observers import Observer
from file import File
from directory import Directory
from gui.app import *

from tkinter import Label


class Controller:
    def __init__(self):
        self._working_dir_path = None
        self._create_working_dir()

        config = json.load(open("firebase.cfg"))
        self._firebase = Firebase(config)
        self._auth = self._firebase.auth()
        self._db = None
        self._uid = None
        self._ipfs = None
        self._root_dir_path = None
        self._encryption_password = None
        self._content = None
        self._event_observer = None

        self._cipher = AESCipher()
        self._ipfs_client = IPFSClient(self._cipher, self._working_dir_path)

        self.root = App()

        self.root.get_frame(Main).start_button.config(command=self.start)

        self.root.get_frame(Authentication).sign_in_button.config(command=self.sign_in)
        self.root.get_frame(Authentication).register_button.config(command=lambda: self.root.show_frame(Registration))

        self.root.get_frame(Registration).sign_up_button.config(command=self.sign_up)

        self.root.mainloop()

    def sign_in(self):
        email = self.root.current_frame.email_var.get()
        password = self.root.current_frame.password_var.get()

        try:
            response = self._auth.sign_in_with_email_and_password(email, password)
            self._uid = response['localId']
            self.root.show_frame(Main)
        except HTTPError as http_err:
            reason = json.loads(http_err.args[1])['error']['message']
            if reason == 'INVALID_EMAIL':
                self.root.current_frame.show_error("No account with this e-mail found!")
            elif reason == 'INVALID_PASSWORD':
                self.root.current_frame.show_error("The password is invalid!")

        self._db = Db(self._firebase.database(), self._uid)

    def sign_up(self):
        email = self.root.current_frame.email_var.get()
        password = self.root.current_frame.password_var.get()
        repeat_password = self.root.current_frame.repeat_password_var.get()

        if password != repeat_password:
            self.root.current_frame.show_error("Passwords do not match!")

        try:
            self._auth.create_user_with_email_and_password(email, password)
            self.root.current_frame.show_info("Registration completed successfully!")
            self.root.show_frame(Authentication)
        except HTTPError as http_err:
            reason = json.loads(http_err.args[1])['error']['message']
            if reason == 'EMAIL_EXISTS':
                self.root.current_frame.show_error("An account with this e-mail already exists!")
            elif reason == 'INVALID_EMAIL':
                self.root.current_frame.show_error("The e-mail address is invalid!")
            elif reason.startswith('WEAK_PASSWORD'):
                self.root.current_frame.show_error("Password should be at least 6 characters!")

    def start(self):
        if not self.root.current_frame.root_dir_var.get():
            self.root.current_frame.show_error("Root dir can not be empty!")
            return

        if not self.root.current_frame.encryption_password_var.get():
            self.root.current_frame.show_error("Error", "Encryption password can not be empty!")
            return

        self._start_time = time.time()

        self._root_dir_path = self.root.current_frame.root_dir_var.get().replace(os.sep, '/')

        self._content = Content(self._root_dir_path, self._db)

        self._cipher.create_key(self.root.current_frame.encryption_password_var.get())

        self.root.current_frame.progress_bar.pack()
        self.root.current_frame.progress_bar.start(interval=20)

        start_thread = threading.Thread(target=self._start_thread)
        start_thread.start()
        # start_thread.join()

        # while start_thread.is_alive():
        #     print("Am I stuck here?")
        #     time.sleep(0.5)

        # self._start_event_observer()
        #
        # try:
        #     while True:
        #         time.sleep(1)
        # except KeyboardInterrupt:
        #     self._event_observer.stop()
        #
        # self._event_observer.join()
        #
        # shutil.rmtree(self._working_dir_path)

    def _start_thread(self):
        self._start_ipfs()

        if self.root.current_frame.sync_var.get() == 1:
            self._sync()

        if self.root.current_frame.add_root_dir_var.get() == 1:
            self._add_root_dir()

        self.root.current_frame.progress_bar.stop()

        self._start_event_observer()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self._event_observer.stop()

        self._event_observer.join()

        shutil.rmtree(self._working_dir_path)

    def _start_ipfs(self):
        self.root.current_frame.ipfs_label.pack()
        self.root.current_frame.ipfs_label.configure(text="Starting IPFS...")

        self._ipfs = IPFS()
        while not self._ipfs.is_ready():
            time.sleep(0.5)

        self.root.current_frame.ipfs_label.configure(text="IPFS ready")

    def _sync(self):
        self.root.current_frame.sync_label.pack()
        self.root.current_frame.sync_label.configure(text="Synchronizing...")

        Sync(self._root_dir_path, self._working_dir_path, self._db, self._ipfs_client, self._cipher).sync()

        self.root.current_frame.sync_label.config(text="Synchronized")

    def _start_event_observer(self):
        event_handler = EventHandler(self._ipfs_client, self._content, self._root_dir_path)
        self._event_observer = Observer()
        self._event_observer.schedule(event_handler, self._root_dir_path, recursive=True)
        self._event_observer.start()

    def _create_working_dir(self):
        self._working_dir_path = os.path.join(os.getcwd(), "working_dir")
        if not os.path.exists(self._working_dir_path):
            os.mkdir(self._working_dir_path)
            ctypes.windll.kernel32.SetFileAttributesW(self._working_dir_path, 2)

    def _add_root_dir(self):
        self.root.current_frame.add_root_dir_label.pack()
        self.root.current_frame.add_root_dir_label.configure(text="Adding root directory to IPFS-Drive...")

        for path in os.listdir(self._root_dir_path):
            full_path = os.path.join(self._root_dir_path, path).replace(os.sep, '/')
            if os.path.getctime(full_path) >= self._start_time:
                continue
            if os.path.isfile(full_path):
                file = File(full_path)
                hash = self._ipfs_client.add_file(file)
                self._content.add(file.path, hash)
            elif os.path.isdir(full_path):
                content_list = self._ipfs_client.add_dir(Directory(full_path), recursive=True)
                self._content.add_list(content_list)

        self.root.current_frame.add_root_dir_label.configure(text="Added root directory to IPFS-Drive")
