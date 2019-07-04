from gui.custom_frame import CustomFrame
from tkinter import *
from tkinter import ttk
from observer import Observer
from ipfs_fs import IPFSDirectory

import threading
import time
import logging


class Main(CustomFrame, Observer):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._controller = controller

        self.root_dir_label = Label(self, text="")
        self.root_dir_label.pack()

        self.listbox = Listbox(self, width=38, height=12, activestyle=NONE)
        self.listbox.bind('<Double-Button-1>', self._on_double_click)
        self.listbox.pack()

        Label(self, text="").pack()

        self.listbox_content = {}

        self.progress_bar = ttk.Progressbar(self, orient=HORIZONTAL, length=230, mode='indeterminate')
        self.progress_bar.pack()

        Label(self, text="").pack()

        self.ipfs_label = Label(self, text="")
        self.ipfs_label.pack()

        self.sync_label = Label(self, text="")
        self.sync_label.pack()

        self.add_root_dir_label = Label(self, text="", width=50)
        self.add_root_dir_label.pack()

        self._logger = logging.getLogger()

    def update(self):
        self._populate_listbox(self._controller.get_content_tree())

    def on_raised(self):
        self._controller.attach(self)
        sync_var = self._controller.get_frame(self.prev).sync_var.get()
        add_root_dir_var = self._controller.get_frame(self.prev).add_root_dir_var.get()
        start_thread = threading.Thread(target=self._start_thread, args=(sync_var, add_root_dir_var))
        start_thread.start()

    def _start_thread(self, sync=False, add_root_dir=False):
        start_time = time.time()

        self.progress_bar.start(interval=20)

        self.ipfs_label.configure(text="Starting IPFS...")
        self._controller.init_ipfs()
        self.ipfs_label.configure(text="IPFS ready")

        if sync:
            self.sync_label.configure(text="Synchronizing...")
            self._controller.synchronize()
            self.sync_label.configure(text="Synchronized")

        if add_root_dir:
            self.add_root_dir_label.configure(text="Adding root directory to IPFS-Drive...")
            self._controller.add_root_dir(start_time)
            self.add_root_dir_label.configure(text="Added root directory to IPFS-Drive")

        self._populate_listbox(self._controller.get_content_tree())

        self.progress_bar.stop()

        self._controller.init_event_monitoring()

        self._controller.start_listening_for_changes()

        while True:
            time.sleep(1)

    def _populate_listbox(self, root_dir):
        listbox = self.listbox
        listbox.delete('0', 'end')
        idx = 1
        self.listbox_content.clear()

        listbox.insert(0, '<<')
        self.listbox_content[0] = root_dir.parent

        for file in root_dir.files + root_dir.dirs:
            listbox.insert(idx, file.name)
            self.listbox_content[idx] = file
            idx += 1

    def _on_double_click(self, *args):
        try:
            idx = self.listbox.curselection()[0]
            if isinstance(self.listbox_content[idx], IPFSDirectory):
                self._populate_listbox(self.listbox_content[idx])
        except Exception as exc:
            self._logger.error(exc)
