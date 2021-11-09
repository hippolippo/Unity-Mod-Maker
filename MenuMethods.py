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


# This function is used to make the loading screens for Building the mod and for generating the Dotnet files
def create_loading_screen(message="Please Wait..."):
    # Visuals
    root = Tk()
    root.title("Please Wait...")
    root.iconbitmap("resources/unitymodmaker.ico")
    root.configure(background="#00062A")
    # The text it shows it provided via the message parameter
    x = Label(root, text=message, font=("Arial", 20), background="#00062A", fg="#b4d9f9")
    x.pack(padx=20, pady=20)
    # This isn't added to the pyro list of windows because it will be deleted before the next visual tick anyway
    # (Visuals freeze during these build methods) - This could be "fixed" by running the build method in a
    # different thread but it isn't necessary to allow them to edit the mod while it is installing
    root.update()
    # it returns x so that you can update the loading text while it is doing one task
    # it returns root so you can destroy it when you are done
    return root, x


# See the new function, this is the function that gets called when the prompt from the new function has "done"
# clicked
def _new_fallback(data):
    # first item in the list is the name of the mod
    name = data[0]
    # check if there is a directory that corresponds to a mod with this name
    # (spaces aren't included in the file names)
    if exists(os.getcwd() + "/projects/" + name.replace(" ", "")):
        # When the fallback to a prompt returns something, the prompt will show that as an error message and
        # keep itself open effectively asking them again
        return "Project Already Exists"
    # Decide whether the mod should use polytech
    poly_tech = data[3]
    if poly_tech.lower() == "true":
        poly_tech = True
    elif poly_tech.lower() == "false":
        poly_tech = False
    else:
        poly_tech = data[1] == "Poly Bridge 2"
    # creates a new mod with this name and information from the prompt
    mod = ModObject(name, poly_tech=poly_tech, game=data[1], folder_name=None if data[2] == "" else data[2],
                    steampath=data[4])
    # creates a pyro window which will have syntax highlighting for CSharp and will be editing our mod object
    pyro.CoreUI(lexer=CSharpLexer(), filename=name.replace(" ", ""), mod=mod)


# This gets called when the "new" button is pressed so it creates a prompt asking for the name of the new mod and
# calls self.new_fallback when they press "done", None means that if they press "cancel" nothing specific is done
def new():
    create_prompt("New Mod", ("Mod Name",
                              "Game Name (Check Spelling and Punctuation)",
                              "Name of Folder in Steam Files (If different from Game Name)",
                              "PolyTech (Poly Bridge Modding Framework)",
                              "Steam Directory"), _new_fallback, None, defaults={
        "Game Name (Check Spelling and Punctuation)": "Poly Bridge 2",
        "PolyTech (Poly Bridge Modding Framework)": "Auto",
        "Steam Directory": "C:\\Program Files (x86)\\Steam\\steamapps\\common\\"
    })


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
    create_prompt("Load Mod", ("Mod Name",), _open_fallback, None, warning="Never Open Mods From Untrusted Sources")


# This gets called when they press the save button on the menubar (and later when they do ctrl+s)
def save(window, filename):
    # directory this programming is running in
    current_directory = os.getcwd()
    # this is the directory for the mod
    folder_path = os.path.join(current_directory, "projects/" + filename)
    try:
        # try to make the project folder because it might not exist
        os.mkdir(os.path.join(current_directory, "projects"))
    except FileExistsError:
        # it already exists so it is fine, you can continue
        pass
    try:
        # try to make the mod directory (it's in the project folder which is why we needed to make sure that existed)
        os.mkdir(folder_path)
    except FileExistsError:
        # it already exists so we are good
        pass
    # calls the save method on the mod object now that we made sure all the correct folders existed
    ModObject.save(window.mod, location=folder_path + "/" + filename + ".umm")


def _copy_fallback(window, name):
    name = name[0]
    ModObject.copy(window.mod, name)


def copy(window):
    create_prompt("Copy Mod", ("New Mod Name",), partial(_copy_fallback, window), None)


def build_install(window):
    root, text = create_loading_screen()

    def set_text(x):
        text.configure(text=x)
        root.update()

    if window.mod.install(destroyonerror=root, progress_updater=set_text):
        root.destroy()
        messagebox.showinfo("Success", "Mod Successfully Installed")


def export_cs(window):
    return


def export_dotnet(window, independent=True):
    root = create_loading_screen("Generating Dotnet Files...")[0]
    if ModObject.create_files(window.mod, destroyonerror=root) is not None:
        if independent:
            root.destroy()
            messagebox.showinfo("Success", "Files Created Successfully")
        return root


def _change_name_fallback(window, name):
    ChangeManager.log_action(window.mod, True)
    window.mod.set_mod_name(name[0])
    window.refresh(False)


def change_mod_name(window):
    create_prompt("Rename Mod", ("New Name",), partial(_change_name_fallback, window), None)


def _change_version_fallback(window, name):
    ChangeManager.log_action(window.mod, True)
    window.mod.set_version(name[0])
    window.refresh(False)


def change_mod_version(window):
    create_prompt("Change Mod Version", ("New Version",), partial(_change_version_fallback, window), None)


def _harmony_patch_fallback(window, values):
    # def create_harmony_patch(self, in_class, method, prefix=True, parameters=list(), have_instance=True, result=None):
    scroll_data = window.text.yview()
    ChangeManager.log_action(window.mod, True)
    window.mod.create_harmony_patch(values[1], values[0], prefix=values[3] == "Prefix", parameters=values[2].split(","),
                                    have_instance=values[5] != "False",
                                    result=values[4] if values[4] != "None" else None)
    window.refresh(False)
    window.text.yview_moveto(scroll_data[0])


def create_harmony_patch(window):
    create_prompt("Create Harmony Patch", ("Function Name", "Function's Class", "Parameters (separate by comma)",
                                           "Prefix/Postfix", "Return Type", "Have Instance?"),
                  partial(_harmony_patch_fallback, window), None,
                  defaults={"Prefix/Postfix": "Prefix", "Return Type": "None", "Have Instance?": "False"})


def _config_item_fallback(window, values):
    scroll_data = window.text.yview()
    ChangeManager.log_action(window.mod, True)
    window.mod.add_config(values[0], values[1], values[2], values[3], values[4])
    window.refresh(False)
    window.text.yview_moveto(scroll_data[0])


def create_config_item(window):
    create_prompt("Create Config Item", ("Variable Name", "Data Type (e.g. int)", "Default Value (C# formatting)",
                                         "Definition (Name in List)", "Description (Info When Hovered Over)"),
                  partial(_config_item_fallback, window), None)
