from ui import *
import maya.cmds as cmds

# Killing all other hair picker windows
for win in cmds.lsUI(windows=True):
    if cmds.window(win, query=True, title=True) == "Hair Picker":
        cmds.deleteUI(win)
        break

_ui = UI()
