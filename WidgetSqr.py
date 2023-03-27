import json
from pprint import pprint
from typing import List
import unreal
import inspect
import importlib
import WidgetUtil
import os
importlib.reload(WidgetUtil)

widgetData : List[dict] = []
widgetOuter : str = ""

def FindByProperty(key, value):
    return (node for node in widgetData if key in node and node[key] == value)


def GetByIndex(index): return widgetData[int(index)]
def GetByObjectReference(ref):
    origin, index = ref["ObjectPath"].split(".")
    origin = origin.split("/")[-1]
    if origin != widgetOuter: 
        unreal.log_warning(f"Object Ref {ref['ObjectPath']} is not from this file")
        return CreateNodeInfo
    return GetByIndex(index)

def GetRootNode():
    for node in FindByProperty("Type", "WidgetBlueprintGeneratedClass"):
        return GetByObjectReference(node["Properties"]["WidgetTree"])
    return None

def pathToDict(path):
    with open(path, "r+", encoding="utf-8") as fp:
        return json.load(fp)

def ConvertWidgetsDict(d : dict):
    return {
        k: json.dumps(v) for k, v in d.items()
    }


def CreateNodeInfo(node):
    data = {
        "children": [],
        "type": node["Type"],
        "name": node["Name"],
        "isvar": "bIsVariable" in node["Properties"] and node["Properties"]["bIsVariable"]
    }

    props = node["Properties"]
    if "RootWidget" in props:
        r = GetByObjectReference(props["RootWidget"])
        if r is not None: data["children"].append(r["Name"])

    if "Slots" in props:
        for s in props["Slots"]:
            r = GetByObjectReference(s)
            if r is not None: r = GetByObjectReference(r["Properties"]["Content"])
            if r is not None: data["children"].append(r["Name"])

    return data

def cleanPath(path : str):
    path = path.strip().strip('"')
    return path

def ImportJson(widget_json_path=""):
    global widgetData
    global widgetOuter
    widget_json_path = cleanPath(widget_json_path)
    widgetOuter =  os.path.splitext(os.path.basename(widget_json_path))[0]

    
    widgetData = pathToDict(widget_json_path)

    baseTree = GetRootNode()
    roots = WidgetUtil.GetRootObjects(widgetData)

    # print(baseTree)
    # pprint([x["Name"] for x in roots])

    widgets = {
        "RootNode": CreateNodeInfo(baseTree)
    }

    for root in roots:
        widgets[root["Name"]] = CreateNodeInfo(root)

    return {
        "widgets": ConvertWidgetsDict(widgets)
    }
