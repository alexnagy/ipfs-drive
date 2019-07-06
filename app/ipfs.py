import subprocess
import threading


class IPFS(subprocess.Popen):
    def __init__(self):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        super().__init__("ipfs daemon", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                         startupinfo=startupinfo, universal_newlines=True)
        self._ready = False
        self._lock = threading.Lock()
        threading.Thread(target=self._check_if_ready).start()

    def _check_if_ready(self):
        for stdout_line in iter(self.stdout.readline, ""):
            if "Daemon is ready" in stdout_line:
                self._lock.acquire()
                self._ready = True
                self._lock.release()
                break

    def is_ready(self):
        self._lock.acquire()
        is_ready = self._ready
        self._lock.release()
        return is_ready

    def __del__(self):
        self.terminate()
