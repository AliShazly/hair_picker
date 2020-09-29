import subprocess
import os
import sys
from ast import literal_eval
import getpass

import pymel.core as pm
import maya.cmds as cmds

import align_uv

################################################################################################
# If you are getting an error:
#   change SCRIPT_DIR to the hair_picker folder in your maya scripts directory:
#   ex. SCRIPT_DIR = "C:/Users/<user_name>/Documents/maya/scripts/hair_picker"  (no backslashes!)
#################################################################################################
SCRIPT_DIR = os.path.split(align_uv.__file__)[0]

if not os.path.exists(SCRIPT_DIR):
    raise Exception("Change SCRIPT_DIR in the ui.py file")

PROCESSING_SCRIPT_PATH = os.path.join(SCRIPT_DIR, "process-image.py")
ICONS_DIR = os.path.join(SCRIPT_DIR, "icons/")
COORDS_PATH = os.path.join(SCRIPT_DIR, "coords.txt")
ICON_SIZE_PATH = os.path.join(ICONS_DIR, "icon_sizes.txt")

class UI:
    def __init__(self):
        self.current_window = self._create_ui_track_window()
        self.texture_path = None


    def _process_texture(self, num_blobs, max_iter, icon_size=256, show_img=False):

        if self.texture_path is None:
            self._prompt_for_file()

        # Assuming user at least has python3 installed
        if sys.platform.startswith("win"):
            python_call = "py -3"
        else:
            try:
                subprocess.check_output(["python3","--version"])
                python_call = "python3"
            except subprocess.CalledProcessError:
                python_call = "python"

        show_flag = "-s" if show_img else ""

        # Generating icons and uv coords from diffuse texture using external OpenCV script
        cmd = "{} {} -i {} -o {} -r {} -n {} -m {} {}".format(python_call, PROCESSING_SCRIPT_PATH, self.texture_path, SCRIPT_DIR, icon_size, num_blobs, max_iter, show_flag)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        stderr = p.stderr.read()
        if stderr:
            raise Exception("Processing script failed: {}".format(stderr))


        with open(COORDS_PATH, "r") as f:
            uv_coords = literal_eval(f.read())

        with open(ICON_SIZE_PATH, "r") as f:
            icon_sizes = literal_eval(f.read())

        # Icons are named after the index of their respective uv coordinates
        icon_paths = [os.path.join(ICONS_DIR, "{}.png".format(i)) for i, _ in enumerate(uv_coords)]

        return uv_coords, icon_paths, icon_sizes


    def _refresh_ui(self):
        pos = self.main_win.getTopLeftCorner()

        num_blobs = int(self.num_blobs_field.getValue()[0])
        icon_size = int(self.icon_size_field.getValue()[0])
        max_iter = int(self.max_iter_field.getValue()[0])
        show_img = self.show_image_checkbox.getValue()
        self.uv_coords, self.icon_paths, self.icon_sizes = self._process_texture(num_blobs, max_iter, icon_size, show_img)

        new_window = self._create_ui_track_window(pos)
        pm.deleteUI(self.current_window)
        self.current_window = new_window


    def _prompt_for_file(self):
        filename = pm.fileDialog2(fileMode=1, caption="Choose Texture")
        if filename is None:
            raise Exception("No file chosen.")
        self.texture_path = filename[0]


    def _create_ui_track_window(self, pos=None):
        # I have to keep track of the window ID because i run into problems when I delete and recreate the window using the PyMel object
        existing_windows = set(cmds.lsUI(type = 'window'))
        self._create_ui(pos)
        new_windows = set(cmds.lsUI(type = 'window')) - existing_windows
        current_window = list(new_windows)[0]
        return current_window


    def _create_ui(self, pos=None):

        if pos:
            self.main_win = pm.window(title="Hair Picker", sizeable=True, topLeftCorner=pos)
        else:
            self.main_win = pm.window(title="Hair Picker", sizeable=True)

        with self.main_win:

            with pm.windows.frameLayout(collapsable=True, l="Params"):
                with pm.verticalLayout():
                    self.num_blobs_field = pm.intFieldGrp(numberOfFields=1, label="Num blobs to detect")
                    self.icon_size_field = pm.intFieldGrp(numberOfFields=1, label="Icon size", value1=256)
                    self.max_iter_field = pm.intFieldGrp(numberOfFields=1, label="Max iterations", value1=50)
                    self.show_image_checkbox = pm.checkBox(label="Show processed image")
                    self.prompt_file_button = pm.button(command = pm.windows.Callback(self._prompt_for_file), label="Choose Texture")
                    self.refresh_ui_button = pm.button(command = pm.windows.Callback(self._refresh_ui), label="Process Texture")
                    self.rotate_positive_button = pm.button(command=pm.windows.Callback(align_uv.rotate_keep_bbox, 90), label="Rotate UV Clockwise")
                    self.rotate_negative_button = pm.button(command=pm.windows.Callback(align_uv.rotate_keep_bbox, -90), label="Rotate UV Counter-clockwise")


            with pm.windows.frameLayout(collapsable=True, l="Blobs Found"):
                with pm.scrollLayout():
                    with pm.autoLayout():
                        with pm.windows.horizontalLayout():
                            try:
                                for icon, coord, size in zip(self.icon_paths, self.uv_coords, self.icon_sizes):
                                    pm.iconTextButton(command=pm.windows.Callback(align_uv.align_uv_to_bbox, coord),
                                        style='iconAndTextCentered', image1=icon, w=size[0], h=size[1])
                            except AttributeError:
                                pass
