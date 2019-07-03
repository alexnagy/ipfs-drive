import json
import time
import os
import threading
import shutil
import ctypes
import logging
import base64

from firebase import Firebase
from requests.exceptions import HTTPError
from ipfs import IPFS
from ipfs_client import IPFSClient
from ipfs_cluster import IPFSCluster
from database import Db
from content import Content
from sync import Sync
from encryption.aes_cipher import AESCipher
from event_handler import EventHandler
from watchdog.observers import Observer
from file import File
from directory import Directory
from gui.gui import *
from ipfs_fs import IPFSDirectory, IPFSFile, walk


class Controller:
    def __init__(self):
        self._working_dir_path = None
        self._create_working_dir()

        config = json.load(open("firebase.cfg"))
        self._firebase = Firebase(config)
        self._auth = self._firebase.auth()
        self._db = None
        self._ipfs = None
        self._root_dir_path = None
        self._encryption_password = None
        self._content = None
        self._event_observer = None
        self._start_time = None
        self._sync = None

        self._logger = logging.getLogger()

        self._cipher = AESCipher()
        self._ipfs_client = IPFSClient(self._cipher, self._working_dir_path)
        self._ipfs_cluster = IPFSCluster()

        self.root = GUI()

        self.root.get_frame(Start).start_button.config(command=self.start)

        self.root.get_frame(Authentication).sign_in_button.config(command=self.sign_in)
        self.root.get_frame(Authentication).register_button.config(command=lambda: self.root.show_frame(Registration))

        self.root.get_frame(Registration).sign_up_button.config(command=self.sign_up)

        self.root.get_frame(Main).listbox.bind('<Double-Button-1>', self.on_double_click)

        self.listbox_content = {}


        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.root.mainloop()

    def sign_in(self):
        email = self.root.current_frame.email_var.get()
        password = self.root.current_frame.password_var.get()

        try:
            response = self._auth.sign_in_with_email_and_password(email, password)
            uid = response['localId']
            token = response['idToken']
            self._db = Db(self._firebase.database(), uid, token)
            self.root.show_frame(Start)
        except HTTPError as http_err:
            reason = json.loads(http_err.args[1])['error']['message']
            if reason == 'INVALID_EMAIL':
                self.root.current_frame.show_error("The e-mail address is invalid!")
            elif reason == 'EMAIL_NOT_FOUND':
                self.root.current_frame.show_error("No account with this e-mail found!")
            elif reason == 'INVALID_PASSWORD':
                self.root.current_frame.show_error("The password is invalid!")
            else:
                self._logger.error(reason)

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
            else:
                self._logger.error(reason)

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

        start_thread = threading.Thread(target=self._start_thread, args=(self.root.current_frame.sync_var.get(),
                                                                         self.root.current_frame.add_root_dir_var.get()))
        start_thread.start()

    def _start_thread(self, sync=False, add_root_dir=False):
        self.root.show_frame(Main)

        self.root.current_frame.progress_bar.pack()
        self.root.current_frame.progress_bar.start(interval=20)

        self._start_ipfs()

        if sync:
            self._synchronize()

        if add_root_dir:
            self._add_root_dir()

        self._populate_listbox()

        self.root.current_frame.progress_bar.stop()

        self._start_event_observer()

        while True:
            time.sleep(1)

    def _start_ipfs(self):
        self.root.current_frame.ipfs_label.pack()
        self.root.current_frame.ipfs_label.configure(text="Starting IPFS...")

        self._ipfs = IPFS()
        while not self._ipfs.is_ready():
            time.sleep(0.5)

        self.root.current_frame.ipfs_label.configure(text="IPFS ready")

    def _synchronize(self):
        self.root.current_frame.sync_label.pack()
        self.root.current_frame.sync_label.configure(text="Synchronizing...")

        self._sync = Sync(self._root_dir_path, self._working_dir_path, self._content, self._db, self._ipfs_client, self._cipher)
        self._sync.start()

        self.root.current_frame.sync_label.config(text="Synchronized")

    def _start_event_observer(self):
        event_handler = EventHandler(self._ipfs_client, self._ipfs_cluster, self._content, self._root_dir_path)
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
            self.root.current_frame.add_root_dir_label.configure(text="Adding %s to IPFS-Drive..." % full_path)
            if os.path.isfile(full_path):
                file = File(full_path)
                hash = self._ipfs_client.add_file(file)
                self._content.add(file.path, hash)
            elif os.path.isdir(full_path):
                content_list = self._ipfs_client.add_dir(Directory(full_path))
                self._content.add_list(content_list)
            self._ipfs_cluster.pin(self._content[full_path])

        self.root.current_frame.add_root_dir_label.configure(text="Added root directory to IPFS-Drive")

    def _on_closing(self):
        if self.root.current_frame.close():
            if self._event_observer:
                self._event_observer.stop()
                self._event_observer.join()
            if self._sync:
                self._sync.stop()
            shutil.rmtree(self._working_dir_path)
            self.root.destroy()

    def on_double_click(self, event):
        listbox = self.root.current_frame.listbox
        idx = listbox.curselection()[0]

        if isinstance(self.listbox_content[idx], IPFSDirectory):
            self.populate(self.listbox_content[idx])

    def _populate_listbox(self):
        db_content = self._db.get_content()
        # idx = 0
        # for k, v in db_content.items():
        #     name = base64.b64decode(k).decode()
        #     if '.' in name:
        #         file = IPFSFile(name, v)
        #     else:
        #         file = IPFSDirectory(name, v)
        #         walk(file)
        #
        #     self.listbox_content[idx] = file
        #     self.root.current_frame.listbox.insert(idx, file.name)
        #
        #     idx += 1

        root_dir = IPFSDirectory('.', None)
        for k, v in db_content.items():
            name = base64.b64decode(k).decode()
            if '.' in name:
                file = IPFSFile(name, v, root_dir)
                root_dir.add_file(file)
            else:
                dir = IPFSDirectory(name, v, root_dir)
                walk(dir)
                root_dir.add_dir(dir)

        self.populate(root_dir)

    def populate(self, root_dir):
        listbox = self.root.current_frame.listbox
        listbox.delete('0', 'end')
        idx = 1
        self.listbox_content.clear()

        listbox.insert(0, '<<')
        self.listbox_content[0] = root_dir.parent

        for file in root_dir.files + root_dir.dirs:
            listbox.insert(idx, file.name)
            self.listbox_content[idx] = file
            idx += 1
