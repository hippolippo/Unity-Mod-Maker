from tkinter import messagebox

from ModObject import *
from tkinter import *
import ctypes

root = Tk()
root.withdraw()


mod = ModObject(mod_name="Never Too Poor", version="1.0.0", poly_tech=True)
patch = mod.create_harmony_patch("Budget", "CanAffordEdge", result="bool", have_instance=False)
patch.add_line(CodeLine("__result = true; return false;"))
mod.install()
