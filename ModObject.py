from ModObjectBuilder import *
from CodeManager import *
import pickle


class ModObject:

    def __init__(self, mod_name="mod", version="1.0.0", poly_tech=False):
        self.config_number = 0
        self.version = CodeLine(version)
        self.poly_tech = poly_tech
        self.mod_name = CodeLine(mod_name)
        self.mod_name_no_space = CodeLine(mod_name.replace(" ", ""))
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
                postfix=END_BLOCK
            )
        self.class_wrap.contents.insert_block_after(self.class_constructor)
        self.awake = create_awake(self.mod_name, self.mod_name_no_space, poly_tech=self.poly_tech)
        self.class_wrap.contents.insert_block_after(self.awake)
        if self.poly_tech:
            self.add_config("mEnabled", "bool", "false", "Enable/Disable Mod",
                            "Controls if the mod should be enabled or disabled")
        self.main_contents = self.class_wrap.contents

    def add_config(self, name, data_type, default, definition, description=""):
        self.config_entry_declarations.insert_block_after(
            CodeLine("public static ConfigEntry<"+data_type+"> "+name+";"))
        self.config_definitions.insert_block_after(CodeLine(
            "public ConfigDefinition "+name+"Def = new ConfigDefinition(pluginVersion, \""+definition+"\");"))
        self.class_constructor.contents.insert_block_after(CodeLine(
            "Config.Bind("+name+"Def, "+default+", new ConfigDescription(\""+description +
            "\", null, new ConfigurationManagerAttributes {Order = "+str(self.config_number)+"}));"
        ))
        self.config_number -= 1

    def create_harmony_patch(self, in_class, method, prefix=True, parameters=list(), have_instance=True, result=None):
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
            postfix=END_BLOCK
        ))
        patch.block_list[-1].contents.insert_block_after(LargeCodeBlockWrapper([
            CodeBlockWrapper(
                prefix=CodeLine("if(mEnabled.Value){"),
                postfix=END_BLOCK
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


def save(mod_object, location="mod.umm"):
    pickle.dump(mod_object, open(location, "wb"))


def load(location="mod.umm"):
    return pickle.load(open(location, "rb"))


if __name__ == "__main__":
    x = ModObject(poly_tech=True, mod_name="Chicken Car")
    x.create_harmony_patch("CompactCar", "CompactCarGravity")
    save(x)
    y = load()
    text = "\n".join([s for s in y.code.get_text().splitlines() if s])
    print(text)
    with open("dump.cs", "w") as file:
        file.write(text)
