import numpy as np
import cv2
from matplotlib import pyplot as plt
from LandmarkDetection import *
import random

def calculate_padded_box(img_path, return_coordinates=False):

    v = bounding_box_coordinates(img_path, padding=True)
    img = cv2.imread(img_path)

    # print(v)
    mid = (int((v[0].x + v[1].x) / 2), int((v[0].y + v[1].y) / 2))

    bb = draw_bounding_box(img, v)
    bb = cv2.circle(bb, mid, 8, (255, 0, 0), -5)

    return bb

def bounding_box_coordinates(image_path, padding=False):
    landmarks = detect_landmarks(image_path)
    v = landmarks[2]
    if padding:
        try:
            v[0].x -= 50
            v[0].y -= 50
            v[2].x += 50
            v[2].y += 50
        except:
            pass
    return v[0], v[2]

def random_color():
    levels = range(32,256,32)
    return tuple(random.choice(levels) for _ in range(3))

def sift_comparison(og1, og2):
    img1 = cv2.cvtColor(og1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(og2, cv2.COLOR_BGR2GRAY)

    # sift
    sift = cv2.SIFT_create()

    keypoints_1, descriptors_1 = sift.detectAndCompute(img1, None)
    keypoints_2, descriptors_2 = sift.detectAndCompute(img2, None)

    # feature matching
    bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)

    matches = bf.match(descriptors_1, descriptors_2)
    matches = sorted(matches, key=lambda x: x.distance)
    
    return matches, keypoints_1, keypoints_2

def create_match_points(og1, og2, n):
    
    matches, keypoints_1, keypoints_2 = sift_comparison(og1, og2)
    
    for match in matches[:n]:
        print(match.distance)
        color = random_color()
        p1 = keypoints_1[match.queryIdx].pt
        p2 = keypoints_2[match.trainIdx].pt
        # print(type(p1[0]))
        og1 = cv2.circle(og1, (int(p1[0]), int(p1[1])), 8, color, 5)
        og2 = cv2.circle(og2, (int(p2[0]), int(p2[1])), 8, color, 5)
        
    return og1, og2

def crop_image_to_bounding_box(image_path, v):
    image = cv2.imread(image_path)
    crop = image[v[0].y:v[1].y, v[0].x:v[1].x]
    return crop

def sift_bounding_box_comparison(og1_path, og2_path, n):

    v1 = bounding_box_coordinates(og1_path)
    v2 = bounding_box_coordinates(og2_path)

    bb1 = crop_image_to_bounding_box(og1_path, v1)
    bb2 = crop_image_to_bounding_box(og2_path, v2)

    bb1_sift, bb2_sift = create_match_points(bb1, bb2, n)

    og1[v1[0].y:v1[1].y, v1[0].x:v1[1].x] = bb1_sift
    og2[v2[0].y:v2[1].y, v2[0].x:v2[1].x] = bb2_sift

    return og1, og2, v1, v2



if __name__=="__main__":
    name1 = 'taj1.jpeg'
    name2 = 'faketaj.jpeg'

    og1 = cv2.imread(name1)
    og2 = cv2.imread(name2)

    # image1, image2 = create_match_points(og1, og2, 10)

    box1 = calculate_padded_box(name1)
    box2 = calculate_padded_box(name2)

    bb_sift1, bb_sift2, v1, v2 = sift_bounding_box_comparison(name1, name2, 4)

    bb_sift1 = draw_bounding_box(bb_sift1, v1, padding=True)
    bb_sift2 = draw_bounding_box(bb_sift2, v2, padding=True)

    # cv2.imshow("", box1)
    # cv2.imshow("a", box2)

    # cv2.imshow("", image1)
    # cv2.imshow("a", image2)

    cv2.imshow("", bb_sift1)
    cv2.imshow("a", bb_sift2)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
