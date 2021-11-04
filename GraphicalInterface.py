import os
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from tkinter import messagebox

from pygments.lexers.dotnet import CSharpLexer
import pyroprompt
create_prompt = pyroprompt.create_prompt
from os.path import exists
from ModObject import *
import pyro

window_count = 0
can_make_menu = True


def set_window_count(x):
    global window_count
    window_count = x


def get_window_count():
    global window_count
    return window_count


def close(menu):
    global can_make_menu
    can_make_menu = True
    try:
        menu.root.destroy()
    except TclError:
        pass


class InterfaceMenu:

    def __init__(self):
        global can_make_menu
        if not can_make_menu:
            return
        can_make_menu = False
        self.root = Tk()
        self.root.configure(background="#00062A")
        self.root.geometry("460x280")
        self.root.resizable(0, 0)
        self.root.title("Unity Mod Maker - Main Menu")
        self.root.iconbitmap("resources/unitymodmaker.ico")
        self.frame = Frame(width=220)
        self.input = Entry(self.frame, background="#4A3EAB", font=("Arial", 18))
        self.input.pack(fill="x")
        self.frame.place(x=20, y=18, width=420)
        self.new_image = PhotoImage(file="resources/newbutton.png")
        self.open_image = PhotoImage(file="resources/openbutton.png")
        self.new_button = Label(self.root, image=self.new_image, background="#00062A")
        self.open_button = Label(self.root, image=self.open_image, background="#00062A")
        self.new_button.place(x=20, y=280-220)
        self.open_button.place(x=240, y=280-220)
        self.new_button.bind("<Button-1>", self.new)
        self.open_button.bind("<Button-1>", self.load)

        self.input.bind('<Return>', self.enter)

        pyro.add_window(self.root)

    def enter(self, e):
        mod_name = e.widget.get()
        no_space = mod_name.replace(" ", "")
        try:
            mod = load(os.getcwd() + "/projects/" + no_space + "/" + no_space + ".umm")
        except FileNotFoundError:
            mod = ModObject(no_space)
        close(self)
        pyro.CoreUI(lexer=CSharpLexer(), filename=no_space, mod=mod)

    def new_fallback(self, name):
        name = name[0]
        if exists(os.getcwd() + "/projects/" + name.replace(" ", "")):
            return "Project Already Exists"
        mod = ModObject(name.replace(" ", ""))
        close(self)
        pyro.CoreUI(lexer=CSharpLexer(), filename=name.replace(" ", ""), mod=mod)

    def new(self, e):
        create_prompt("New Mod", ("Mod Name",), self.new_fallback, None)

    def load_fallback(self, name):
        name = name[0]
        if not exists(os.getcwd() + "/projects/" + name.replace(" ", "")):
            return "Project Doesn't Exist"
        try:
            mod = load(os.getcwd() + "/projects/" + name.replace(" ", "") + "/" + name.replace(" ", "") + ".umm")
        except FileNotFoundError:
            return "Unity Mod Maker File Missing"
        close(self)
        pyro.CoreUI(lexer=CSharpLexer(), filename=name.replace(" ", ""), mod=mod)

    def load(self, e):
        create_prompt("Load Mod", ("Mod Name",), self.load_fallback, None,
                      warning="Never Open Mods From Untrusted Sources")


if __name__ == "__main__":
    InterfaceMenu()
    pyro.mainloop()
