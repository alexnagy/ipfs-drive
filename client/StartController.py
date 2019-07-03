from gui.start import Start

import time
import os
import threading


class StartController:
    def __init__(self, root):
        self._root = root

        self._root.get_frame(Start).start_button.config(command=self._start)
        
    def _start(self):
        if not self._root.current_frame.root_dir_var.get():
            self._root.current_frame.show_error("Root dir can not be empty!")
            return

        if not self._root.current_frame.encryption_password_var.get():
            self._root.current_frame.show_error("Error", "Encryption password can not be empty!")
            return

        self._start_time = time.time()

        self._root_dir_path = self._root.current_frame.root_dir_var.get().replace(os.sep, '/')
        if not os.path.exists(self._root_dir_path):
            os.makedirs(self._root_dir_path)

        self._content = Content(self._root_dir_path, self._db)

        self._cipher.create_key(self._root.current_frame.encryption_password_var.get())

        start_thread = threading.Thread(target=self._start_thread, args=(self._root.current_frame.sync_var.get(),
                                                                         self._root.current_frame.add_root_dir_var.get()))
        start_thread.start()