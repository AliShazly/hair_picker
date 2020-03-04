import pymel.core as pm


def buttonPressed(*args):
    pm.iconTextButton( style='iconAndTextCentered', image1='sphere.png', label='sphere' )
    win.show()

win = pm.window(title="window")
layout = pm.columnLayout()
pm.button(label="Create button", command=buttonPressed)
win.show()




def generate_ui():
    # Save icon pictures to /icons
    # create buttons & refresh UI
    # store coords in global variables (?)
    pass
    
