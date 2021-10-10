import hashlib
import time

import PIL
from PIL import Image
import requests
from selenium import webdriver
import os
import io
from google.cloud import vision

DRIVER_PATH = '/Users/pats/webdriver/chromedriver 4'
wd = webdriver.Chrome(executable_path=DRIVER_PATH)
wd.get('https://google.com')


# vision_client = vision.Client('ServiceAccountKey.json')


def persist_image(folder_path: str, url: str, unique_file_number: int):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path, 'image' + str(unique_file_number) + '.png')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")


def fetch_image_urls(query: str, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: int = 1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

        # build the google query

    # search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
    # search_url = "https://www.google.com/search?as_st=y&tbm=isch&as_q={" \
    #             "q}&as_epq=&as_oq=&as_eq=&cr=&as_sitesearch=&safe=images&tbs=isz:lt,islt:qsvga "
    # query = query + " imagesize:large"
    # load the page
    search_url = "https://www.google.com/search?q={q}%20&tbm=isch&safe=images&tbs=isz:l&hl=en&sa=X&ved" \
                 "=0CAIQpwVqFwoTCNDC3M3Xv_MCFQAAAAAdAAAAABAc&biw=1440&bih=722 "
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)

        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls


def search_and_download(search_term: str, driver_path: str, number_images: int, target_path='./images'):
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with webdriver.Chrome(executable_path=driver_path) as wd:
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=0.5)
    unique_file_number = 1
    for elem in res:
        try:
            persist_image(target_folder, elem, unique_file_number)
            unique_file_number += 1
        except:
            pass


def resolution_based_filter(search_term):
    removed = 0
    folder_path = 'images/' + search_term.replace(" ", "_")
    for file_name in os.listdir(folder_path):
        file_name = os.path.join(folder_path, file_name)
        image2 = PIL.Image.open(file_name)
        width, height = image2.size
        if width < 300 or height < 400:
            print("REMOVING LOW RESOLUTION PICTURE: " + file_name)
            print("With resolution:"+ str(width) + " x " + str(height))
            os.remove(file_name)
            removed += 1
    return removed


def feature_based_filter(search_term):
    print()
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'ServiceAccountKey.json'
    client = vision.ImageAnnotatorClient()
    # [END vision_python_migration_client]

    # Loads the image into memory
    folder_path = 'images/' + search_term.replace(" ", "_")
    firstlabels = []
    firstIteration = True
    removed = 0
    for file_name in os.listdir(folder_path):
        file_name = os.path.join(folder_path, file_name)
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)

        # Performs label detection on the image file
        response = client.label_detection(image=image)
        labels = response.label_annotations

        similarity = 0
        # print('Labels:')
        i = 0
        if firstIteration:
            # print(file_name)
            for label in labels:
                firstlabels.append(label.description)
            firstIteration = False

        else:
            current_labels = []
            for label in labels:
                current_labels.append(label.description)
                if label.description in firstlabels:
                    # print(label.description + " MATCHES " + firstlabels[i])
                    similarity += 1
                i += 1
            print(file_name)
            if similarity < 3:
                os.remove(file_name)
                print(current_labels)
                print("REMOVE BAD IMAGE:" + file_name + "\n")
                removed += 1
            else:
                print("GOOD IMAGE\n")
    return removed


def landmark_rating_filter(search_term):
    removed = 0
    print("LANDMARK RATING BASED FILTER")
    """Detects landmarks in the file. """
    folder_path = 'images/' + search_term.replace(" ", "_")
    os.environ[
        'GOOGLE_APPLICATION_CREDENTIALS'] = r'ServiceAccountKey.json'
    client = vision.ImageAnnotatorClient()
    # print(os.getcwd())

    for file_name in os.listdir(folder_path):
        file_name = os.path.join(folder_path, file_name)
        # file_name = "/Users/pats/OneDrive/My Stuff/VandyHacks/ai-perlapse/images_collection/"+file_name
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)

        response = client.landmark_detection(image=image)
        landmarks = response.landmark_annotations
        CUT_OFF_SCORE = 0.5

        try:
            if landmarks[0].score < CUT_OFF_SCORE:
                print("SCORE LOW:" + file_name)
                os.remove(file_name)
                removed += 1
        except:
            print("NO LANDMARKS:" + file_name)
    return removed

def run_filtering(search_term):
    removed_through_feature = feature_based_filter(search_term=search_term)
    removed_through_rating = landmark_rating_filter(search_term=search_term)
    removed_through_resolution = resolution_based_filter(search_term=search_term)
    print("FILTERED OUT " + str(removed_through_feature) + " IMAGES BASED ON FEATURE DETECTION")
    print("FILTERED OUT " + str(removed_through_rating) + " IMAGES BASED ON RATING DETECTION")
    print("FILTERED OUT " + str(removed_through_resolution) + " IMAGES BASED ON FEATURE DETECTION")

if __name__ == '__main__':
    search_term = input("Name of Monument:")
    number_img = int(input("Number of images for hyperlapse: "))
    search_and_download(search_term=search_term, driver_path=DRIVER_PATH, number_images=number_img * 2)
    input("Press any key to run filtering")
    run_filtering(search_term=search_term)
