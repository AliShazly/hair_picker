import pymel.core as pm

import subprocess
import os
import sys
from ast import literal_eval
# import allign-uv.py


# Only change this
#SCRIPT_DIR = "/home/ali/projects/hair-picker"
SCRIPT_DIR = "G:/personalProjects/hair-picker/"

PROCESSING_SCRIPT_PATH = os.path.join(SCRIPT_DIR, "process-image.py")
ICONS_DIR = os.path.join(SCRIPT_DIR, "icons/")
COORDS_PATH = os.path.join(SCRIPT_DIR, "coords.txt")

class UI:
    def __init__(self):
        self.uv_coords, self.icon_paths = self._refresh_icons()
    
    def _read_coords(self, file_path):
        with open(file_path, "r") as f:
            data = f.read()
        return literal_eval(data)

    def _refresh_icons(self):
        
        # Getting diffuse texture path
        shape_node = cmds.ls(dag=True, o=True, s=True, sl=True)
        shading_grps = cmds.listConnections(shape_node, type="shadingEngine")
        shaders = cmds.ls(cmds.listConnections(shading_grps), materials=1)
        file_node = cmds.listConnections("{}.color".format(shaders[0]), type="file")
        img_path = cmds.getAttr("{}.fileTextureName".format(file_node[0]))
        
        
        # Generating icons and uv coords from diffuse texture using external script
        if sys.platform == "win32":
            python_call = "python"
        else:
            python_call = "python3"

        ret_code = subprocess.call("{} {} {} {}".format(python_call, PROCESSING_SCRIPT_PATH, img_path, SCRIPT_DIR), shell=True)
        if ret_code == 1:
            raise Exception("Processing script failed. Do you have numPy and openCV installed?")

        uv_coords = self._read_coords(COORDS_PATH)
        # Icons are named after the index of their respective uv coordinates
        icon_paths = [os.path.join(ICONS_DIR, "{}.png".format(i)) for i, _ in enumerate(uv_coords)]
        return uv_coords, icon_paths


    def _create_ui(self):
        main_win = pm.window(title="Hair Picker", sizeable=True, wh=(512, 768))
        with main_win:
            with pm.scrollLayout(childResizable=True):
                with pm.columnLayout():
                    for icon, coord in zip(self.icon_paths, self.uv_coords):
                        pm.iconTextButton(command=pm.windows.Callback(allign_uv_to_bbox, coord), style='iconAndTextCentered', image1=icon)


ui = UI()
ui._create_ui()
