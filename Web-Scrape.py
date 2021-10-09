from urllib.request import urlopen as uReq
import requests
from bs4 import BeautifulSoup
import os

def main_function():
    download_image()

def user_place_input():
    desired_place = input('Enter the location/monument: ')
    return desired_place

def url_builder():
    search_url_sec1 = 'https://www.google.com/search?q='
    search_url_sec2 = '&tbm=isch&ved=2ahUKEwik6vm7qLzzAhXK0FMKHd1yAosQ2-cCegQIABAA&oq='
    search_url_sec3 = '&gs_lcp=CgNpbWcQA1AAWABg6ARoAHAAeACAAQCIAQCSAQCYAQCqAQtnd3Mtd2l6LWltZw&sclient=img&ei=9wJhYeSSBMqhzwLd5YnYCA&bih=722&biw=1440&hl=EN'
    string_index = ''
    desired_place = user_place_input()
    for image in desired_place:
        if image == ' ':
            string_index+= '+'
        else:
            string_index+= image
    search_url = search_url_sec1 + string_index + search_url_sec2 + string_index + search_url_sec3
    return search_url

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
