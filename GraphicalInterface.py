from tkinter import messagebox, simpledialog

from ModObject import *
from tkinter import *
from functools import partial


class ResizingCanvas(Canvas):
    def __init__(self, parent, **kwargs):
        Canvas.__init__(self, parent, **kwargs)
        self.parent = parent
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self, x, y, labels):
        # determine the ratio of old width/height to new width/height
        wscale = float(x)/self.width
        hscale = float(x)/self.height
        self.width = x-40
        self.height = y-40
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, wscale, hscale)


class Window:
    def __init__(self, mod):

        self.root = Tk()
        self.root.geometry("1080x720")
        self.pointer = mod
        self.tree = [mod]
        self.back = Button(self.root, text="Back", command=self.back)
        self.back.pack()
        self.frame = Frame(self.root)

    def back(self):
        if len(self.tree) <= 1:
            return
        self.tree.pop()
        self.pointer = self.tree[-1]
        self.draw_pointer()

    def draw_pointer(self):
        self.frame.destroy()
        self.frame = Frame(self.root)
        self.canvas = ResizingCanvas(self.frame)
        scrollbar = Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        scrollbar.config(command=self.canvas.yview)
        scrollbar2 = Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        scrollbar2.config(command=self.canvas.xview)
        scrollable_frame = Frame(self.canvas)
        self.root.bind(
            "<Configure>",
            lambda e: configured(self, e)
        )
        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set, xscrollcommand=scrollbar2.set)
        block_list = self.pointer.get_block_list()
        self.labels = list()
        self.buttons = list()
        i = 0
        j = 0
        for block in block_list:
            self.labels.append(Label(scrollable_frame, text=block, anchor="e", justify=LEFT, font=("Courier New", 10)))
            self.labels[-1].grid(sticky=W, row=i)
            i += 1
            self.buttons.append(Button(scrollable_frame, text="Enter Block ^", command=partial(enter, j)))
            self.buttons[-1].grid(sticky=W, row=i)
            j += 1
            i += 1
        self.frame.pack()
        scrollbar.pack(side="right", fill=Y)
        scrollbar2.pack(side="bottom", fill=X)
        self.canvas.pack(side="left", fill="both", expand=True)




def configured(window, e):
    window.canvas.configure(
        scrollregion=window.canvas.bbox("all")
    )
    window.canvas.on_resize(window.root.winfo_width(), window.root.winfo_height(),window.labels)

def enter(number):
    x.tree.append(x.pointer.get_list()[number])
    x.pointer = x.pointer.get_list()[number]
    x.draw_pointer()

root = Tk()
root.withdraw()
name = simpledialog.askstring("Mod Name", "What Is The Mod's Name? (Case Sensitive)")
no_space = name.replace(" ", "")
try:
    mod = load(os.getcwd()+"/"+no_space+"/"+no_space+".umm")
except FileNotFoundError:
    mod = ModObject(name)
x = Window(mod)
x.draw_pointer()
x.root.mainloop()