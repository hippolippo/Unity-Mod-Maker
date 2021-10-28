import shutil
from tkinter import messagebox

from ModObjectBuilder import *
from CodeManager import *
import pickle
import os
import subprocess
from tkinter import *


class ModObject:

    def __init__(self, mod_name="mod", version="1.0.0", poly_tech=True):
        self.config_number = 0
        self.version = CodeLine(version)
        self.poly_tech = poly_tech
        self.mod_name = CodeLine(mod_name, locked=True)
        self.mod_name_no_space = CodeLine(mod_name.replace(" ", ""), locked=True)
        self.code = LargeCodeBlockWrapper()
        self.header = create_headers(poly_tech=self.poly_tech)
        self.code.insert_block_before(self.header)
        self.namespace = create_namespace(self.mod_name, self.mod_name_no_space)
        self.code.insert_block_after(self.namespace)
        self.in_namespace = create_namespace_contents(poly_tech=self.poly_tech)
        self.namespace.contents = self.in_namespace
        self.class_wrap = create_class(self.mod_name, self.mod_name_no_space, poly_tech=self.poly_tech)
        self.namespace.contents.insert_block_after(self.class_wrap)
        self.constants = create_constants(self.mod_name, self.mod_name_no_space, self.version,
                                          poly_tech=self.poly_tech)
        self.class_wrap.contents.insert_block_after(self.constants)
        self.config_entry_declarations = LargeCodeBlockWrapper()
        self.class_wrap.contents.insert_block_after(self.config_entry_declarations)
        self.config_definitions = LargeCodeBlockWrapper()
        self.class_wrap.contents.insert_block_after(self.config_definitions)
        self.reflections_declarations = LargeCodeBlockWrapper([LargeCodeBlockWrapper(), LargeCodeBlockWrapper()])
        # ^^ First is for methods second is for fields
        self.class_wrap.contents.insert_block_after(self.reflections_declarations)
        self.general_declarations = LargeCodeBlockWrapper()
        self.class_wrap.contents.insert_block_after(self.general_declarations)
        self.poly_tech_functions = create_poly_tech_functions(self.poly_tech)
        self.class_wrap.contents.insert_block_after(self.poly_tech_functions)
        self.class_constructor = CodeBlockWrapper(
            prefix=CodeBlock([CodeLine("public "), self.mod_name_no_space, CodeLine("(){")], delimiter=""),
            contents=LargeCodeBlockWrapper(),
            postfix=end_block()
        )
        self.class_wrap.contents.insert_block_after(self.class_constructor)
        self.awake = create_awake(self.mod_name, self.mod_name_no_space, poly_tech=self.poly_tech)
        self.class_wrap.contents.insert_block_after(self.awake)
        if poly_tech:
            self.add_config("mEnabled", "bool", "false", "Enable/Disable Mod",
                            "Controls if the mod should be enabled or disabled")
        self.main_contents = self.class_wrap.contents

    def add_config(self, name, data_type, default, definition, description=""):
        self.config_entry_declarations.insert_block_after(
            CodeLine("public static ConfigEntry<" + data_type + "> " + name + ";"))
        self.config_definitions.insert_block_after(CodeLine(
            "public ConfigDefinition " + name + "Def = new ConfigDefinition(pluginVersion, \"" + definition + "\");"))
        self.class_constructor.contents.insert_block_after(CodeLine(
            name + " = " +
            "Config.Bind(" + name + "Def, " + default + ", new ConfigDescription(\"" + description +
            "\", null, new ConfigurationManagerAttributes {Order = " + str(self.config_number) + "}));"
        ))
        self.config_number -= 1

    def create_harmony_patch(self, in_class, method, prefix=True, parameters=list(), have_instance=True, result=None, ):
        poly_tech = self.poly_tech
        if result is not None:
            parameters.insert(0, "ref " + result + " __result")
        if have_instance:
            parameters.insert(0, "ref " + in_class + " __instance")

        patch = LargeCodeBlockWrapper()
        self.main_contents.insert_block_after(patch)
        patch.insert_block_after(CodeLine(
            "[HarmonyPatch(typeof(" + in_class + "), \"" + method + "\")]"
        ))
        patch.insert_block_after(CodeLine(
            "[HarmonyPrefix]" if prefix else "[HarmonyPostfix]"
        ))
        patch.insert_block_after(CodeBlockWrapper(
            prefix=CodeLine(
                "private static bool " + in_class.replace("_", "") + method +
                ("Prefix" if prefix else "Postfix") +
                "Patch(" +
                ", ".join(parameters) + "){"
            ),
            contents=LargeCodeBlockWrapper(),
            postfix=end_block()
        ))
        patch.block_list[-1].contents.insert_block_after(LargeCodeBlockWrapper([
            CodeBlockWrapper(
                prefix=CodeLine("if(mEnabled.Value){" if poly_tech else ""),
                postfix=end_block() if poly_tech else CodeLine("")
            ),
            CodeLine("return true;")
        ]))
        return patch.block_list[-1].contents.block_list[-1].block_list[0].contents

    def set_mod_name(self, new_name):
        self.mod_name.code = new_name
        self.mod_name_no_space.code = new_name.replace(" ", "")

    def set_version(self, new_version):
        self.version.code = new_version

    def get_text(self):
        return self.code.get_text()

    def get_block_list(self):
        return self.code.get_block_list()
    def get_list(self):
        return self.code.get_list()

    def install(self):
        path = create_files(self)
        if path is None:
            return None
        dotnet_build(path)
        try:
            os.remove("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Poly Bridge 2\\BepInEx\\plugins\\" +
                      self.mod_name_no_space.get_text() + ".dll")
        except FileNotFoundError:
            pass
        shutil.move(path + "/bin/Debug/netstandard2.0/" + self.mod_name_no_space.get_text() + ".dll",
                    "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Poly Bridge 2\\BepInEx\\plugins")


def create_files(mod: ModObject):
    name_no_space = mod.mod_name_no_space.get_text()
    current_directory = os.getcwd()
    folder_path = os.path.join(current_directory, "projects/"+name_no_space)
    try:
        os.mkdir(folder_path)
    except FileExistsError:
        pass
    save(mod, location=folder_path + "/" + name_no_space + ".umm")
    shutil.copyfile("gitignoretemplate", folder_path + "/.gitignore")
    shutil.copyfile("configmanagertemplate", folder_path + "/ConfigurationManagerAttributes.cs")
    with open(folder_path + "/" + name_no_space + ".cs", "w") as f:
        code = "\n".join([s for s in mod.code.get_text().splitlines() if s])
        f.write(code)
    with open(folder_path + "/" + name_no_space + ".csproj", "w") as f:
        code = open("csprojtemplate", "r").read().replace("{{mod_name}}", name_no_space).replace("{{ptf}}",
                                                                                                 """
    <Reference Include="PolyTechFramework">
        <HintPath>Libraries/PolyTechFramework.dll</HintPath>
    </Reference>""" if mod.poly_tech else "")
        f.write(code)

    try:
        shutil.copytree("C:/Program Files (x86)/Steam/steamapps/common/Poly Bridge 2/Poly Bridge 2_Data/Managed",
                        folder_path + "\\Libraries", dirs_exist_ok=True)
        shutil.copytree("C:/Program Files (x86)/Steam/steamapps/common/Poly Bridge 2/BepInEx/core",
                        folder_path + "\\Libraries", dirs_exist_ok=True)
        if mod.poly_tech:
            shutil.copytree("C:/Program Files (x86)/Steam/steamapps/common/Poly Bridge "
                            "2/BepInEx/plugins",
                            folder_path + "\\Libraries", dirs_exist_ok=True)
    except FileNotFoundError as e:
        print(e)
        print("ERROR: Could not create mod files, make sure Poly Bridge 2 is installed with BepInEx" +
              " and Polytech" if mod.poly_tech else "")
        messagebox.showerror("Could Not Create Mod Files",
                             "Couldn't Create Mod File, Make sure Poly Bridge 2 is Installed with BepInEx" +
                             " and Polytech" if mod.poly_tech else "")
        return None
    return folder_path


def dotnet_build(path):
    subprocess.run(["dotnet", "build"], cwd=path)


def save(mod_object, location="mod.umm"):
    pickle.dump(mod_object, open(location, "wb"))


def load(location="mod.umm"):
    return pickle.load(open(location, "rb"))


def copy(mod_object, name):
    name_no_space = name.replace(" ", "")
    current_directory = os.getcwd()
    folder_path = os.path.join(current_directory, "projects/"+name_no_space)
    try:
        os.mkdir(folder_path)
    except FileExistsError:
        pass
    save(mod_object, location=folder_path + "/" + name_no_space + ".umm")
    mod2 = load(folder_path + "/" + name_no_space + ".umm")
    mod2.set_mod_name(name)
    save(mod2, location=folder_path + "/" + name_no_space + ".umm")


if __name__ == "__main__":
    x = ModObject(poly_tech=True, mod_name="Chicken Car")
    x.create_harmony_patch("CompactCar", "CompactCarGravity")
    save(x)
    y = load()
    text = "\n".join([s for s in y.code.get_text().splitlines() if s])
    path = create_files(x)
    dotnet_build(path)
