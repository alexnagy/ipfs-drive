from tkinter import Frame, messagebox


class CustomFrame(Frame):
    def __init__(self, master):
        super().__init__(master)

    @staticmethod
    def show_info(message):
        messagebox.showinfo("Info", message)

    @staticmethod
    def show_error(message):
        messagebox.showerror("Error", message)