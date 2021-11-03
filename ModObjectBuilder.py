from CodeManager import *


def end_block():
    return CodeLine("}")


def create_headers(poly_tech=True):
    code = [
        CodeLine("using System;"),
        CodeLine("using System.Collections;"),
        CodeLine("using BepInEx;"),
        CodeLine("using BepInEx.Logging;"),
        CodeLine("using HarmonyLib;"),
        CodeLine("using BepInEx.Configuration;"),
        CodeLine("using UnityEngine;"),
        CodeLine("using System.Reflection;")
    ]
    if poly_tech:
        code.append(CodeLine("using PolyTechFramework;"))
    return CodeBlock(code_lines=code)


def create_namespace(mod_name, mod_name_no_space):
    namespace_top = CodeBlock([
        CodeLine("namespace"),
        mod_name_no_space,
        CodeLine("{")
    ],
        delimiter=" "
    )
    namespace = CodeBlockWrapper(
        prefix=namespace_top,
        postfix=end_block()
    )
    return namespace


def create_namespace_contents(poly_tech=True):
    namespace_contents = LargeCodeBlockWrapper()
    bix_dependencies = CodeBlock()
    bix_dependencies.add_line(code_line=CodeLine("[BepInPlugin(pluginGuid, pluginName, pluginVersion)]"))
    if poly_tech:
        bix_dependencies.add_line(code_line=CodeLine(
            "[BepInDependency(PolyTechMain.PluginGuid, BepInDependency.DependencyFlags.HardDependency)]"
        ))
    namespace_contents.insert_block_before(bix_dependencies)
    namespace_contents.insert_block_after(LargeCodeBlockWrapper())
    return namespace_contents


def create_class(mod_name, mod_name_no_space, poly_tech=True):
    output = CodeBlockWrapper(
        prefix=CodeBlock(code_lines=[
            CodeLine("public class"),
            mod_name_no_space,
            CodeLine("{")
        ], delimiter=" "),
        contents=LargeCodeBlockWrapper(),
        postfix=end_block()
    )
    if poly_tech:
        output.prefix.add_line(CodeLine(": PolyTechMod"), location=2)
    return output


def create_constants(mod_name, mod_name_no_space, version, poly_tech=True):
    output = LargeCodeBlockWrapper()
    plugin_guid = LargeCodeBlockWrapper([CodeLine("public const string pluginGuid =")], delimiter=" ")
    output.insert_block_after(plugin_guid)
    if not poly_tech:
        plugin_guid.insert_block_after(CodeBlock([CodeLine("\"org.bepinex.plugins."),
                                                  mod_name_no_space, CodeLine("\";")], delimiter=""))
    else:
        plugin_guid.insert_block_after(CodeBlock([CodeLine("\"polytech."),
                                                  mod_name_no_space, CodeLine("\";")], delimiter=""))
    plugin_name = LargeCodeBlockWrapper([CodeLine("public const string pluginName =")], delimiter=" ")
    output.insert_block_after(plugin_name)
    plugin_name.insert_block_after(CodeBlock([CodeLine("\""), mod_name, CodeLine("\";")], delimiter=""))
    plugin_version = LargeCodeBlockWrapper([CodeLine("public const string pluginVersion =")], delimiter=" ")
    output.insert_block_after(plugin_version)
    plugin_version.insert_block_after(CodeBlock([CodeLine("\""), version, CodeLine("\";")], delimiter=""))
    return output


def create_function(head, contents=None):
    if contents is None:
        new_contents = LargeCodeBlockWrapper()
    else:
        new_contents = contents
    head = CodeLine(head + "{")
    function = CodeBlockWrapper(
        prefix=head,
        contents=new_contents,
        postfix=end_block()
    )
    return function


def create_poly_tech_functions(poly_tech=True):
    if not poly_tech:
        return CodeBlock()
    output = LargeCodeBlockWrapper()
    enable_code = CodeBlock([CodeLine("mEnabled.Value = true;"), CodeLine("this.isEnabled = true;")])
    output.insert_block_after(create_function("public override void enableMod()", contents=enable_code))
    disable_code = CodeBlock([CodeLine("mEnabled.Value = false;"), CodeLine("this.isEnabled = false;")])
    output.insert_block_after(create_function("public override void disableMod()", contents=disable_code))
    output.insert_block_after(create_function("public override string getSettings()",
                                              contents=CodeLine("    return \"\";")))
    output.insert_block_after(create_function("public override void setSettings(string settings)"))
    return output


def create_awake(mod_name, mod_name_no_space, poly_tech=True):
    output = LargeCodeBlockWrapper()
    if poly_tech:
        output.insert_block_after(CodeLine("this.repositoryUrl = \"\";"))
        output.insert_block_after(CodeLine("this.isCheat = true;"))
        output.insert_block_after(CodeLine("PolyTechMain.registerMod(this);"))
        output.insert_block_after(CodeBlock([CodeLine("Logger.LogInfo(\""), mod_name,
                                             CodeLine(" Registered\");")],
                                            delimiter=""))
    output.insert_block_after(CodeBlock([CodeLine("Harmony.CreateAndPatchAll(typeof("), mod_name_no_space,
                                         CodeLine("));")], delimiter=""))
    if poly_tech:
        output.insert_block_after(CodeBlock([CodeLine("Logger.LogInfo(\""), mod_name,
                                             CodeLine(" Methods Patched\");")],
                                            delimiter=""))
    output = create_function("void Awake()", contents=output)
    return output
