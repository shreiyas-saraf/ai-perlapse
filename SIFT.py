import numpy as np
import cv2
from matplotlib import pyplot as plt
from LandmarkDetection import *
import random
from PIL import Image
import math
from scipy.spatial import ConvexHull, convex_hull_plot_2d

# TODO: try to see relative distance from mean in one and then compare in other?
# TODO: try to compare anomalies

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def calculate_distance(distances, num_keypoints=5):
    distances = np.array(distances).reshape((num_keypoints, 1))
    weights = np.ones((1,num_keypoints))
    # weights[0][:4] = np.array([0.5, 0.25, 0.125, 0.07])
    # print(weights)
    return np.dot(weights, distances)


def compute_angle(p1, p2):
    # angle of p2 with respect to p1
    if p2 == p1:
        return 1
    hyp = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    adjc = p2[0] - p1[0]
    angle = math.acos(adjc / hyp)
    return angle / (math.pi / 2)


def compute_distance(p1, p2):
    if p2 == p1:
        return 0
    hyp = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    return hyp

def normalize(x, img):
    return x/(img.shape[0]*img.shape[1])


def calculate_point_similarity(kp1, kp2):
    # kp1/2 = [(x, y), (x, y), (x, y), (x, y)]
    matrix1 = np.zeros(shape=(4, 4))
    matrix2 = np.zeros(shape=(4, 4))

    for r in range(4):
        for c in range(4):
            matrix1[r][c] = compute_distance(kp1[r].pt, kp1[c].pt)
            matrix2[r][c] = compute_distance(kp2[r].pt, kp2[c].pt)

    return (
        np.divide(matrix1, matrix2),
    )

def convex_hull(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # convert to grayscale
    blur = cv2.blur(gray, (3, 3))  # blur the image
    ret, thresh = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    hull = []
    # calculate points for each contour
    for i in range(len(contours)):
    # creating convex hull object for each contour
        hull.append(cv2.convexHull(contours[i], False))

    # create an empty black image
    drawing = np.zeros((thresh.shape[0], thresh.shape[1], 3), np.uint8)

    # draw contours and hull points
    for i in range(len(contours)):
        color_contours = (0, 255, 0)  # green - color for contours
        color = (255, 0, 0)  # blue - color for convex hull
        # draw ith contour
        cv2.drawContours(drawing, contours, i, color_contours, 1, 8, hierarchy)
        # draw ith convex hull object
        cv2.drawContours(drawing, hull, i, color, 1, 8)

    return drawing

def point_distances_using_complex(kp1, kp2):
    # Convert x, y coordinates into complex numbers
    # so that the distances are much easier to compute
    z1 = np.array([[complex(c.pt[0], c.pt[1]) for c in kp1]])
    z2 = np.array([[complex(c.pt[0], c.pt[1]) for c in kp2]])

    # Computes the intradistances between keypoints for each image
    KP_dist1 = abs(z1.T - z1)
    KP_dist2 = abs(z2.T - z2)

    # Distance between featured matched keypoints
    # FM_dist = abs(z2 - z1)
    return KP_dist1[:906, :906], KP_dist2, np.linalg.det(np.divide(KP_dist1[:906, :906], KP_dist2))


def calculate_padded_box(img_path, return_coordinates=False):
    v = bounding_box_coordinates(img_path, padding=True)
    img = cv2.imread(img_path)

    # print(v)
    mid = (int((v[0].x + v[1].x) / 2), int((v[0].y + v[1].y) / 2))

    bb = draw_bounding_box(img, v)
    bb = cv2.circle(bb, mid, 8, (255, 0, 0), -5)

    return bb


def bounding_box_coordinates(image_path, padding=False):
    try:
        landmarks = detect_landmarks(image_path)
    except:
        return Point(0,0), Point(cv2.imread(image_path).shape[1], cv2.imread(image_path).shape[0])
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
    levels = range(32, 256, 32)
    return tuple(random.choice(levels) for _ in range(3))


def sift_comparison(og1, og2):
    img1 = cv2.cvtColor(og1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(og2, cv2.COLOR_BGR2GRAY)

    # sift
    sift = cv2.SIFT_create()

    keypoints_1, descriptors_1 = sift.detectAndCompute(img1, None)
    keypoints_2, descriptors_2 = sift.detectAndCompute(img2, None)
    # TODO: delete keypoint if on edge

    # feature matching
    bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)

    matches = bf.match(descriptors_1, descriptors_2)
    matches = sorted(matches, key=lambda x: x.distance)

    return matches, keypoints_1, keypoints_2


def create_match_points(og1, og2, n):
    matches, keypoints_1, keypoints_2 = sift_comparison(og1, og2)
    distances = []
    p1s, p2s = [], []
    for match in matches[:n]:
        # print(match.distance)
        distances.append(match.distance)
        color = random_color()
        p1 = keypoints_1[match.queryIdx].pt
        p1s.append(p1)
        p2 = keypoints_2[match.trainIdx].pt
        p2s.append(p2)
        # print(type(p1[0]))
        og1 = cv2.circle(og1, (int(p1[0]), int(p1[1])), 8, (255, 0, 0), 5)
        og2 = cv2.circle(og2, (int(p2[0]), int(p2[1])), 8, (255, 0, 0), 5)

    return og1, og2, distances, p1s, p2s


def crop_image_to_bounding_box(image_path, v):
    image = cv2.imread(image_path)
    crop = image[v[0].y:v[1].y, v[0].x:v[1].x]
    return crop


def sift_bounding_box_comparison(og1_path, og2_path, n, bb=True):

    og1 = cv2.imread(og1_path)
    og2 = cv2.imread(og2_path)

    if not bb:
        bb1 = cv2.imread(og1_path)
        bb2 = cv2.imread(og2_path)
    else:
        v1 = bounding_box_coordinates(og1_path)
        v2 = bounding_box_coordinates(og2_path)

        bb1 = crop_image_to_bounding_box(og1_path, v1)
        bb2 = crop_image_to_bounding_box(og2_path, v2)

        # print("1 done")

    bb1_sift, bb2_sift, distances, kp1, kp2 = create_match_points(bb1, bb2, n)

    # print(calculate_distance(distances, n))
    # print(calculate_point_similarity(kp1, kp2))
    # print(point_distances_using_complex(kp1, kp2))

    og1[v1[0].y:v1[1].y, v1[0].x:v1[1].x] = bb1_sift
    og2[v2[0].y:v2[1].y, v2[0].x:v2[1].x] = bb2_sift

    return og1, og2, v1, v2, kp1, kp2

def batch_rearrange(folder):
    out = []
    images = [item for item in os.listdir(folder)]
    # images =[item for item in os.listdir(folder)]

    for i in range(len(images)-1):
        if images[1].endswith("png"):
            name1 = folder+"/"+images[i]
            name2 = folder+"/"+images[i+1]

            print(name1, name2)
            # og1 = cv2.imread(name1)
            # og2 = cv2.imread(name2)

            # image1, image2 = create_match_points(og1, og2, 10)

            # box1 = calculate_padded_box(name1)
            # box2 = calculate_padded_box(name2)
            #
            bb_sift1, bb_sift2, v1, v2, kp1, kp2 = sift_bounding_box_comparison(name1, name2, 3)

            # bb_sift1 = draw_bounding_box(bb_sift1, v1, padding=True)
            # bb_sift2 = draw_bounding_box(bb_sift2, v2, padding=True)

            # print(kp1[1], kp1[2])
            print(normalize(compute_distance(kp1[1], kp1[2]), cv2.imread(name1)))

            # print(kp2[1], kp2[2])
            print(normalize(compute_distance(kp2[1], kp2[2]), cv2.imread(name2)))
            #
            cv2.imshow("1", bb_sift1)
            cv2.imshow("2", bb_sift2)
            #
            cv2.waitKey(0)
            cv2.destroyAllWindows()

def process_jpg_png(image_path):
    im1 = Image.open(image_path)
    im1.save(image_path[:8] + ".png")

if __name__ == "__main__":
    name1 = 'hyp6.png'
    name2 = 'hyp2.png'

    folder = "images/white_house"
    batch_rearrange(folder)

