from tkinter import messagebox

from pyroprompt import *
import pyro
from os.path import exists
import os
from ModObject import ModObject
import ModObject
from tkinter import *
from pygments.lexers.dotnet import CSharpLexer


def _new_fallback(name):
    name = name[0]
    if exists(os.getcwd() + "/projects/" + name.replace(" ", "")):
        return "Project Already Exists"
    mod = ModObject(name.replace(" ", ""))
    pyro.CoreUI(lexer=CSharpLexer(), filename=name.replace(" ", ""), mod=mod)


def new():
    create_prompt("New Mod", ("Mod Name",), _new_fallback, None)


def _open_fallback(name):
    name = name[0]
    if not exists(os.getcwd() + "/projects/" + name.replace(" ", "")):
        return "Project Doesn't Exist"
    try:
        mod = ModObject.load(os.getcwd() + "/projects/" + name.replace(" ", "") + "/" + name.replace(" ", "") + ".umm")
    except FileNotFoundError:
        return "Unity Mod Maker File Missing"
    pyro.CoreUI(lexer=CSharpLexer(), filename=name.replace(" ", ""), mod=mod)


def open():
    create_prompt("Load Mod", ("Mod Name",), _open_fallback, None)


def save(mod, filename):
    current_directory = os.getcwd()
    folder_path = os.path.join(current_directory, "projects/"+filename)
    try:
        os.mkdir(folder_path)
    except FileExistsError:
        pass
    ModObject.save(mod, location=folder_path + "/" + filename + ".umm")


def _copy_fallback(mod, name):
    name = name[0]
    ModObject.copy(mod, name)


def copy(mod):
    create_prompt("Copy Mod", ("New Mod Name",), partial(_copy_fallback, mod), None)


def build_install(mod):
    root = Tk()
    root.title("Please Wait...")
    root.iconbitmap("resources/unitymodmaker.ico")
    root.configure(background="#618dcf")
    Label(root, text="Please Wait...", font=("Arial", 20), background="#618dcf").pack(padx=20, pady=20)
    root.update()
    if mod.install(destroyonerror=root):
        root.destroy()
        messagebox.showinfo("Success", "Mod Successfully Installed")


def export_cs(mod):
    return


def export_dotnet(mod):
    return
