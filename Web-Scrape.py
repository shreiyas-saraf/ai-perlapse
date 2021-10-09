from urllib.request import urlopen as uReq
import requests
from bs4 import BeautifulSoup
from google.cloud import vision
import io
import os
import glob
from selenium import webdriver
import pandas as pd


# import cv2


def main_function():
    download_image()


def user_place_input():
    desired_place = input('Enter the location/monument: ')
    return desired_place


def url_builder():
    search_url_sec1 = 'https://www.google.com/search?q='
    search_url_sec2 = '&rlz=1C5CHFA_enUS968US968&sxsrf=AOaemvL8Bn72Z5AcrPjtkFwRj6PkDPrZSA:1633761894622&source=lnms&tbm=isch&sa=X&ved=2ahUKEwj-94Cr3bzzAhWYkHIEHWcDAHEQ_AUoAXoECAEQAw&biw=1440&bih=789&dpr=2'

    # desired_place = user_place_input()
    desired_place = "Taj Mahal"
    if desired_place == ' ':
        string_index = '+'
    else:
        string_index = desired_place

    return search_url_sec1 + string_index + search_url_sec2


def web_scrape():
    search_url = url_builder()
    r = requests.get(search_url)

    soup = BeautifulSoup(r.text, 'html.parser')
    images_source_codes = soup.find_all('img')
    list_of_image_src = []
    for i in images_source_codes:
        if '.gif' not in i['src']:
            list_of_image_src.append(i['src'])
    return list_of_image_src


def download_image():
    try:
        os.mkdir(os.path.join(os.getcwd(), 'images_collection'))
    except:
        pass
    os.chdir(os.path.join(os.getcwd(), 'images_collection'))
    list_of_image_src = web_scrape()
    count = 0
    for i in list_of_image_src:
        count += 1
        image_name = 'image' + str(count)
        file_of_images = open(image_name + '.jpg', 'wb')
        final_image = requests.get(i)
        file_of_images.write(final_image.content)

    file_of_images.close()


"""def valid_images():
    i = 0
    while i < 20:
        detect_landmarks(ai-perlapse/images_collection/image)
"""


def detect_landmarks(path, landmark_name):
    """Detects landmarks in the file."""

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'/Users/pats/OneDrive/My Stuff/VandyHacks/ai-perlapse/ServiceAccountKey.json'
    client = vision.ImageAnnotatorClient()
    # print(os.getcwd())

    for filename in os.listdir(path):
        # print(filename)
        filename = path+"/"+filename
        # filename = "/Users/pats/OneDrive/My Stuff/VandyHacks/ai-perlapse/images_collection/"+filename
        with io.open(filename, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)

        response = client.landmark_detection(image=image)
        landmarks = response.landmark_annotations

        try:
            if not landmarks[0].description.startswith(landmark_name):
                # TODO: CHECK FOR LOCATION
                # os.remove(filename)
                print("NOT MATCHING:"+filename + " - "+landmarks[0].description)
            elif landmarks[0].score < 0.5:
                # os.remove(filename)
                print("SCORE LOW:"+filename)

        except:
            print("NO LANDMARKS:"+filename)


    # return (
    #     landmarks[0].description,
    #     landmarks[0].score,
    #     landmarks[0].bounding_poly.vertices,
    #     landmarks[0].locations
    # )

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


"""
image = "drawing.png"
landmarks = detect_landmarks(image)
vertices = landmarks[2]

im = cv2.imread(image)

start = (vertices[0].x, vertices[0].y)
end = (vertices[2].x, vertices[2].y)

color = (255, 0, 0)
thickness = 2

im = cv2.rectangle(im, start, end, color, thickness)

print(landmarks[0])
print(landmarks[1])

cv2.imshow("image", im)
cv2.waitKey(0)
cv2.destroyAllWindows()

"""
# main_function()
folder_path = "Liberty Pics"
detect_landmarks(folder_path, "Statue of Liberty")
