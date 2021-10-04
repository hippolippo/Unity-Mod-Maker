from ModObject import *

mod = ModObject(mod_name="Never Too Poor", version="1.0.0", poly_tech=True)
patch = mod.create_harmony_patch("Budget", "CalculateBridgeCost", result="float", have_instance=False)
patch.add_line(CodeLine("__result = 0.0f;"))
patch.add_line(CodeLine("return false;"))
with open("dump.cs", "w") as file:
    file.write(mod.get_text())

