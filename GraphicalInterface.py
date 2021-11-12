"""
This module is the main module of the entire program, running this file is how you start the application
It contains the code for the main menu which is what you are greeted with when you are using the program
"""

import os
from tkinter import messagebox, filedialog
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from functools import partial
import json

from pygments.lexers.dotnet import CSharpLexer
import pyroprompt

# Makes it easier to make a prompt
create_prompt = pyroprompt.create_prompt
from os.path import exists
from ModObject import *
import pyro

# keep track of the number of windows so you only open the main menu when the last one is closed
window_count = 0
# keep track of whether it should even open the main menu depending on if there is one already open (avoid more than one
# menu open at a time
can_make_menu = True

DEFAULT_SETTINGS = {
    "Default Game": "Poly Bridge 2",
    "Default Game Folder": "",
    "Default Steam Directory": "C:\\Program Files (x86)\\Steam\\steamapps\\common\\",


}


# These two functions are used to keep track of how many pyro windows are open becuase the main interface should open
# when the last window is closed but not when just any window is closed

def set_window_count(x):
    global window_count
    window_count = x


def get_window_count():
    global window_count
    return window_count


# This is a function that gets called when the main window gets closed, it sets can_make_menu to True because now a new
# menu can be made without having duplicates
def close(menu):
    global can_make_menu
    can_make_menu = True
    try:
        menu.root.destroy()
    except TclError:
        pass


class InterfaceMenu:

    def __init__(self):
        # doesn't make a menu if can_make_menu is false, meaning there is a menu already open
        global can_make_menu
        if not can_make_menu:
            return
        # it sets can_make_menu to false because now there is a menu and a new one shouldn't be made
        can_make_menu = False
        self.settings = self.find_settings()
        # Setting up the main window visuals
        self.root = Tk()
        self.root.configure(background="#00062A")
        self.root.geometry("460x220")
        self.root.resizable(0, 0)
        self.root.title("Unity Mod Maker - Main Menu")
        self.root.iconbitmap("resources/unitymodmaker.ico")
        self.new_image = PhotoImage(file="resources/newbutton.png")
        self.open_image = PhotoImage(file="resources/openbutton.png")
        self.new_button = Label(self.root, image=self.new_image, background="#00062A")
        self.open_button = Label(self.root, image=self.open_image, background="#00062A")
        self.new_button.place(x=20, y=20)
        self.open_button.place(x=240, y=20)
        # The buttons are bound to the self.new function and self.load function because they are new and load buttons
        self.new_button.bind("<Button-1>", self.new)
        self.open_button.bind("<Button-1>", self.load)

        def mouse_enter(e):
            e.widget.config(fg="#8a7cf9")

        def mouse_exit(e):
            e.widget.config(fg="#4a3eab")

        extra_buttons = []

        self.open_external = Label(self.root, text="Open From .umm File")
        self.open_external.place(x=20, y=150)
        self.open_external.bind("<Button-1>", self.open_dialog)
        extra_buttons.append(self.open_external)

        self.settings_button = Label(self.root, text="Unity Mod Maker Settings")
        self.settings_button.place(x=20, y=180)
        self.settings_button.bind("<Button-1>", self.change_settings)
        extra_buttons.append(self.settings_button)

        for button in extra_buttons:
            button.config(font=("Arial", 15), fg="#4a3eab", background="#00062A")
            button.bind("<Enter>", mouse_enter)
            button.bind("<Leave>", mouse_exit)

        # Instead of doing root.mainloop we do pyro.add_window to avoid thread conflicts, pyro deals with calling
        # root.update() on  everything in the pyro window list, there is also no need to remove closed windows from this
        pyro.add_window(self.root)

    def find_settings(self):
        settings = None
        try:
            with open('settings.json') as json_file:
                settings = json.load(json_file)
                for item in DEFAULT_SETTINGS:
                    if item not in settings:
                        settings[item] = DEFAULT_SETTINGS[item]
            with open('settings.json', 'w') as json_file:
                json.dump(settings, json_file)
        except Exception:
            with open('settings.json', 'w') as json_file:
                json.dump(DEFAULT_SETTINGS, json_file)
                settings = DEFAULT_SETTINGS
        return settings


    def save_settings(self, settings, values):
        for i in range(len(settings)):
            self.settings[settings[i]] = values[i]
        with open('settings.json', 'w') as json_file:
            json.dump(self.settings, json_file)


    def change_settings(self, e):
        ordered_settings = [item for item in self.settings]
        create_prompt("Unity Mod Maker Settings", ordered_settings, partial(self.save_settings, ordered_settings), None,
                      defaults=self.settings, width=500)


    def _copy_fallback(self, mod, name):
        name = name[0]
        self.new_name = name
        mod = copy(mod, name)
        if mod is not None: return mod
        return self.load_fallback([self.new_name])

    def open_dialog(self, e):
        messagebox.showwarning("Never Open Mods From Untrusted Sources", "Reminder: Never Open Mods From Untrusted Sources!!")
        file = filedialog.askopenfile(filetypes=[("Unity Mod Maker Files", "*.umm")])
        if file is None: return
        name = file.name
        file.close()
        mod = load(name)
        create_prompt("Create Mod From .umm file", ("New Mod Name",), partial(self._copy_fallback, mod), None)
        #pyro.CoreUI(lexer=CSharpLexer(), filename=mod.mod_name_no_space.get_text(), mod=mod)

    def enter(self, e):
        # mod_name is the contents of the text box
        mod_name = e.widget.get()
        # no_space is the name of the mod without spaces
        no_space = mod_name.replace(" ", "")
        # First tries to load the mod, if it doesn't exist it creates a new mod
        try:
            mod = load(os.getcwd() + "/projects/" + no_space + "/" + no_space + ".umm")
        except FileNotFoundError:
            mod = ModObject(no_space)
        # this closes the main menu because we do not need it anymore
        close(self)
        # creates a pyro window which will have syntax highlighting for CSharp and will be editing our mod object
        pyro.CoreUI(lexer=CSharpLexer(), filename=no_space, mod=mod)

    # See the new function, this is the function that gets called when the prompt from the new function has "done"
    # clicked
    def new_fallback(self, data, window):
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
        # make sure the game is set up in a way to support modding
        support = verify_game(data[1], data[1] if data[2] == "" else data[2], data[4], window)
        if type(support) is str:
            return support
        if not support:
            return ""
        # creates a new mod with this name and information from the prompt
        mod = ModObject(name, poly_tech=poly_tech, game=data[1], folder_name=None if data[2] == "" else data[2],
                        steampath=data[4])
        # close the menu window because we don't need it anymore
        close(self)
        # creates a pyro window which will have syntax highlighting for CSharp and will be editing our mod object
        pyro.CoreUI(lexer=CSharpLexer(), filename=name.replace(" ", ""), mod=mod)

    # This gets called when the "new" button is pressed so it creates a prompt asking for the name of the new mod and
    # calls self.new_fallback when they press "done", None means that if they press "cancel" nothing specific is done
    def new(self, e):
        create_prompt("New Mod", ("Mod Name",
                                  "Game Name (Check Spelling and Punctuation)",
                                  "Name of Folder in Steam Files (If different from Game Name)",
                                  "PolyTech (Poly Bridge Modding Framework)",
                                  "Steam Directory"), self.new_fallback, None, defaults={
            "Game Name (Check Spelling and Punctuation)": self.settings["Default Game"],
            "Name of Folder in Steam Files (If different from Game Name)": self.settings["Default Game Folder"],
            "PolyTech (Poly Bridge Modding Framework)": "Auto",
            "Steam Directory": self.settings["Default Steam Directory"]
        })

    # See the load function, this is the function that gets called when the prompt from the load function has "done"
    # clicked
    def load_fallback(self, name):
        # name is a list of values but it is only one long so just replace it with the first item
        name = name[0]
        # If the directory corresponding to the name doesn't exist, they can't open it
        check_path = os.getcwd() + "/projects/" + name.replace(" ", "")
        if not exists(check_path):
            # When the fallback to a prompt returns something, the prompt will show that as an error message and
            # keep itself open effectively asking them again
            return "Project Doesn't Exist"
        try:
            # It attempts to load the .umm file with the mod name inside of the directory (This should exist assuming
            # the file was generated by this program and they didn't specifically delete it
            mod = load(os.getcwd() + "/projects/" + name.replace(" ", "") + "/" + name.replace(" ", "") + ".umm")
        except FileNotFoundError:
            # When the fallback to a prompt returns something, the prompt will show that as an error message and
            # keep itself open effectively asking them again
            return "Unity Mod Maker File Missing"
        # close the main menu because we do not need it anymore
        close(self)
        # creates a pyro window which will have syntax highlighting for CSharp and will be editing our mod object
        pyro.CoreUI(lexer=CSharpLexer(), filename=name.replace(" ", ""), mod=mod)

    # This gets called when the "open" button is pressed so it creates a prompt asking for the name of the mod and
    # calls self.load_fallback when they press "done", None means that if they press "cancel" nothing specific is done
    # there is also a warning that will show up in red telling them not to open mods from untrusted sources this is
    # due to the fact that a malicious .umm file could allow for arbitrary code execution
    def load(self, e):
        create_prompt("Load Mod", ("Mod Name",), self.load_fallback, None,
                      warning="Never Open Mods From Untrusted Sources")


if __name__ == "__main__":
    # Creates the main menu and then calls the pyro mainloop
    InterfaceMenu()
    # Pyro has a global (static) list in it that all windows add themselves into, each time pyro mainloop happens it
    # updates each of these windows and does all the required tick events, this is to prevent thread conflicts
    pyro.mainloop()
