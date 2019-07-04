from gui.start import Start
from gui.main import Main
from gui.authentication import Authentication
from gui.registration import Registration
from tkinter import *

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
from ipfs_fs import IPFSDirectory, IPFSFile, walk
from firebase import Firebase

import json
import time
import os
import shutil
import ctypes
import logging
import base64


class IPFSDrive(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry("300x350")
        self.title("IPFS-Drive")

        mainframe = Frame(self)
        mainframe.pack(side="top", fill="both", expand=True)
        mainframe.grid_rowconfigure(0, weight=1)
        mainframe.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (Start, Main, Authentication, Registration):
            frame = F(parent=mainframe, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.frames[Registration].next = Authentication
        self.frames[Start].next = Main
        self.frames[Main].prev = Start

        self.current_frame = None

        self.protocol("WM_DELETE_WINDOW", self.exit)

        self._working_dir_path = None
        self.init_working_dir()

        config = json.load(open("firebase.cfg"))
        self._firebase = Firebase(config)
        self._auth = self._firebase.auth()
        self._db = None
        self._ipfs = None
        self._root_dir_path = None
        self._encryption_password = None
        self._content = None
        self._event_observer = None
        self._sync = None

        self._logger = logging.getLogger()

        self._cipher = AESCipher()
        self._ipfs_client = IPFSClient(self._cipher, self._working_dir_path)
        self._ipfs_cluster = IPFSCluster()

        self.show_frame(Authentication)

    def show_frame(self, frame):
        self.current_frame = self.frames[frame]
        self.current_frame.tkraise()
        if isinstance(self.current_frame, Main):
            self.current_frame.on_raised()

    def get_frame(self, frame):
        return self.frames[frame]

    def get_auth(self):
        return self._firebase.auth()

    def get_content(self):
        return self._content

    def set_root_dir_path(self, root_dir_path):
        self._root_dir_path = root_dir_path.replace(os.sep, '/')

    def init_working_dir(self):
        self._working_dir_path = os.path.join(os.getcwd(), "working_dir")
        if not os.path.exists(self._working_dir_path):
            os.mkdir(self._working_dir_path)
            ctypes.windll.kernel32.SetFileAttributesW(self._working_dir_path, 2)

    def init_db(self, uid, token):
        self._db = Db(self._firebase.database(), uid, token)

    def init_content(self):
        self._content = Content(self._root_dir_path, self._db)

    def init_cipher_key(self, encryption_password):
        self._cipher.create_key(encryption_password)

    def init_ipfs(self):
        self._ipfs = IPFS()
        while not self._ipfs.is_ready():
            time.sleep(0.5)

    def init_sync(self):
        self._sync = Sync(self._root_dir_path, self._working_dir_path, self._content, self._db, self._ipfs_client,
                          self._cipher)

    def init_event_monitoring(self):
        event_handler = EventHandler(self._ipfs_client, self._ipfs_cluster, self._content, self._root_dir_path)
        self._event_observer = Observer()
        self._event_observer.schedule(event_handler, self._root_dir_path, recursive=True)
        self._event_observer.start()

    def synchronize(self):
        self._sync.start()

    def start_listening_for_changes(self):
        self._sync.start_listening()

    def add_root_dir(self, start_time):
        for path in os.listdir(self._root_dir_path):
            full_path = os.path.join(self._root_dir_path, path).replace(os.sep, '/')
            if os.path.getctime(full_path) >= start_time:
                continue
            if os.path.isfile(full_path):
                file = File(full_path)
                hash = self._ipfs_client.add_file(file)
                self._content.add(file.path, hash)
            elif os.path.isdir(full_path):
                content_list = self._ipfs_client.add_dir(Directory(full_path))
                self._content.add_list(content_list)
            self._ipfs_cluster.pin(self._content[full_path])

    def get_content_tree(self):
        db_content = self._db.get_content()

        root_dir = IPFSDirectory('.', None)

        if db_content is None:
            return root_dir

        for k, v in db_content.items():
            name = base64.b64decode(k).decode()
            if '.' in name:
                file = IPFSFile(name, v, root_dir)
                root_dir.add_file(file)
            else:
                dir = IPFSDirectory(name, v, root_dir)
                walk(dir)
                root_dir.add_dir(dir)

        return root_dir

    def attach(self, obj):
        self._content.attach(obj)
        self._logger.debug("Attached to content")
        if self._sync:
            self._sync.attach(obj)
            self._logger.debug("Attached to sync")

    def run(self):
        self.mainloop()

    def exit(self):
        if self.current_frame.close():
            if self._event_observer:
                self._event_observer.stop()
                self._event_observer.join()
            if self._sync:
                self._sync.stop()
            shutil.rmtree(self._working_dir_path)
            self.destroy()
