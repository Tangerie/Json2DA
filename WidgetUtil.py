from pprint import pprint
from typing import Dict, List
import importlib
import BPCreators
importlib.reload(BPCreators)

def ResolveRef(data : List[dict], refObject):
    index = int(refObject["ObjectPath"].split(".")[-1])
    return data[index]

def ResolveReferenceToString(data : List[dict], refObject):
    return refObject["ObjectName"]

def FindByName(data : List[dict], name : str):
    return (x for x in data if "Name" in x and x["Name"] == name)

def isRootNode(node):
    return "Outer" in node and node["Outer"] == "WidgetTree"

def GetRootObjects(data : List[dict]):
    return tuple(x for x in data if isRootNode(x))

# Stuff to not put in the Struct
__StructIgnore = {
    "SpecifiedColor": ["Hex"]
}

def CreateStruct(data : List[dict], props : dict):
    pairs = []
    for key, value in props.items():
        if key in __StructIgnore and isinstance(value, dict):
            value = {k: v for k, v in value.items() if k not in __StructIgnore[key]}
        pairs.append(f'{key}={ConvertPropertyValue(data, key, value)}')

    return f'({",".join(pairs)})'

def ConvertPropertyValue(data : List[dict], key : str, props):
    if key == "Text": return BPCreators.Text(props)
    
    if isinstance(props, dict): 
        if "ObjectName" in props and "ObjectPath" in props:
            return ResolveReferenceToString(data, props)
        else:
            return CreateStruct(data, props)
    
    if isinstance(props, str): return BPCreators.StrValue(key, props)

    if isinstance(props, list):
        return tuple(ConvertPropertyValue(data, key, x) for x in props)

    return f"{props}"



def Properties(data : List[dict], widget_props):
    output_props = {}
    for key, props in widget_props.items():
        result = ConvertPropertyValue(data, key, props)
        if isinstance(result, (list, tuple)):
            for i, value in enumerate(result):
                output_props[f'{key}({i})'] = value
        else:
            output_props[key] = result

    return BPCreators.PropertiesToString(**output_props)

'''
ChildContainers: 
    - RootWidget
    - Slots
    - Content

NOTE: Slot refers to the parent

WidgetSlotPair is not in FModel JSON, but it is not required (UE will generate it)

To make a "slottable" expanded in editor: bExpandedInDesigner=True 
'''

__ChildContainerKeys = ("RootWidget", "Slots")
__IgnoredKeys = (
    "Slot", 
    # Temp Testing Ignores
    # "ColorTag", "Font", "ColorAndOpacity", "Brush"
)


def CleanProps(props : dict):
    return { k: v for k, v in props.items() if k not in __IgnoredKeys}

# Properties that aren't related to structure like Slots etc.
def GetNonStructuralProps(props : dict):
    return { k: v for k, v in props.items() if k not in __IgnoredKeys and k not in __ChildContainerKeys}



def getClassPath(widget):
    if widget["ClassPath"] == "":
        return widget["Class"].split("'")[1]
    else: 
        return widget["ClassPath"]

def CreateSlots(data : List[dict], slots_list):
    lines = ([], [], [])

    for i, sl in enumerate(slots_list):
        slot = ResolveRef(data, sl)
        lines[0].extend(
            BPCreators.Object(Class=getClassPath(slot), Name=slot["Name"])
        )

        lines[1].extend(
            BPCreators.Object(Name=slot["Name"], Content=Properties(data, GetNonStructuralProps(slot["Properties"])))
        )

        lines[2].append(
            BPCreators.ArrayItem("Slots", i, BPCreators.ReferenceFromTypeName(slot))
        )

    return tuple((*lines[0], *lines[1], *lines[2], "bExpandedInDesigner=True"))

def CreateWidget(data : List[dict], widget):
    print(f'=== {widget["Name"]} [{widget["Type"]}] ===')

    w_props = CleanProps(widget["Properties"])

    obj_props = {
        "Class": getClassPath(widget),
        "Name": widget["Name"],
        "Content": []
    }

    if "Slots" in w_props:
        obj_props["Content"].extend(CreateSlots(data, w_props["Slots"]))

    other_props = GetNonStructuralProps(w_props)
    
    obj_props["Content"].extend(Properties(data, other_props))

    # print(w_props.keys())



    return BPCreators.Object(**obj_props)


    

def CreateRootWidget(data : List[dict]):
    root_objs = GetRootObjects(data)

    widget_texts = []

    for x in root_objs:
        widget_texts.extend(CreateWidget(data, x))

    print("\n\n" + "\n".join(widget_texts))


    # print("\n".join(Properties(data, {
    #   "Brush": {
    #     "ImageSize": {
    #       "X": 32.0,
    #       "Y": 50.0
    #     },
    #     "TintColor": {
    #       "SpecifiedColor": {
    #         "R": 1.0,
    #         "G": 1.0,
    #         "B": 1.0,
    #         "A": 0.0,
    #         "Hex": "FFFFFF"
    #       }
    #     }
    #   },
    #   "Slot": {
    #     "ObjectName": "HorizontalBoxSlot'UI_BP_MenuTextButton_C:WidgetTree.HorizontalBox_0.HorizontalBoxSlot_1'",
    #     "ObjectPath": "/Game/UI/Menus/UI_BP_MenuTextButton.25"
    #   },
    #   "bIsVariable": False,
    #   "Visibility": "ESlateVisibility::SelfHitTestInvisible"
    # })))

    return "\n".join(widget_texts)