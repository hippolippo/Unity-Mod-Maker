from tkinter import messagebox, simpledialog

from ModObject import *
from tkinter import *
from functools import partial
from pygments.lexers.dotnet import CSharpLexer
from pygments.styles import get_style_by_name


# TODO: Finish this and then implement it
class SmartCodeLine:

    def __init__(self, line, parent, container_list):
        self.line = line
        self.parent = parent
        self.container_list = container_list

    def add_line_after(self):
        self.parent.add_line_after(self.line)


class ResizingCanvas(Canvas):
    def __init__(self, parent, **kwargs):
        Canvas.__init__(self, parent, **kwargs)
        self.parent = parent
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self, x, y, labels):
        # determine the ratio of old width/height to new width/height
        wscale = float(x) / self.width
        hscale = float(x) / self.height
        self.width = x
        self.height = y
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
        self.menubar = Menu(root)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.menu = Menu(self.menubar, tearoff=0)
        '''self.filemenu.add_command(label="New", command=self.new)
        self.filemenu.add_command(label="Open", command=self.open)
        self.filemenu.add_command(label="Save", command=self.save)'''

    def back(self, update=True):
        if update:
            self.text_update()
        if len(self.tree) <= 1:
            return
        self.tree.pop()
        self.pointer = self.tree[-1]
        self.draw_pointer()

    def text_update(self):
        if type(self.pointer) is CodeLine:
            self.pointer.code = self.texts[0].get()
        if type(self.pointer) is CodeBlock:
            for i in enumerate(self.pointer.lines):
                i[1].code = self.texts[i[0]].get()

    def draw_pointer(self):
        self.frame.destroy()
        self.frame = Frame(self.root)
        self.canvas = ResizingCanvas(self.frame)
        scrollbar = Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        scrollbar.config(command=self.canvas.yview)
        scrollbar2 = Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        scrollbar2.config(command=self.canvas.xview)
        scrollable_frame = Frame(self.canvas)
        scrollable_frame.grid_columnconfigure(0, weight=1)
        self.root.bind(
            "<Configure>",
            lambda e: configured(self, e)
        )
        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set, xscrollcommand=scrollbar2.set)
        editable_text = False
        '''
        if type(self.pointer) is CodeLine:
            editable_text = True
        if type(self.pointer) is CodeBlock:
            editable_text = True
        '''
        block_list = self.pointer.get_block_list()
        self.labels = list()
        self.buttons = list()
        self.texts = list()
        i = 0
        j = 0
        for block in block_list:
            self.texts.append(StringVar(scrollable_frame, value=block[0]))
            if type(block[2]) is CodeLine and not block[1]:
                self.labels.append(Entry(scrollable_frame, font=("Courier New", 10), width=max(len(block[0]), 50),
                                         textvariable=self.texts[-1]))
                self.labels[-1].grid(sticky=W, row=i)
            else:
                self.labels.append(Label(scrollable_frame, text=self.texts[-1].get(), anchor="e", justify=LEFT,
                                         font=("Courier New", 10)))
                self.labels[-1].bind("<Button-1>", partial(enter_by_block, self, block[2]))
                self.labels[-1].grid(sticky=W, row=i)
            i += 1
            '''
            if not editable_text:
                self.buttons.append(Button(scrollable_frame, text="Enter Block ^", command=partial(enter_by_index, self, j)))
                self.buttons[-1].grid(sticky=W, row=i)
                i += 1
            '''
            j += 1

        self.frame.pack()
        scrollbar.pack(side="right", fill=Y)
        scrollbar2.pack(side="bottom", fill=X)
        self.canvas.pack(side="left", fill="both", expand=True)


def configured(window, e):
    window.canvas.configure(
        scrollregion=window.canvas.bbox("all")
    )
    window.canvas.on_resize(window.root.winfo_width(), window.root.winfo_height(), window.labels)


def enter_by_index(obj, number):
    obj.tree.append(obj.pointer.get_list()[number])
    obj.pointer = obj.pointer.get_list()[number]
    obj.draw_pointer()


def enter_by_block(obj, block, e):
    obj.tree.append(block)
    obj.pointer = block
    obj.draw_pointer()


root = Tk()
root.withdraw()
name = simpledialog.askstring("Mod Name", "What Is The Mod's Name? (Case Sensitive)")
no_space = name.replace(" ", "")
try:
    mod = load(os.getcwd() + "/" + no_space + "/" + no_space + ".umm")
except FileNotFoundError:
    mod = ModObject(name)
x = Window(mod)
x.draw_pointer()
x.root.mainloop()
