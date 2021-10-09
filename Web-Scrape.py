from urllib.request import urlopen as uReq
import requests
from bs4 import BeautifulSoup
import os
# from google.cloud import vision
import io


def main_function():
    download_image()


def user_place_input():
    desired_place = input('Enter the location/monument: ')
    return desired_place


def url_builder():
    search_url_sec1 = 'https://www.google.com/search?q='
    search_url_sec2 = '&rlz=1C5CHFA_enUS968US968&sxsrf=AOaemvL8Bn72Z5AcrPjtkFwRj6PkDPrZSA:1633761894622&source=lnms&tbm=isch&sa=X&ved=2ahUKEwj-94Cr3bzzAhWYkHIEHWcDAHEQ_AUoAXoECAEQAw&biw=1440&bih=789&dpr=2'

    #desired_place = user_place_input()
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


main_function()
