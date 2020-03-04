#! /usr/bin/env python3

import cv2
import numpy as np
import sys

def process(alpha, blur_percentage=0.01):
    contrast = cv2.equalizeHist(alpha)

    blur_amt = int(alpha.shape[0] * blur_percentage)
    # Gaussian blur kernel must be odd
    if blur_amt % 2 == 0:
        blur_amt += 1
    blur = cv2.GaussianBlur(contrast, (blur_amt, blur_amt), 0)

    _, thresh = cv2.threshold(blur,8,255,cv2.THRESH_BINARY)
    return thresh


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
        icons.append(icon)
    return icons

path = sys.argv[1]
image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
proc = process(image)
uv_bbox_coords, contours = find_blobs(proc)
icons = create_icons(image, contours)

for i in icons:
    cv2.imshow("daw", i)
    cv2.waitKey(0)
print(uv_bbox_coords)
