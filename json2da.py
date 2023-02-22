import json
import unreal
from pprint import pprint
import inspect
import importlib

import utils
importlib.reload(utils)

from utils import str_to_enum, try_get_map_type, as_key_pair, create_linked_asset, try_get_map_value_type

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
    
def main(json_string):
    sel_asset = unreal.EditorUtilityLibrary.get_selected_assets()
    data = json.loads(json_string)[0]
    [apply(asset, data["Properties"]) for asset in sel_asset]