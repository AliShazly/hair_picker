import pymel.core as pm

import subprocess
import os
from ast import literal_eval
# import allign-uv.py


# Only change this
script_dir = "/home/ali/projects/hair-picker"

processing_script_path = os.path.join(script_dir, "process-image.py")
icons_dir = os.path.join(script_dir, "icons/")
coords_path = os.path.join(script_dir, "coords.txt")

def get_diffuse_texture(shape_node):
    shading_grps = cmds.listConnections(shape_node, type="shadingEngine")
    shaders = cmds.ls(cmds.listConnections(shading_grps), materials=1)
    file_node = cmds.listConnections("{}.color".format(shaders[0]), type="file")
    return cmds.getAttr("{}.fileTextureName".format(file_node[0]))

def read_coords(file_path):
    with open(file_path, "r") as f:
        data = f.read()
    return literal_eval(data)

def generate_ui(window):
    shape_node_selection = cmds.ls(dag=True, o=True, s=True, sl=True)
    img_path = get_diffuse_texture(shape_node_selection)
    subprocess.call("python3 {} {} {}".format(processing_script_path, img_path, script_dir), shell=True)
    coords = read_coords(coords_path)
    
    for idx, coord in enumerate(coords):
        icon_path = os.path.join(icons_dir, "{}.png".format(idx))
        pm.iconTextButton(command=pm.windows.Callback(allign_uv_to_bbox, coord), style='iconAndTextCentered', image1=icon_path)
        window.show()
    
win = pm.window(title="window")
layout = pm.columnLayout()
generate_ui(win)