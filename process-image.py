#! /usr/bin/env python3

import os
import sys
import cv2
import numpy as np

def process(alpha, blur_percentage=0.01):
    contrast = cv2.equalizeHist(alpha)

    blur_amt = int(alpha.shape[0] * blur_percentage)
    # Gaussian blur kernel must be odd
    if blur_amt % 2 == 0:
        blur_amt += 1
    blur = cv2.GaussianBlur(contrast, (blur_amt, blur_amt), 0)

    _, thresh = cv2.threshold(blur,8,255,cv2.THRESH_BINARY)
    return thresh

def resize_keep_aspect(img, size):
    old_height, old_width = img.shape[:2]
    if img.shape[0] >= size:
        aspect_ratio = size / float(old_height)
        dim = (int(old_width * aspect_ratio), size)
        img = cv2.resize(img, dim, interpolation=cv2.INTER_BILINEAR)
    elif img.shape[1] >= size:
        aspect_ratio = size / float(old_width)
        dim = (size, int(old_height * aspect_ratio))
        img = cv2.resize(img, dim, interpolation=cv2.INTER_BILINEAR)
    return img


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
        icon_resized = resize_keep_aspect(icon, 256)
        icons.append(icon_resized)
    return icons


def save_data(icons, bbox_coords, path):
    icon_path = os.path.join(path, "icons/")
    if not os.path.exists(icon_path):
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
