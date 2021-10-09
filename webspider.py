import hashlib
import time
from PIL import Image
import requests
from selenium import webdriver
import os
import io
from google.cloud import vision

DRIVER_PATH = '/Users/sunidhidhawan/Desktop/ai-perlapse/chromedriver'
wd = webdriver.Chrome(executable_path=DRIVER_PATH)
wd.get('https://google.com')


def persist_image(folder_path: str, url: str):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
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

    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
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


def search_and_download(search_term: str, driver_path: str, target_path='./images', number_images=50):
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with webdriver.Chrome(executable_path=driver_path) as wd:
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=0.5)

    for elem in res:
        persist_image(target_folder, elem)


def detect_landmarks(path, landmark_name):
    """ Detects landmarks in the file. """

    os.environ[
        'GOOGLE_APPLICATION_CREDENTIALS'] = r'/Users/pats/OneDrive/My Stuff/VandyHacks/ai-perlapse/ServiceAccountKey.json'
    client = vision.ImageAnnotatorClient()
    # print(os.getcwd())

    for filename in os.listdir(path):
        # print(filename)
        filename = path + "/" + filename
        # filename = "/Users/pats/OneDrive/My Stuff/VandyHacks/ai-perlapse/images_collection/"+filename
        with io.open(filename, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)

        response = client.landmark_detection(image=image)
        landmarks = response.landmark_annotations
        CUT_OFF_SCORE = 0.5

        try:
            if landmarks[0].score < CUT_OFF_SCORE:
                print("SCORE LOW:" + filename)
                # os.remove(filename)
        except:
            print("NO LANDMARKS:" + filename)


search_term = input("Name of Monument:" )
search_and_download(search_term=search_term, driver_path=DRIVER_PATH)
