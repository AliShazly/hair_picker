import maya.cmds as cmds

def square_unwrap(obj):
    cmds.polyForceUV("{}.f[0:]".format(obj), unitize=True)
    cmds.select("{}.map[0:]".format(obj))
    cmds.polyMapSewMove()
    
def scale_uvs(obj, new_width, new_height):
    cmds.select("{}.map[0:]".format(obj))
    (xmin, xmax), (ymin, ymax) = cmds.polyEvaluate(boundingBox2d=True)
    old_width = xmax - xmin
    old_height = ymax - ymin
    scale_u = new_width / old_width
    scale_v = new_height / old_height
    cmds.polyEditUV(scaleU=scale_u, scaleV=scale_v)
    
def transform_uvs(obj, new_center):
    cmds.select("{}.map[0:]".format(obj))
    (xmin, xmax), (ymin, ymax) = cmds.polyEvaluate(boundingBox2d=True)
    old_center = ((xmin + xmax) / 2, (ymin + ymax) / 2)
    transform_u = new_center[0] - old_center[0]
    transform_v = new_center[1] - old_center[1]
    cmds.polyEditUV(u=transform_u, v=transform_v)

def allign_uv_to_bbox(bbox_coords):
    try:
        obj = cmds.ls(selection=True)[0]
    except IndexError:
        raise Exception("Select a piece of geometry")
    (xmin, ymax), (xmax, ymin) = bbox_coords # Assuming bbox coords are in opencv format
    bbox_width = xmax - xmin
    bbox_height = ymax - ymin
    bbox_center = ((xmin + xmax) / 2, (ymin + ymax) / 2)
    
    square_unwrap(obj)
    scale_uvs(obj, bbox_width, bbox_height)
    transform_uvs(obj, bbox_center)
    cmds.select(obj, r=True)
