import shutil
from tkinter import messagebox

from ModObjectBuilder import *
from CodeManager import *
import pickle
import os
import subprocess
from tkinter import *

VERSION = "alpha 0.1.1"
windows = []


def get_windows(): return windows


class LimitedModObject:
    def __init__(self):
        pass

class ModObject(LimitedModObject):

    def __init__(self, mod_name="mod", version="1.0.0", poly_tech=True, game="Poly Bridge 2", folder_name=None,
                 steampath="C:\\Program Files (x86)\\Steam\\steamapps\\common\\"):
        self.saved = False
        self.index = 0
        self.mod_maker_version = VERSION
        self.game = game
        self.folder_name = self.game if folder_name is None else folder_name
        self.steampath = steampath
        self.config_number = 0
        self.version = CodeLine(version, locked=True)
        self.poly_tech = poly_tech
        self.mod_name = CodeLine(mod_name, locked=True)
        self.mod_name_no_space = CodeLine(mod_name.replace(" ", ""), locked=True)
        self.code = LargeCodeBlockWrapper()
        self.header = create_headers(poly_tech=self.poly_tech)
        self.code.insert_block_before(self.header)
        self.namespace = create_namespace(self.mod_name, self.mod_name_no_space)
        self.code.insert_block_after(self.namespace)
        self.in_namespace = create_namespace_contents(self.game, poly_tech=self.poly_tech)
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
        self.update = create_update(self.mod_name, self.mod_name_no_space, poly_tech=self.poly_tech)
        self.class_wrap.contents.insert_block_after(self.awake)
        self.class_wrap.contents.insert_block_after(self.update)
        self.add_config("mEnabled", "bool", "false", "Enable/Disable Mod",
                        "Controls if the mod should be enabled or disabled", should_indent=False)
        self.main_contents = self.class_wrap.contents
        self.indent()
        self.code.insert_block_after(CodeLine("\n"))

    def add_config(self, name, data_type, default, definition, description="", should_indent=True):
        if should_indent:
            self.config_entry_declarations.insert_block_after(
                CodeLine("public static ConfigEntry<" + data_type + "> " + name + ";").indent().indent())
            self.config_definitions.insert_block_after(CodeLine(
                "public ConfigDefinition " + name + "Def = new ConfigDefinition(pluginVersion, \"" + definition
                + "\");").indent().indent())
            self.class_constructor.contents.insert_block_after(CodeLine(
                name + " = " +
                "Config.Bind(" + name + "Def, " + default + ", new ConfigDescription(\"" + description +
                "\", null, new ConfigurationManagerAttributes {Order = " + str(self.config_number) + "}));"
            ).indent().indent().indent())
        else:
            self.config_entry_declarations.insert_block_after(
                CodeLine("public static ConfigEntry<" + data_type + "> " + name + ";"))
            self.config_definitions.insert_block_after(CodeLine(
                "public ConfigDefinition " + name + "Def = new ConfigDefinition(pluginVersion, \"" + definition
                + "\");"))
            self.class_constructor.contents.insert_block_after(CodeLine(
                name + " = " +
                "Config.Bind(" + name + "Def, " + default + ", new ConfigDescription(\"" + description +
                "\", null, new ConfigurationManagerAttributes {Order = " + str(self.config_number) + "}));"
            ))
        self.config_number -= 1

    def declare_variable(self, data_type, name, default=None):
        if default is not None:
            self.general_declarations.insert_block_after(CodeBlock([
                CodeLine("public"),
                CodeLine("static"),
                CodeLine(data_type),
                CodeLine(name),
                CodeLine("="),
                CodeLine(default + ";")
            ], delimiter=" ").indent().indent())
        else:
            self.general_declarations.insert_block_after(CodeBlock([
                CodeLine("public"),
                CodeLine("static"),
                CodeLine(data_type),
                CodeLine(name + ";")
            ], delimiter=" ").indent().indent())

    def create_harmony_patch(self, in_class, method, prefix=True, parameters=list(), have_instance=True, result=None):
        poly_tech = self.poly_tech
        parameters = [i for i in parameters if i != '']
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
                "private " + ("static " if not have_instance else "") + ("bool" if prefix else "void") + " " +
                in_class.replace("_", "") + method +
                ("Prefix" if prefix else "Postfix") +
                "Patch(" +
                ", ".join(parameters) + "){"
            ),
            contents=LargeCodeBlockWrapper(),
            postfix=end_block()
        ))
        return_false = CodeLine("return false; // Cancels Original Function" if prefix else "")
        return_true = CodeLine("return true;" if prefix else "")
        patch.block_list[-1].contents.insert_block_after(LargeCodeBlockWrapper([
            CodeBlockWrapper(
                prefix=CodeLine("if(mEnabled.Value){"),
                contents=CodeBlock([CodeLine("// Write code for patch here"),
                                    CodeLine("//__result = null;"), return_false]
                                   if result is not None else [CodeLine("// Write code for patch here"),
                                                               return_false]).indent(),
                postfix=end_block()
            ),
            return_true
        ]))
        patch.block_list[-1].contents.indent()
        patch.indent()
        patch.indent()
        return patch.block_list[-1].contents.block_list[-1].block_list[0].contents

    def autosave(self, changeSaved=True):
        current_directory = os.getcwd()
        name_no_space = self.mod_name_no_space.get_text()
        folder_path = os.path.join(current_directory, "projects/" + name_no_space)
        if not os.path.isdir(folder_path):
            return
        if changeSaved:
            self.saved = False

        save(self, location=folder_path + "/" + name_no_space + "-auto.umm", overwrite_auto=False)

    def set_mod_name(self, new_name):
        self.mod_name.code = new_name
        self.mod_name_no_space.code = new_name.replace(" ", "")

    def set_version(self, new_version):
        self.version.code = new_version

    def get_text(self):
        return self.code.get_text()

    def get_code_lines(self):
        return self.code.get_code_lines()

    def get_block_list(self):
        return self.code.get_block_list()

    def get_list(self):
        return self.code.get_list()

    def indent(self):
        self.code.default_indent()

    def install(self, destroyonerror=None, progress_updater=print):
        progress_updater("Generating Dotnet Files...")
        path = create_files(self, destroyonerror=destroyonerror)
        if path is None:
            return None
        progress_updater("Running Dotnet Build...")
        build_result = dotnet_build(path)
        '''# I don't remember why I wrote this so I'm just commenting it out for now
        try:
            os.path.join(self.steampath, self.game, "BepInEx/plugins/" +
                         self.mod_name_no_space.get_text() + ".dll")
        except FileNotFoundError:
            pass
        '''
        try:
            shutil.move(path + "/bin/Debug/netstandard2.0/" + self.mod_name_no_space.get_text() + ".dll",
                        os.path.join(self.steampath, self.folder_name, "BepInEx/plugins/" +
                                     self.mod_name_no_space.get_text() + ".dll"))
            shutil.copyfile(os.path.join(os.getcwd(), "resources/Default Libraries/ConfigurationManager.dll"),
                            os.path.join(self.steampath, self.folder_name, "BepInEx/plugins/ConfigurationManager.dll"))
            shutil.copyfile(os.path.join(os.getcwd(), "resources/Default Libraries/netstandard.dll"),
                            os.path.join(self.steampath, self.folder_name, "BepInEx/plugins/netstandard.dll"))

            '''shutil.move(os.path.join(os.getcwd(), "resources/Default Libraries/ConfigurationManager.dll"),
                        os.path.join(self.steampath, self.folder_name, "BepInEx/plugins/" +
                                     self.mod_name_no_space.get_text() + ".dll"))'''
        except FileNotFoundError:
            if destroyonerror is not None:
                destroyonerror.destroy()
            root = Tk()
            root.title("Build Failed")
            root.iconbitmap("resources/unitymodmaker.ico")
            from tkinter import scrolledtext
            textbox = scrolledtext.ScrolledText(root)
            textbox.configure(bg="#191F44", fg="#FFC014", )
            textbox.insert(1.0, build_result)
            textbox.pack(fill="both")
            root.update()
            global windows
            windows.append(root)
            root.focus()
            '''messagebox.showerror("Build of mod failed",
                                 "The mod failed to build, either there was an error in the code or dotnet is not prope"
                                 "rly installed. See Command Prompt for Details.")'''
            return None
        return True


def create_files(mod: ModObject, destroyonerror=None):
    name_no_space = mod.mod_name_no_space.get_text()
    current_directory = os.getcwd()
    folder_path = os.path.join(current_directory, "projects/" + name_no_space)
    try:
        os.mkdir(os.path.join(current_directory, "projects"))
    except FileExistsError:
        pass
    try:
        os.mkdir(folder_path)
    except FileExistsError:
        pass
    save(mod, location=folder_path + "/" + name_no_space + ".umm")
    shutil.copyfile("resources/gitignoretemplate", folder_path + "/.gitignore")
    shutil.copyfile("resources/configmanagertemplate", folder_path + "/ConfigurationManagerAttributes.cs")
    with open(folder_path + "/" + name_no_space + ".cs", "w") as f:
        code = "\n".join([s for s in mod.code.get_text().splitlines() if s])
        f.write(code)
    with open(folder_path + "/" + name_no_space + ".csproj", "w") as f:
        code = open("resources/csprojtemplate", "r").read().replace("{{mod_name}}", name_no_space).replace("{{ptf}}",
                                                                                                 """
    <Reference Include="PolyTechFramework">
        <HintPath>Libraries/PolyTechFramework.dll</HintPath>
    </Reference>""" if mod.poly_tech else "")
        f.write(code)

    try:

        shutil.copytree(os.path.join(mod.steampath, mod.folder_name, mod.game + "_Data", "Managed"),
                        folder_path + "\\Libraries", dirs_exist_ok=True)
        shutil.copytree(os.path.join(mod.steampath, mod.folder_name, "BepInEx/core"),
                        folder_path + "\\Libraries", dirs_exist_ok=True)
        shutil.copytree(os.path.join(os.getcwd(), "resources/Default Libraries"),
                        folder_path + "\\Libraries", dirs_exist_ok=True)
        if mod.poly_tech:
            shutil.copytree(os.path.join(mod.steampath, mod.folder_name, "BepInEx/plugins"),
                            folder_path + "\\Libraries", dirs_exist_ok=True)
    except FileNotFoundError as e:
        print(e)
        print("ERROR: Could not create mod files, make sure " + mod.game + " is installed with BepInEx" +
              " and Polytech" if mod.poly_tech else "")
        if destroyonerror is not None:
            destroyonerror.destroy()
        messagebox.showerror("Could Not Create Mod Files",
                             "Couldn't Create Mod File, Make sure " + mod.game + " is installed with BepInEx" +
                             " and Polytech" if mod.poly_tech else "")
        return None
    return folder_path


def dotnet_build(path):
    command = subprocess.Popen(["dotnet", "build"], cwd=path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    return command.stdout.read()


def save(mod_object, location="mod.umm", overwrite_auto=True):
    mod_object.saved = True
    auto_path = location.split(".")
    if len(auto_path) == 1:
        auto_path += "-auto"
    else:
        auto_path[-2] += "-auto"
        auto_path = ".".join("auto_path")
    if overwrite_auto:
        if os.path.exists(auto_path):
            os.remove(auto_path)
    pickle.dump(mod_object, open(location, "wb"))


def load(location="mod.umm", auto_option=True):
    auto_path = location.split(".")
    if len(auto_path) == 1:
        auto_path += "-auto"
    else:
        auto_path[-2] += "-auto"
        auto_path = ".".join(auto_path)
    use_auto = False
    if auto_option and os.path.exists(auto_path):
        use_auto = messagebox.askquestion("Load Autosave?",
                                          "There is an autosave available, would you like to load it instead?")
    if use_auto:
        location = auto_path
    mod = pickle.load(open(location, "rb"))
    if mod.mod_maker_version != VERSION:
        messagebox.showwarning("Mod From Old Version", "This Mod Was Made in Version " + mod.mod_maker_version +
                               " and may not function properly when converted to this version (" + VERSION + ")")
        mod.mod_maker_version = VERSION
    return mod


def copy(mod_object, name):
    name_no_space = name.replace(" ", "")
    current_directory = os.getcwd()
    folder_path = os.path.join(current_directory, "projects", name_no_space)
    try:
        os.mkdir(folder_path)
    except FileExistsError:
        return "That Project Already Exists"
    save(mod_object, location=folder_path + "/" + name_no_space + ".umm")
    mod2 = load(folder_path + "/" + name_no_space + ".umm")
    mod2.set_mod_name(name)
    save(mod2, location=folder_path + "/" + name_no_space + ".umm")


def verify_game(name, folder_name, steam_path, prompt):
    if not os.path.isdir(os.path.join(steam_path, folder_name)):
        messagebox.showerror("Game Not Found",
                             "Game Not Found. There is no directory \"" + os.path.join(steam_path, folder_name) + "\"",
                             parent=prompt)
        return False
    if not os.path.isdir(os.path.join(steam_path, folder_name, name + "_Data")):
        messagebox.showerror("Game Not Valid",
                             "The directory \"" + os.path.join(steam_path, folder_name, name + "_Data") +
                             "\" Does not exist, this is probably due to the game not being a CSharp Unity Game which "
                             "means it can't be modded with this tool", parent=prompt)
        return False
    if not os.path.isdir(os.path.join(steam_path, folder_name, "BepInEx")):
        question = messagebox.askquestion("Install BepInEx",
                                          "BepInEx is not installed on this game, would you like to install it "
                                          "automatically?",
                                          icon="info", parent=prompt)
        if question == "yes":
            shutil.copytree(os.path.join(os.getcwd(), "resources", "BepInEx"),
                            os.path.join(steam_path, folder_name), dirs_exist_ok=True)
            messagebox.showinfo("BepInEx Installed", "BepInEx has been installed, please run the game once and then "
                                                     "exit in order to generate the proper files, then click \"OK\"",
                                parent=prompt)
            if not os.path.isdir(os.path.join(steam_path, folder_name, "BepInEx", "Plugins")):
                return "BepInEx not fully installed"
            return True
        else:
            return False
    if not os.path.isdir(os.path.join(steam_path, folder_name, "BepInEx", "Plugins")):
        messagebox.showinfo("BepInEx Partially Installed",
                            "BepInEx is installed with files missing, please run the game once and then "
                            "exit in order to generate the proper files, then click \"OK\"",
                            parent=prompt)
        if not os.path.isdir(os.path.join(steam_path, folder_name, "BepInEx", "Plugins")):
            return "BepInEx not fully installed"
    return True


if __name__ == "__main__":
    x = ModObject(poly_tech=True, mod_name="Chicken Car")
    x.create_harmony_patch("CompactCar", "CompactCarGravity")
    save(x)
    y = load()
    text = "\n".join([s for s in y.code.get_text().splitlines() if s])
    path = create_files(x)
    dotnet_build(path)
