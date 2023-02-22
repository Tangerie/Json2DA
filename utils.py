import unreal
import map_types
import importlib
importlib.reload(map_types)
from map_types import MAP_TYPES


def as_key_pair(data):
    return [list(x.items())[0] for x in data]

def does_asset_exist(folder, name):
    return unreal.EditorAssetLibrary.does_asset_exist(folder + "/" + name)

def create_data_asset_from_str_type(folder, name, type_str):
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset = tools.create_asset(name, folder, getattr(unreal, type_str), unreal.DataAssetFactory())
    unreal.EditorAssetLibrary.save_loaded_asset(asset, False)
    return asset

def create_linked_asset(data):
    obj_type, obj_name = data["ObjectName"].split("'")[:2]
    full_path = data["ObjectPath"].split(".")[0] + "." + obj_name
    asset = unreal.load_asset(f"{obj_type}'{full_path}'")

    if asset is None:
        tools = unreal.AssetToolsHelpers.get_asset_tools()

        if obj_type == "Texture2D":
            factory = unreal.Texture2DFactoryNew()
        else:
            factory = unreal.DataAssetFactory()
        asset = tools.create_asset(obj_name, "/".join(data["ObjectPath"].split(".")[0].split("/")[:-1]), getattr(unreal, obj_type), factory)
        print(asset)
        unreal.EditorAssetLibrary.save_loaded_asset(asset, False)

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
    
def update_map(m_prop, data, ty):
    v_ty = ty["Value"]
    k_ty = ty["Key"]
    
    if k_ty == "": k_ty = "str"


    is_builtin = v_ty in __builtins__
    
    for key, value in as_key_pair(data):
        if k_ty != "str" and unreal.EnumBase in getattr(unreal, k_ty).__mro__:
            key = str_to_enum(key)

        if v_ty == "":
            v_ty = try_get_map_value_type(m_prop, key)
            if v_ty is None: print(key)
        if v_ty == "__AssetRef":
            uvalue =  create_linked_asset(value)
        else:
            uvalue = value if is_builtin else  getattr(unreal, v_ty)()
            if not is_builtin: apply(uvalue, value)
    
       
        m_prop[key] = uvalue

    return m_prop

# Like obj.set_editor_property except it takes our JSON as a value
def set_editor_property(obj, key, value):
    try:
        prop = obj.get_editor_property(key)
    except:
        return
    ty = type(prop)

    if ty in (unreal.Name, str, float):
        obj.set_editor_property(key, value)
    elif unreal.EnumBase in ty.__mro__:
        obj.set_editor_property(key, str_to_enum(value))
    elif ty is unreal.Map:
        map_ty = try_get_map_type(obj, key)
        if map_ty is None: raise Exception("ERROR", key)
        obj.set_editor_property(key, update_map(prop, value, map_ty))
    elif isinstance(value, dict) and "ObjectName" in value:
        obj.set_editor_property(key, create_linked_asset(value))
    elif unreal.StructBase in ty.__mro__:
        apply(prop, value)

def apply(asset, data : dict):
    for key in data:
        set_editor_property(asset, key, data[key])
    