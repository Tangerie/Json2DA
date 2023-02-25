import importlib
import unreal
import json
import MaterialExpressions
import materialutil
importlib.reload(MaterialExpressions)
importlib.reload(materialutil)
from materialutil import connectNodesUntilSingle

AssetTools = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EditorAssetLibrary = unreal.EditorAssetLibrary
EditorUtilityLibrary = unreal.EditorUtilityLibrary

mat = EditorUtilityLibrary.get_selected_assets()[0]

Y_GAP = 175


def create_node(ty, yPos, name, defaultValue=None):
    node = MEL.create_material_expression(mat, ty, 0, yPos * Y_GAP)
    node.set_editor_property("ParameterName", name)
    if defaultValue is not None: node.set_editor_property("DefaultValue", defaultValue)
    return node

def generateInputNodes(data : dict):
    
    # Store last nodes (not always same as parameter nodes)
    all_final_nodes = []

    for p in data["ScalarParameterValues"]:
        all_final_nodes.append(
            create_node(MaterialExpressions.ScalarParameter, len(all_final_nodes), p["ParameterInfo"]["Name"], p["ParameterValue"])
        )

    for p in data["VectorParameterValues"]:
        all_final_nodes.append(
            create_node(MaterialExpressions.VectorParameter, len(all_final_nodes), p["ParameterInfo"]["Name"], unreal.LinearColor(p["ParameterValue"]["R"], p["ParameterValue"]["G"], p["ParameterValue"]["B"], p["ParameterValue"]["A"]))
        )

    for p in data["TextureParameterValues"]:
        node = create_node(MaterialExpressions.TextureSampleParameter2D, len(all_final_nodes), p["ParameterInfo"]["Name"])
        node.set_editor_property("SamplerSource", unreal.SamplerSourceMode.SSM_WRAP_WORLD_GROUP_SETTINGS)
        all_final_nodes.append(
            node
        )

    return all_final_nodes



def main(json_path):
    with open(json_path.file_path, "r+") as fp:
        data = json.load(fp)[0]["Properties"]

    MEL.delete_all_material_expressions(mat)
    nodes = generateInputNodes(data)
    final_node = connectNodesUntilSingle(mat, nodes)
    MEL.connect_material_property(final_node, "", unreal.MaterialProperty.MP_BASE_COLOR)
    unreal.EditorAssetLibrary.save_loaded_asset(mat, True)