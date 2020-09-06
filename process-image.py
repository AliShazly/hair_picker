#! /usr/bin/env python3

import os
import sys
import cv2
import numpy as np

def _imshow(img, title=''):
    cv2.imshow(f"{title}_win", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def process(image, blur_percentage=0.01, thresh_min=8):
    contrast = cv2.equalizeHist(image)

    blur_amt = int(image.shape[0] * blur_percentage)
    # Gaussian blur kernel must be odd
    if blur_amt % 2 == 0:
        blur_amt += 1
    blur = cv2.GaussianBlur(contrast, (blur_amt, blur_amt), 0)

    _, thresh = cv2.threshold(blur, thresh_min, 255, cv2.THRESH_BINARY)
    return thresh


def resize_keep_aspect(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    resized = cv2.resize(image, dim, interpolation=inter)
    return resized, dim


def normalize_to_uv(coord, max_size):
    normalized = [val / max_size for val in coord]
    normalized[1] = 1 - normalized[1]
    return tuple(normalized)


def find_blobs(img):
    if img.shape[0] != img.shape[1]:
        raise Exception("Provided texture is not square")

    contours, hier = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    rgb = cv2.cvtColor(img ,cv2.COLOR_GRAY2RGB)
    contour_img = cv2.drawContours(rgb, contours, -1, (0,255,0), 4)
    
    uv_bbox_coords = []
    for cnt in contours:
        (x,y,w,h) = cv2.boundingRect(cnt)
        top_left = normalize_to_uv((x, y), image.shape[0])
        bot_right = normalize_to_uv((x+w, y+h), image.shape[0])
        uv_bbox_coords.append((top_left, bot_right))

        cv2.rectangle(contour_img,(x,y),(x+w,y+h),(0,0,255),4)

    return uv_bbox_coords, contours, contour_img


def create_icons(orig_img, contours, height):
    icons = []
    icon_sizes = []
    for cnt in contours:
        (x,y,w,h) = cv2.boundingRect(cnt)
        icon = orig_img[y:y+h, x:x+w]
       
        # Icon might be upside down, better than horizontal. 
        if w > h:
            icon = cv2.rotate(icon, cv2.ROTATE_90_CLOCKWISE)  
        
        icon_resized, dim = resize_keep_aspect(icon, height=height)
        icons.append(icon_resized)
        icon_sizes.append(dim)

    return icons, icon_sizes


def save_data(icons, icon_sizes, bbox_coords, path):
    icon_path = os.path.join(path, "icons/")
    if os.path.exists(icon_path):
        for f in os.listdir(icon_path):
            full_path = os.path.join(icon_path, f)
            os.remove(full_path)
    else:
        os.mkdir(icon_path)

    for idx, img in enumerate(icons):
        cv2.imwrite(f"{icon_path}/{idx}.png", img)

    with open(f"{icon_path}/icon_sizes.txt", "w+") as f:
        f.write(str(icon_sizes))

    with open(f"{path}/coords.txt", "w+") as f:
        f.write(str(bbox_coords))


if __name__ == "__main__":
    img_path = sys.argv[1]
    out_path = sys.argv[2]
    blur_percentage = float(sys.argv[3]) / 100
    icon_height = int(sys.argv[4])
    thresh_min = int(sys.argv[5])
    show_img = True if sys.argv[6] == "True" else False

    image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    proc = process(image, blur_percentage, thresh_min)
    uv_bbox_coords, contours, contour_img = find_blobs(proc)
    
    if show_img:
        _imshow(resize_keep_aspect(contour_img, height=1024)[0])
    
    icons, icon_sizes = create_icons(image, contours, icon_height)
    save_data(icons, icon_sizes, uv_bbox_coords, out_path)
