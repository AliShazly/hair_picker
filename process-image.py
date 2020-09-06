#! /usr/bin/env python3

import os
import sys
import cv2
import numpy as np

def _imshow(img, title=''):
    cv2.imshow(f"{title}_win", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def process(alpha, blur_percentage=0.01):
    contrast = cv2.equalizeHist(alpha)

    blur_amt = int(alpha.shape[0] * blur_percentage)
    # Gaussian blur kernel must be odd
    if blur_amt % 2 == 0:
        blur_amt += 1
    blur = cv2.GaussianBlur(contrast, (blur_amt, blur_amt), 0)

    _, thresh = cv2.threshold(blur,8,255,cv2.THRESH_BINARY)
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
    return resized 


def normalize_to_uv(coord, max_size):
    normalized = [val / max_size for val in coord]
    normalized[1] = 1 - normalized[1]
    return tuple(normalized)


def find_blobs(img):
    if img.shape[0] != img.shape[1]:
        raise Exception("Provided texture is not square")

    contours, hier = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    uv_bbox_coords = []
    for cnt in contours:
        (x,y,w,h) = cv2.boundingRect(cnt)
        top_left = normalize_to_uv((x, y), image.shape[0])
        bot_right = normalize_to_uv((x+w, y+h), image.shape[0])
        uv_bbox_coords.append((top_left, bot_right))

    return uv_bbox_coords, contours


def create_icons(orig_img, contours):
    icons = []
    for cnt in contours:
        (x,y,w,h) = cv2.boundingRect(cnt)
        icon = orig_img[y:y+h, x:x+w]
        if w > h:
            icon_resized = resize_keep_aspect(icon, width=256)
        else:
            icon_resized = resize_keep_aspect(icon, height=256)
        icons.append(icon_resized)
    return icons


def save_data(icons, bbox_coords, path):
    icon_path = os.path.join(path, "icons/")
    if os.path.exists(icon_path):
        for f in os.listdir(icon_path):
            full_path = os.path.join(icon_path, f)
            os.remove(full_path)
    else:
        os.mkdir(icon_path)


    for idx, img in enumerate(icons):
        cv2.imwrite(f"{icon_path}/{idx}.png", img)

    with open(f"{path}/coords.txt", "w+") as f:
        f.write(str(bbox_coords))


if __name__ == "__main__":
    img_path = sys.argv[1]
    out_path = sys.argv[2]

    image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    proc = process(image)
    uv_bbox_coords, contours = find_blobs(proc)
    icons = create_icons(image, contours)
    save_data(icons, uv_bbox_coords, out_path)
