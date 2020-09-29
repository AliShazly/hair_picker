#! /usr/bin/env python3

import os
import sys
import argparse

try:
    import numpy as np
    import cv2
except ModuleNotFoundError:
    # Installing required packages to script directory to avoid polluting global namespace
    # maybe a bad idea, can't tell.
    deps_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dependencies")
    if not os.path.isdir(deps_folder):
        os.mkdir(deps_folder)
    sys.path.insert(1, deps_folder)

    if not os.path.isdir(os.path.join(deps_folder, "cv2")):
        # Autodesk path stuff creates conflits with pip when trying to install packages
        path_bak = sys.path
        filter_ = ["autodesk", "bifrost", "maya"]
        sys.path = [p for p in sys.path if not any(kw in p.lower() for kw in filter_)]

        # Unsupported way of installing packages, but subprocess doesn't work from inside another subprocess
        import pip
        install = ["install", "--target", deps_folder, "numpy", "opencv_python"]

        if hasattr(pip, "main"):
            pip.main(install)
        else:
            pip._internal.main(install)

        for p in path_bak:
            if p not in sys.path:
                sys.path.append(p)

    import numpy as np
    import cv2


def _imshow(img, title=''):
    cv2.imshow(f"{title}_win", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def process(image, blur_percentage, thresh_min):
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
    # if img.shape[0] != img.shape[1]:
    #     raise Exception("Provided texture is not square")

    contours, hier = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    uv_bbox_coords = []
    for cnt in contours:
        (x,y,w,h) = cv2.boundingRect(cnt)
        top_left = normalize_to_uv((x, y), image.shape[0])
        bot_right = normalize_to_uv((x+w, y+h), image.shape[0])
        uv_bbox_coords.append((top_left, bot_right))

    return uv_bbox_coords, contours


def draw_contours(img, contours):
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    contour_img = cv2.drawContours(img, contours, -1, (0,255,0), 4)
    for cnt in contours:
        (x,y,w,h) = cv2.boundingRect(cnt)
        cv2.rectangle(contour_img,(x,y),(x+w,y+h),(0,0,255),4)
    return contour_img


def auto_detect_blobs(raw_img, n_blobs, max_iter, blur=0.01, thresh_min=8):

    thresh_img = process(raw_img, blur, thresh_min)
    coords, contours = find_blobs(thresh_img)

    def clamp(n, minn, maxn):
        return max(min(maxn, n), minn)

    c = 0
    past_blur = 0
    past_thresh = 0
    while len(coords) != n_blobs:
        if c > max_iter:
            return None

        if blur == past_blur and thresh_min == past_thresh:
            return None

        print("Processing... iteration #{}".format(c))

        past_blur = blur
        past_thresh = thresh_min

        if len(coords) > n_blobs:
            blur += 0.01
            thresh_min -= 1

        elif len(coords) < n_blobs:
            blur -= 0.005
            thresh_min += 2

        blur = clamp(blur, 0, 0.08)
        thresh_min = clamp(thresh_min, 0, 30)

        thresh_img = process(raw_img, blur, thresh_min)
        coords, contours = find_blobs(thresh_img)
        c += 1

    return coords, contours


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
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--img_path", type=str)
    parser.add_argument("-o", "--out_path", type=str)
    parser.add_argument("-r", "--resolution", type=int)
    parser.add_argument("-n", "--num_blobs", type=int)
    parser.add_argument("-m", "--max_iter", type=int, default=50)
    parser.add_argument("-s", "--show_img", action="store_true")
    args = parser.parse_args()

    image = cv2.imread(args.img_path, cv2.IMREAD_GRAYSCALE)
    ret = auto_detect_blobs(image, args.num_blobs, args.max_iter)
    if ret is None:
        raise Exception("Auto detection failed.")
    else:
        uv_bbox_coords, contours = ret

    if args.show_img:
        contour_img = draw_contours(image, contours)
        _imshow(resize_keep_aspect(contour_img, height=1024)[0])

    icons, icon_sizes = create_icons(image, contours, args.resolution)
    save_data(icons, icon_sizes, uv_bbox_coords, args.out_path)

