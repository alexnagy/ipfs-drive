from tkinter import *
from tkinter import ttk
from ipfs_test import IPFSDirectory, walk

main = Tk()
main.title("IPFS-Drive Content")
main.geometry("350x350")
frame = ttk.Frame(main, padding=(3, 3, 12, 12))
frame.grid(column=0, row=0, sticky=(N, S, E, W))

lstbox = Listbox(frame, width=20, height=10)
lstbox.pack()

root_dir = IPFSDirectory('.', r'QmQjYkCuDmxbJ9uQpEGmKTtjAf1raXgr6kGaPGspZnHqGF')
walk(root_dir)
content = {}

def populate(root_dir):
    lstbox.delete('0', 'end')
    idx = 1
    content.clear()

    lstbox.insert(0, '<<')
    content[0] = root_dir.parent

    for file in root_dir.files + root_dir.dirs:
        lstbox.insert(idx, file.name)
        content[idx] = file
        idx += 1

def select(event):
    sel_idx = lstbox.curselection()[0]

    if isinstance(content[sel_idx], IPFSDirectory):
        populate(content[sel_idx])



populate(root_dir)

lstbox.bind('<Double-Button-1>', select)

main.mainloop()