from gui.main import Main
from gui.authentication import Authentication
from gui.registration import Registration
from tkinter import *


class GUI(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry("300x325")
        self.title("IPFS-Drive")

        mainframe = Frame(self)
        mainframe.pack(side="top", fill="both", expand=True)
        mainframe.grid_rowconfigure(0, weight=1)
        mainframe.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Main, Authentication, Registration):
            frame = F(master=mainframe)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.current_frame = None

        self.show_frame(Authentication)

    def show_frame(self, frame):
        self.current_frame = self.frames[frame]
        self.current_frame.tkraise()

    def get_frame(self, frame):
        return self.frames[frame]
