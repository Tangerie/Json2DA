import unreal
import os
import importlib, importlib.util
import inspect
from pprint import pprint
def getScriptsDirectory():
    return unreal.Paths.combine([unreal.Paths.project_content_dir(), "Python", "Scripts"])




def GetAvailableScripts():
    root = unreal.Paths.combine([unreal.Paths.project_content_dir(), "Python", "Scripts"])
    files = [
        x[:-len(".py")] for x in os.listdir(root) if all((
            os.path.isfile(unreal.Paths.combine([root, x])),
            x.endswith(".py"),
            x != "__init__.py"
        ))
    ]

    return {
        "files": files
    }
