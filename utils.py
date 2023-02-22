import unreal
import map_types
import importlib
importlib.reload(map_types)
from map_types import MAP_TYPES


def as_key_pair(data):
    return [list(x.items())[0] for x in data]

def create_linked_asset(data):
    obj_type, obj_name = data["ObjectName"].split("'")[:2]
    full_path = data["ObjectPath"].split(".")[0] + "." + obj_name
    asset = unreal.load_asset(f"{obj_type}'{full_path}'")

    return asset

def get_typestr_from_name(name : str):
    return name.split("'")[0]

# EGearSlotIDEnum::BACK => GearSlotIDEnum.BACK
def str_to_enum(val):
    enum_type, enum_val = val.split("::")
    enum_type = enum_type[1:]
    return getattr(getattr(unreal, enum_type), enum_val)

def try_get_map_value_type(map_obj, key):
    try:
        map_obj[key] = {}
    except:
        try:
            map_obj[key] = 0
        except:
            pass
        pass
    
    try:
        if map_obj.get(key) is None: return None

        ty = type(map_obj.pop(key))
        return ty.__name__
    except:
        return None

def try_get_map_type(obj, key):
    map_obj = obj.get_editor_property(key)
    if key in MAP_TYPES:
        return MAP_TYPES[key]
    
    try:
        map_obj["_"] = {}
    except:
        try:
            map_obj["_"] = 0
        except:
            pass
        pass
    
    try:
        if map_obj.get("_") is None: return None

        ty = type(map_obj.pop("_"))
        return { "Key": "str", "Value": ty.__name__ }
    except:
        return None