from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

def main_function():
    url_builder()

def user_place_input():
    desired_place = input('Enter the location/monument: ')
    return desired_place

def url_builder():
    search_url_sec1 = 'https://www.google.com/search?q='
    search_url_sec2 = '&tbm=isch&ved=2ahUKEwik6vm7qLzzAhXK0FMKHd1yAosQ2-cCegQIABAA&oq='
    search_url_sec3 = '&gs_lcp=CgNpbWcQA1AAWABg6ARoAHAAeACAAQCIAQCSAQCYAQCqAQtnd3Mtd2l6LWltZw&sclient=img&ei=9wJhYeSSBMqhzwLd5YnYCA&bih=722&biw=1440&hl=EN'
    string_index = ''
    desired_place = user_place_input()
    for i in desired_place:
        if i == ' ':
            string_index+= '+'
        else:
            string_index+= i
    search_url = search_url_sec1 + string_index + search_url_sec2 + string_index + search_url_sec3
    print(search_url)
    return search_url

#def web_scrape():


main_function()
