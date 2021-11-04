from tkinter import messagebox

from pyroprompt import *
import pyro
from os.path import exists
import os
from ModObject import ModObject
import ModObject
from tkinter import *
import ChangeManager
from pygments.lexers.dotnet import CSharpLexer


def create_loading_screen(message="Please Wait..."):
    root = Tk()
    root.title("Please Wait...")
    root.iconbitmap("resources/unitymodmaker.ico")
    root.configure(background="#00062A")
    x = Label(root, text=message, font=("Arial", 20), background="#00062A", fg="#b4d9f9")
    x.pack(padx=20, pady=20)
    root.update()
    return root, x

def _new_fallback(name):
    name = name[0]
    if exists(os.getcwd() + "/projects/" + name.replace(" ", "")):
        return "Project Already Exists"
    mod = ModObject.ModObject(name.replace(" ", ""))
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
        os.mkdir(os.path.join(current_directory, "projects"))
    except FileExistsError:
        pass
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
    root, text = create_loading_screen()

    def set_text(x):
        text.configure(text=x)
        root.update()
    if mod.install(destroyonerror=root, progress_updater=set_text):
        root.destroy()
        messagebox.showinfo("Success", "Mod Successfully Installed")


def export_cs(mod):
    return


def export_dotnet(mod, independent=True):
    root = create_loading_screen("Generating Dotnet Files...")[0]
    if ModObject.create_files(mod, destroyonerror=root) is not None:
        if independent:
            root.destroy()
            messagebox.showinfo("Success", "Files Created Successfully")
        return root

def _change_name_fallback(mod, window, name):
    ChangeManager.log_action(mod, True)
    mod.set_mod_name(name[0])
    window.refresh(False)

def change_mod_name(mod, window):
    create_prompt("Rename Mod", ("New Name",), partial(_change_name_fallback, mod, window), None)

def _change_version_fallback(mod, window, name):
    ChangeManager.log_action(mod, True)
    mod.set_version(name[0])
    window.refresh(False)

def change_mod_version(mod, window):
    create_prompt("Change Mod Version", ("New Version",), partial(_change_version_fallback, mod, window), None)

def _harmony_patch_fallback(mod, window, values):
    # def create_harmony_patch(self, in_class, method, prefix=True, parameters=list(), have_instance=True, result=None):
    ChangeManager.log_action(mod, True)
    mod.create_harmony_patch(values[1], values[0], prefix=values[3] == "Prefix", parameters=values[2].split(","),
                             have_instance=values[5] != "False",result=values[4] if values[4] != "None" else None)
    window.refresh(False)

def create_harmony_patch(mod, window):
    create_prompt("Create Harmony Patch", ("Function Name", "Function's Class", "Parameters (separate by comma)",
                                           "Prefix/Postfix", "Return Type", "Have Instance?"), partial(_harmony_patch_fallback, mod, window), None,
                  defaults={"Prefix/Postfix": "Prefix", "Return Type": "None", "Have Instance?": "False"})
