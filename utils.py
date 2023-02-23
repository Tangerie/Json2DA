import unreal
import map_types
import importlib
importlib.reload(map_types)
from map_types import MAP_TYPES, FACTORY_MAP

def get_factory_from_class(clazz):
    for c in clazz.__mro__:
        if c.__name__ in FACTORY_MAP and len(FACTORY_MAP[c.__name__]) > 0: return FACTORY_MAP[c.__name__]

def create_with_factory(folder, name, clazz, factory_name):
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = getattr(unreal, factory_name)()
    print(factory)
    return tools.create_asset(name, folder, clazz, factory)

def try_create_asset(folder, name, type_str):
    if not hasattr(unreal, type_str):
        unreal.log_error(f"{type_str} does not exist")
        return
    
    clazz = getattr(unreal, type_str)
    available_factories = get_factory_from_class(clazz)

    if available_factories is None:
        unreal.log_error(f"{type_str} does not have a factory")
        return

    for factory_name in available_factories:
        print(f"Trying {factory_name}")
        try:
            asset =  create_with_factory(folder, name, clazz, factory_name)
            if asset is not None: return asset
        except Exception as e: unreal.log_error(e)

    return None

def as_key_pair(data):
    return [list(x.items())[0] for x in data]

def does_asset_exist(folder, name):
    return unreal.EditorAssetLibrary.does_asset_exist(folder + "/" + name)

def create_linked_asset(data):
    obj_type, obj_name = data["ObjectName"].split("'")[:2]
    full_path = data["ObjectPath"].split(".")[0] + "." + obj_name
    asset = unreal.load_asset(f"{obj_type}'{full_path}'")

    if asset is None:
        folder = "/".join(data["ObjectPath"].split(".")[0].split("/")[:-1])
        asset = try_create_asset(folder, obj_name, obj_type)
        print(asset)
        if asset is not None: unreal.EditorAssetLibrary.save_loaded_asset(asset, False)

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
        if len(value) > 0:
            map_ty = try_get_map_type(obj, key)
            if map_ty is None: 
                unreal.log_error(f"Map {key} is unknown, leaving blank")
            else:
                obj.set_editor_property(key, update_map(prop, value, map_ty))
    elif isinstance(value, dict) and "ObjectName" in value:
        obj.set_editor_property(key, create_linked_asset(value))
    elif unreal.StructBase in ty.__mro__:
        apply(prop, value)

def apply(asset, data : dict):
    for key in data:
        set_editor_property(asset, key, data[key])
    