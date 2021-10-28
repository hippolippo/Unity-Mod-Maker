from pyroprompt import *
import pyro
from os.path import exists
import os
from ModObject import ModObject
import ModObject
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
