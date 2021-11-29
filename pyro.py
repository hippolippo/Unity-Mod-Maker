#!/usr/bin/env python


"""
    UnityModderPyro, Modified to work for Unity Mod Maker By Hippolippo

    Original Code https://github.com/JamesStallings/pyro/blob/master/pyro:
    simple elegant text editor built on python/tkinter
    by James Stallings, June 2015
    Adapted from:

      Pygments Tkinter example
      copyleft 2014 by Jens Diemer
      licensed under GNU GPL v3

    and

      'OONO' designed and written by Lee Fallat, 2013-2014.
      Inspired by acme, sam, vi and ohmwriter.
    A sincere thanks to these good people for making their source code available for myself and others
    to learn from. Cheers!


        Pyro currently does a very minimalist job of text editing via tcl/tk ala tkinter.

        What pyro does now:

           colorizes syntax for a variety of text types; to wit:

               Python
               PlainText
               Html/Javascript
               Xml
               Html/Php
               Perl6
               Ruby
               Ini/Init
               Apache 'Conf'
               Bash Scripts
               Diffs
               C#
               MySql

           writes out its buffer
           converts tabs to 4 spaces

           It does this in an austere text editor framework which is essentially a glue layer
           bringing together the tk text widget with the Pygment library for styling displayed
           text. Editor status line is in the window title.

           Pyro comes with one serious warning: it is a user-space editor. It makes no effort
           to monitor state-change events on files and so should not be used in situations
           where it is possible that more than one writer will have access to the file.


        Pyro's current controls are as follows:

           Ctrl+q quits
           Ctrl+w writes out the buffer
           Selection, copy, cut and paste are all per xserver/window manager. Keyboard navigation via
           arrow/control keys, per system READLINE.

        Pyro's current commands are:

           #(num) move view to line 'num' and highlight it, if possible.
           *(text) find text in file.
           /(delim)(text)(delim)(text) search and replace

        Pyro requires Tkinter and Pygment external libraries.

"""

import os
import io
import sys

import ChangeManager
from GraphicalInterface import *
import MenuMethods
from functools import partial

try:
    # Python 3
    import tkinter
    from tkinter import font, ttk, scrolledtext, _tkinter

except ImportError:
    # Python 2
    import Tkinter as tkinter
    from Tkinter import ttk
    import tkFont as font
    import ScrolledText as scrolledtext

from ModObject import *
from pygments.lexers.python import PythonLexer
from pygments.lexers.special import TextLexer
from pygments.lexers.html import HtmlLexer
from pygments.lexers.html import XmlLexer
from pygments.lexers.templates import HtmlPhpLexer
from pygments.lexers.perl import Perl6Lexer
from pygments.lexers.ruby import RubyLexer
from pygments.lexers.configs import IniLexer
from pygments.lexers.configs import ApacheConfLexer
from pygments.lexers.shell import BashLexer
from pygments.lexers.diff import DiffLexer
from pygments.lexers.dotnet import CSharpLexer
from pygments.lexers.sql import MySqlLexer

from pygments.styles import get_style_by_name

pyros = []
windows = []


class CoreUI(object):
    """
        CoreUI is the editor object, derived from class 'object'. It's instantiation initilizer requires the
        ubiquitous declaration of the 'self' reference implied at call time, as well as a handle to
        the lexer to be used for text decoration.
    """

    def __init__(self, lexer, filename="Untitled", mod=None):
        set_window_count(get_window_count() + 1)
        self.filename = filename
        if mod is None:
            mod = ModObject("Untitled")
        self.mod = mod
        self.contents = mod.get_text()
        self.sourcestamp = {}
        self.filestamp = {}
        self.uiopts = []
        self.lexer = lexer
        self.lastRegexp = ""
        self.markedLine = 0
        self.root = tkinter.Tk()
        self.root.iconbitmap("resources/unitymodmaker.ico")
        self.root.protocol("WM_DELETE_WINDOW", self.destroy_window)
        self.uiconfig()
        self.root.bind("<Key>", self.event_key)
        self.root.bind('<Control-KeyPress-q>', self.close)
        self.root.bind('<Control-KeyPress-z>', self.undo)
        self.root.bind('<Control-KeyPress-y>', self.redo)
        self.root.bind('<Button>', self.event_mouse)
        self.root.bind('<Configure>', self.event_mouse)
        self.text.bind('<Return>', self.autoindent)
        self.text.bind('<Tab>', self.tab2spaces4)
        self.create_tags()
        self.text.edit_modified(False)
        self.bootstrap = [self.recolorize]
        self.loadfile(self.contents)
        self.recolorize()
        self.root.geometry("1200x700+10+10")
        self.initialize_menubar()
        self.updatetitlebar()
        self.root.update()
        self.root.focus()
        self.scroll_data = self.text.yview()
        self.starting()
        global pyros
        pyros.append(self)

    def undo(self, e=None):
        mod = ChangeManager.undo()
        if mod is not None:
            self.mod = mod
            self.refresh(False)
        return "break"

    def redo(self, e):
        mod = ChangeManager.redo()
        if mod is not None:
            self.mod = mod
            self.refresh(False)
        return "break"

    def initialize_menubar(self):
        self.menubar = tkinter.Menu(self.root)

        self.filemenu = tkinter.Menu(self.menubar, tearoff=False)
        self.editmenu = tkinter.Menu(self.menubar, tearoff=False)
        self.createmenu = tkinter.Menu(self.menubar, tearoff=False)
        self.buildmenu = tkinter.Menu(self.menubar, tearoff=False)

        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.filemenu.add_command(label="New", command=MenuMethods.new)
        self.filemenu.add_command(label="Open", command=MenuMethods.open)
        self.filemenu.add_command(label="Save", command=partial(MenuMethods.save, self, self.filename))
        self.filemenu.add_command(label="Save as Renamed Copy", command=partial(MenuMethods.copy, self))

        self.menubar.add_cascade(label="Edit", menu=self.editmenu)

        self.editmenu.add_command(label="Change Mod Name", command=partial(MenuMethods.change_mod_name, self))
        self.editmenu.add_command(label="Change Mod Version",
                                  command=partial(MenuMethods.change_mod_version, self))

        self.menubar.add_cascade(label="Create", menu=self.createmenu)

        self.createmenu.add_command(label="Create Harmony Patch",
                                    command=partial(MenuMethods.create_harmony_patch, self))
        self.createmenu.add_command(label="Create Config Item",
                                    command=partial(MenuMethods.create_config_item, self))
        self.createmenu.add_command(label="Create Keybind",
                                    command=partial(MenuMethods.create_keybind, self))

        self.menubar.add_cascade(label="Build", menu=self.buildmenu)

        self.buildmenu.add_command(label="Build and Install", command=partial(MenuMethods.build_install, self))
        self.buildmenu.add_command(label="Export C# File", command=partial(MenuMethods.export_cs, self))
        self.buildmenu.add_command(label="Generate Dotnet Files", command=partial(MenuMethods.export_dotnet, self))

        self.root.config(menu=self.menubar)

    def refresh(self, updateMod=True):
        if updateMod:
            self.scroll_data = self.text.yview()
            text = self.text.get("1.0", tkinter.END)[:-1]
            cursor = self.text.index(tkinter.INSERT)
            #print(cursor)
            index = ChangeManager.update(self.mod, self.text.get("1.0", tkinter.END)[:-1])
            if index == "Locked":
                self.undo()
                return
            self.mod.index = index
        else:
            text = None
            index = self.mod.index
        self.text.delete("1.0", tkinter.END)
        self.text.insert("1.0", self.mod.get_text())
        if self.mod.get_text() == text and text is not None:
            self.text.mark_set("insert", str(cursor))
        else:
            text = self.text.get("1.0", tkinter.END).split("\n")
            a, i = 0, 0
            while a + len(text[i]) + 1 < index and i < len(text):
                a += len(text[i])
                a += 1
                i += 1
            j = index - a
            self.text.mark_set("insert", "%d.%d" % (i + 1, j))

        self.recolorize()
        self.text.yview_moveto(self.scroll_data[0])


    def uiconfig(self):
        """
            this method sets up the main window and two text widgets (the editor widget, and a
            text entry widget for the commandline).
        """
        self.uiopts = {"height": "60",
                       "width": "132",
                       "cursor": "xterm",
                       "bg": "#00062A",
                       "fg": "#FFAC00",
                       "insertbackground": "#FFD310",
                       "insertborderwidth": "1",
                       "insertwidth": "3",
                       "exportselection": True,
                       "undo": True,
                       "selectbackground": "#E0000E",
                       "inactiveselectbackground": "#E0E0E0"
                       }
        self.text = scrolledtext.ScrolledText(master=self.root, **self.uiopts)
        self.text.vbar.configure(
            activebackground="#FFD310",
            borderwidth="0",
            background="#68606E",
            highlightthickness="0",
            highlightcolor="#00062A",
            highlightbackground="#00062A",
            troughcolor="#20264A",
            relief="flat")
        self.cli = tkinter.Text(self.root, {"height": "1",
                                            "bg": "#191F44",
                                            "fg": "#FFC014",
                                            "insertbackground": "#FFD310",
                                            "insertborderwidth": "1",
                                            "insertwidth": "3",
                                            "exportselection": True,
                                            "undo": True,
                                            "selectbackground": "#E0000E",
                                            "inactiveselectbackground": "#E0E0E0"
                                            })
        self.text.grid(column=0, row=0, sticky=('nsew'))
        self.cli.grid(column=0, row=1, pady=1, sticky=('nsew'))
        self.cli.bind("<Return>", self.cmdlaunch)
        self.cli.bind("<KeyRelease>", self.adjust_cli)
        self.cli.visible = True
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)

    def updatetitlebar(self):
        self.root.title("Unity Mod Maker - " + self.filename)
        self.root.update()

    def destroy_window(self):
        self.close()

    def search(self, regexp, currentposition):
        """
             this method implements the core functionality of the search feature
             arguments: the search target as a regular expression and the position
             from which to search.
        """
        characters = tkinter.StringVar()
        index_start = ""
        index_end = ""

        try:
            index_start = self.text.search(
                regexp,
                currentposition + "+1c",
                regexp=True,
                count=characters)

        except _tkinter.TclError:
            index_start = "1.0"

        if index_start == "":
            index_start = self.text.index("insert")

        length = characters.get()

        if length == "":
            length = "0"

        index_end = "{0}+{1}c".format(index_start, length)
        return index_start, index_end

    def replace(self, regexp, subst, cp):
        """
            this method implements the search+replace compliment to the search functionality
        """
        index_start, index_end = self.search(regexp, cp)

        if index_start != index_end:
            self.text.delete(index_start, index_end)
            self.text.insert(index_start, subst)

        return index_start, index_end

    def gotoline(self, linenumber):
        """
            this method implements the core functionality to locate a specific line of text by
            line position
            arguments: the target line number
        """
        index_start = linenumber + ".0"
        index_end = linenumber + ".end"
        return index_start, index_end

    def cmd(self, cmd, index_insert):
        """
            this method parses a line of text from the command line and invokes methods on the text
            as indicated for each of the implemented commands
            arguments: the command, and the insert position
        """
        index_start = ""
        index_end = ""
        regexp = ""
        linenumber = ""
        cmdchar = cmd[0:1]  # truncate newline
        cmd = cmd.strip("\n")

        if len(cmdchar) == 1:
            regexp = self.lastRegexp
            linenumber = self.markedLine

        if cmdchar == "*":
            if len(cmd) > 1:
                regexp = cmd[1:]
                index_start, index_end = self.search(regexp, index_insert)
                self.lastRegexp = regexp
        elif cmdchar == "#":
            if len(cmd) > 1:
                linenumber = cmd[1:]
            index_start, index_end = self.gotoline(linenumber)
            self.markedLine = linenumber
        elif cmdchar == "/":
            if len(cmd) > 3:  # the '/', delimter chr, 1 chr target, delimiter chr, null for minimum useful s+r
                snr = cmd[1:]
                token = snr[0]
                regexp = snr.split(token)[1]
                subst = snr.split(token)[2]
                index_start, index_end = self.replace(regexp, subst, index_insert)
        return index_start, index_end

    def cmdcleanup(self, index_start, index_end):
        """
            this method cleans up post-command and prepares the command line for re-use
            arguments: index beginning and end. ** this needs an audit, as does the entire
                                                    index start/end construct **
        """
        if index_start != "":
            self.text.mark_set("insert", index_start)
            self.text.tag_add("sel", index_start, index_end)
            # self.text.focus()
            self.text.see(index_start)
            self.cli.delete("1.0", tkinter.END)

    def cmdlaunch(self, event):
        """
            this method implements the callback for the key binding (Return Key)
            in the command line widget, wiring it up to the parser/dispatcher method.
            arguments: the tkinter event object with which the callback is associated
        """
        mods = {
            0: None,
            0x0001: 'Shift',
            0x0002: 'Caps Lock',
            0x0004: 'Control',
            0x0008: 'Left-hand Alt',
            0x0010: 'Num Lock',
            0x0080: 'Right-hand Alt',
            0x0100: 'Mouse button 1',
            0x0200: 'Mouse button 2',
            0x0400: 'Mouse button 3'
        }
        if mods[event.state] == "Shift":
            self.adjust_cli(event)
            return
        cmd = self.cli.get("1.0", tkinter.END)
        self.cli.delete("1.0", tkinter.END)
        if cmd[0] == "~":
            try:
                if cmd.count("\n") > 1:
                    exec(cmd[1:])
                else:
                    print("User Command Executed", "(" + cmd[1:-1] + ")", "Gives:", eval(cmd[1:]))
                self.root.update()
            except Exception as e:
                print(e)
        self.adjust_cli(event)
        return "break"

    def adjust_cli(self, event=None):
        height = self.cli.cget("height")
        if min(self.cli.get("1.0", tkinter.END).count("\n"), 25) != height:
            self.cli.config(height=min(self.cli.get("1.0", tkinter.END).count("\n"), 25))

    def autoindent(self, event):
        """
            this method implements the callback for the Return Key in the editor widget.
            arguments: the tkinter event object with which the callback is associated
        """
        indentation = ""
        lineindex = self.text.index("insert").split(".")[0]
        linetext = self.text.get(lineindex + ".0", lineindex + ".end")

        for character in linetext:
            if character in [" ", "\t"]:
                indentation += character
            else:
                break

        self.text.insert(self.text.index("insert"), "\n" + indentation)
        return "break"

    def tab2spaces4(self, event):
        """
            this method implements the callback for the indentation key (Tab Key) in the
            editor widget.
            arguments: the tkinter event object with which the callback is associated
        """
        self.text.insert(self.text.index("insert"), "    ")
        return "break"

    def loadfile(self, text):
        """
            this method implements loading a file into the editor.
            arguments: the scrollable text object into which the text is to be loaded
        """
        if text:
            self.text.insert(tkinter.INSERT, text)
            self.text.tag_remove(tkinter.SEL, '1.0', tkinter.END)
            self.text.see(tkinter.INSERT)

    def event_key(self, event):
        """
            this method traps the keyboard events. anything that needs doing when a key is pressed is done here.
            arguments: the associated event object
        """
        keycode = event.keycode
        char = event.char
        self.recolorize()
        self.updatetitlebar()

    def event_write(self, event):
        """
            the callback method for the root window 'ctrl+w' event (write the file to disk)
            arguments: the associated event object.
        """
        with open(self.filename, "w") as filedescriptor:
            filedescriptor.write(self.text.get("1.0", tkinter.END)[:-1])

        self.text.edit_modified(False)
        self.root.title("Pyro: File Written.")

    def event_mouse(self, event):
        """
            this method traps the mouse events. anything that needs doing when a mouse
            operation occurs is done here.
            arguments: the associated event object
        """
        self.updatetitlebar()
        # self.recolorize()

    def close(self, event=None):
        import GraphicalInterface
        GraphicalInterface.set_window_count(GraphicalInterface.get_window_count() - 1)
        self.root.destroy()
        if get_window_count() <= 0:
            GraphicalInterface.set_window_count(0)
            InterfaceMenu()

    # ---------------------------------------------------------------------------------------

    def starting(self):
        """
            the classical tkinter event driver loop invocation, after running through any
            startup tasks
        """
        for task in self.bootstrap:
            task()

    def create_tags(self):
        """
            thmethod creates the tags associated with each distinct style element of the
            source code 'dressing'
        """
        bold_font = font.Font(self.text, self.text.cget("font"))
        bold_font.configure(weight=font.BOLD)
        italic_font = font.Font(self.text, self.text.cget("font"))
        italic_font.configure(slant=font.ITALIC)
        bold_italic_font = font.Font(self.text, self.text.cget("font"))
        bold_italic_font.configure(weight=font.BOLD, slant=font.ITALIC)
        style = get_style_by_name('default')

        for ttype, ndef in style:
            tag_font = None

            if ndef['bold'] and ndef['italic']:
                tag_font = bold_italic_font
            elif ndef['bold']:
                tag_font = bold_font
            elif ndef['italic']:
                tag_font = italic_font

            if ndef['color']:
                foreground = "#%s" % ndef['color']
            else:
                foreground = None

            self.text.tag_configure(str(ttype), foreground=foreground, font=tag_font)

    def recolorize(self):
        """
            this method colors and styles the prepared tags
        """
        code = self.text.get("1.0", "end-1c")
        tokensource = self.lexer.get_tokens(code)
        start_line = 1
        start_index = 0
        end_line = 1
        end_index = 0

        for ttype, value in tokensource:
            if "\n" in value:
                end_line += value.count("\n")
                end_index = len(value.rsplit("\n", 1)[1])
            else:
                end_index += len(value)

            if value not in (" ", "\n"):
                index1 = "%s.%s" % (start_line, start_index)
                index2 = "%s.%s" % (end_line, end_index)

                for tagname in self.text.tag_names(index1):  # FIXME
                    self.text.tag_remove(tagname, index1, index2)

                self.text.tag_add(str(ttype), index1, index2)

            start_line = end_line
            start_index = end_index


if __name__ == "__main__":
    extens = "cs"

    try:
        extens = sys.argv[1].split('.')[1]
    except IndexError:
        pass
    extens = "cs"
    if extens == "py" or extens == "pyw" or extens == "sc" or extens == "sage" or extens == "tac":
        ui_core = CoreUI(lexer=PythonLexer())
    elif extens == "txt" or extens == "README" or extens == "text":
        ui_core = CoreUI(lexer=TextLexer())
    elif extens == "htm" or extens == "html" or extens == "css" or extens == "js" or extens == "md":
        ui_core = CoreUI(lexer=HtmlLexer())
    elif extens == "xml" or extens == "xsl" or extens == "rss" or extens == "xslt" or extens == "xsd" or extens == "wsdl" or extens == "wsf":
        ui_core = CoreUI(lexer=XmlLexer())
    elif extens == "php" or extens == "php5":
        ui_core = CoreUI(lexer=HtmlPhpLexer())
    elif extens == "pl" or extens == "pm" or extens == "nqp" or extens == "p6" or extens == "6pl" or extens == "p6l" or extens == "pl6" or extens == "pm" or extens == "p6m" or extens == "pm6" or extens == "t":
        ui_core = CoreUI(lexer=Perl6Lexer())
    elif extens == "rb" or extens == "rbw" or extens == "rake" or extens == "rbx" or extens == "duby" or extens == "gemspec":
        ui_core = CoreUI(lexer=RubyLexer())
    elif extens == "ini" or extens == "init":
        ui_core = CoreUI(lexer=IniLexer())
    elif extens == "conf" or extens == "cnf" or extens == "config":
        ui_core = CoreUI(lexer=ApacheConfLexer())
    elif extens == "sh" or extens == "cmd" or extens == "bashrc" or extens == "bash_profile":
        ui_core = CoreUI(lexer=BashLexer())
    elif extens == "diff" or extens == "patch":
        ui_core = CoreUI(lexer=DiffLexer())
    elif extens == "cs":
        ui_core = CoreUI(lexer=CSharpLexer())
    elif extens == "sql":
        ui_core = CoreUI(lexer=MySqlLexer())
    else:
        ui_core = CoreUI(lexer=PythonLexer())  # default (no extension) lexer is python


def add_window(window):
    global windows
    windows.append(window)


def mainloop():
    global pyros
    global windows
    while True:
        count = 0
        for pyro in pyros:
            try:
                pyro.root.update()
                pyro.adjust_cli()
                box = pyro.text.get("1.0", tkinter.END)[:-1]
                modtext = pyro.mod.get_text()
                if box != modtext:
                    pyro.refresh()
                count += 1
            except _tkinter.TclError as e:
                #print(e)
                pass
        for window in windows:
            try:
                window.update()
                count += 1
            except _tkinter.TclError:
                pass
        for window in get_windows():
            try:
                window.update()
                count += 1
            except _tkinter.TclError:
                pass
        if count == 0:
            print("Exiting: All Windows Deleted")
            exit(0)
