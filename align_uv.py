import maya.cmds as cmds

def get_uv_dimensions(obj):
    cmds.select("{}.map[0:]".format(obj))
    (xmin, xmax), (ymin, ymax) = cmds.polyEvaluate(boundingBox2d=True)
    width = xmax - xmin
    height = ymax - ymin
    return width, height

def get_uv_center(obj):
    cmds.select("{}.map[0:]".format(obj))
    (xmin, xmax), (ymin, ymax) = cmds.polyEvaluate(boundingBox2d=True)
    center = ((xmin + xmax) / 2, (ymin + ymax) / 2)
    return center

def square_unwrap(obj):
    cmds.polyForceUV("{}.f[0:]".format(obj), unitize=True)
    cmds.select("{}.map[0:]".format(obj))
    cmds.polyMapSewMove()

def scale_uvs(obj, new_width, new_height):
    old_width, old_height = get_uv_dimensions(obj)
    center = get_uv_center(obj)
    scale_u = new_width / old_width
    scale_v = new_height / old_height
    cmds.select("{}.map[0:]".format(obj))
    cmds.polyEditUV(pu=center[0], pv=center[1], scaleU=scale_u, scaleV=scale_v)

def transform_uvs(obj, new_center):
    old_center = get_uv_center(obj)
    transform_u = new_center[0] - old_center[0]
    transform_v = new_center[1] - old_center[1]
    cmds.select("{}.map[0:]".format(obj))
    cmds.polyEditUV(u=transform_u, v=transform_v)

def rotate_uvs(obj, angle):
    cmds.select("{}.map[0:]".format(obj))
    center = get_uv_center(obj)
    cmds.polyEditUV(pu=center[0], pv=center[1], a=angle)

def align_uv_to_bbox(bbox_coords):
    try:
        obj = cmds.ls(selection=True)[0]
    except (IndexError, TypeError):
        raise Exception("Select a piece of geometry")
    (xmin, ymax), (xmax, ymin) = bbox_coords # Assuming bbox coords are in opencv format
    bbox_width = xmax - xmin
    bbox_height = ymax - ymin
    bbox_center = ((xmin + xmax) / 2, (ymin + ymax) / 2)

    square_unwrap(obj)
    scale_uvs(obj, bbox_width, bbox_height)
    transform_uvs(obj, bbox_center)
    cmds.select(obj, r=True)

def rotate_keep_bbox(angle):
    try:
        obj = cmds.ls(selection=True)[0]
    except (IndexError, TypeError):
        raise Exception("Select a piece of geometry")
    rotate_uvs(obj, angle)
    width, height = get_uv_dimensions(obj)
    scale_uvs(obj, new_width=height, new_height=width)
    cmds.select(obj, r=True)

