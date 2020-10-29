from tkinter import *
from tkinter.filedialog import *

filename = None

root = Tk()
text = Text(root, width=400, height=400)
menubar = Menu(root)
filemenu = Menu(menubar)

def openFile():
    with (f := askopenfile('r')):
        t = f.read()
        text.delete(0.0, END)
        text.insert(0.0, t)

def saveFile():
    with (f := asksaveasfile('w')):
        t = text.get(0.0, END)
        f.write(t.rstrip())

text.pack()

filemenu.add_command(label="Open", command=openFile)
filemenu.add_command(label="Save", command=saveFile)
filemenu.add_separator()
filemenu.add_command(label="Close", command=root.quit)

menubar.add_cascade(label="File", menu=filemenu)

root.title("Texedit")
root.minsize(width=400, height=400)
root.maxsize(width=400, height=400)
root.config(menu=menubar)
root.mainloop()