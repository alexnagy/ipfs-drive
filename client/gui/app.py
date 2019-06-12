from tkinter import ttk, messagebox
from tkinter import *


class App(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry("300x310")
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


class MyCustomFrame(Frame):
    def __init__(self, master):
        super().__init__(master)

    @staticmethod
    def show_info(message):
        messagebox.showinfo("Info", message)

    @staticmethod
    def show_error(message):
        messagebox.showerror("Error", message)

    def add_label(self, text):
        label = Label(self, text=text)
        label.pack()
        return label


class Main(MyCustomFrame):
    def __init__(self, master):
        super().__init__(master)
        self.root_dir_var = StringVar()
        Label(self, text="Root directory:").pack()
        Entry(self, textvariable=self.root_dir_var, width=40).pack()

        Label(self, text="").pack()

        self.encryption_password_var = StringVar()
        Label(self, text="Encryption password:").pack()
        Entry(self, textvariable=self.encryption_password_var, width=40).pack()

        Label(self, text="").pack()

        self.add_root_dir_var = IntVar()
        Checkbutton(self, text="Add root directory to IPFS-Drive", variable=self.add_root_dir_var).pack()

        self.sync_var = IntVar()
        Checkbutton(self, text="Synchronize", variable=self.sync_var).pack()

        Label(self, text="").pack()

        self.start_button = Button(self, text="Start", height=1, width=10)
        self.start_button.pack()

        # Label(self, text="").pack()

        self.progress_bar = ttk.Progressbar(self, orient=HORIZONTAL, length=200, mode='indeterminate')

        Label(self, text="").pack()

        self.ipfs_label = Label(self, text="")
        self.add_root_dir_label = Label(self, text="")
        self.sync_label = Label(self, text="")


class Registration(MyCustomFrame):
    def __init__(self, master):
        super().__init__(master)

        Label(self, text="Please enter details below to register").pack()
        Label(self, text="").pack()

        self.email_var = StringVar()
        self.password_var = StringVar()
        self.repeat_password_var = StringVar()

        Label(self, text="E-mail:").pack()
        Entry(self, textvariable=self.email_var, width=30).pack()

        Label(self, text="Password:").pack()
        Entry(self, textvariable=self.password_var, show='*', width=30).pack()

        Label(self, text="Repeat password:").pack()
        Entry(self, textvariable=self.repeat_password_var, show='*', width=30).pack()

        Label(self, text="").pack()
        self.sign_up_button = Button(self, text="Sign up", width=10, height=1)
        self.sign_up_button.pack()


class Authentication(MyCustomFrame):
    def __init__(self, master):
        super().__init__(master)

        Label(self, text="Please enter details below to login").pack()
        Label(self, text="").pack()

        self.email_var = StringVar()
        self.password_var = StringVar()

        Label(self, text="E-mail:").pack()
        Entry(self, textvariable=self.email_var, width=30).pack()

        Label(self, text="").pack()

        Label(self, text="Password:").pack()
        Entry(self, textvariable=self.password_var, show='*', width=30).pack()

        Label(self, text="").pack()

        self.sign_in_button = Button(self, text="Sign in", width=10, height=1)
        self.sign_in_button.pack()

        Label(self, text="").pack()

        Label(self, text="Don't have an account?").pack()
        self.register_button = Button(self, text="Register", height=1, width=10)
        self.register_button.pack()

        Label(self, text="").pack()
