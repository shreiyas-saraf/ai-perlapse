from google.cloud import vision
import io
import os
import pandas as pd
import cv2

def detect_landmarks(path):
    """Detects landmarks in the file."""

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'ServiceAccountKey.json'
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.landmark_detection(image=image)
    landmarks = response.landmark_annotations

    return (
        landmarks[0].description,
        landmarks[0].score,
        landmarks[0].bounding_poly.vertices,
        landmarks[0].locations
    )
    #
    # for landmark in landmarks[:1]:
    #     print(landmark.description)
    #     print(landmark.score)
    #     print(landmark.bounding_poly.vertices)
    #     for location in landmark.locations:
    #         lat_lng = location.lat_lng
    #         print('Latitude {}'.format(lat_lng.latitude))
    #         print('Longitude {}'.format(lat_lng.longitude))
    #
    # if response.error.message:
    #     raise Exception(
    #         '{}\nFor more info on error messages, check: '
    #         'https://cloud.google.com/apis/design/errors'.format(
    #             response.error.message))

image = "drawing.png"
landmarks = detect_landmarks(image)
vertices = landmarks[2]

im = cv2.imread(image)

start = (vertices[0].x, vertices[0].y)
end = (vertices[2].x, vertices[2].y)

color = (255,0,0)
thickness = 2

im = cv2.rectangle(im, start, end, color, thickness)

print(landmarks[0])
print(landmarks[1])

cv2.imshow("image", im)
cv2.waitKey(0)
cv2.destroyAllWindows()



