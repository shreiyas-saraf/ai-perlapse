from selenium import webdriver
import sys
import os
sys.path.append(os.getcwd())
print(sys.path)
from selenium.webdriver.common.keys import Keys
import time
# Opens up web driver and goes to Google Images
driver = webdriver.Chrome()
driver.get('https://www.google.ca/imghp?hl=en&tab=ri&authuser=0&ogbl')




