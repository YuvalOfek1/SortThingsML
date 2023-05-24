import time
import random as ran
import sys

import codecs
import requests
import re
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup


def searchDate(checkInDate, checkOutDate):
    searchbox_present = EC.presence_of_element_located(
        (By.CLASS_NAME, "d47738b911"))  # the first search box
    WebDriverWait(driver, timeout=10).until(searchbox_present)

    check_in_button = driver.find_element(By.XPATH, "//*[@data-testid='date-display-field-start']")
    check_in_button.click()
    while True:
        try:
            check_in_date = driver.find_element(By.XPATH, f"//*[@data-date='{checkInDate}']")
            check_in_date.click()
            break
        except NoSuchElementException:
            next_month_button = driver.find_element(By.XPATH, "//*[@type='button']"
                                                    and "//*[@class='fc63351294 a822bdf511 e3c025e003 fa565176a8 cfb238afa1 c334e6f658 ae1678b153 c9fa5fc96d be298b15fa']")
            next_month_button.click()

    check_out_button = driver.find_element(By.XPATH, "//*[@data-testid='date-display-field-end']")
    check_out_button.click()
    while True:
        try:
            check_out_date = driver.find_element(By.XPATH, f"//*[@data-date='{checkOutDate}']")
            check_out_date.click()
            break
        except NoSuchElementException:
            next_month_button = driver.find_element(By.XPATH, "//*[@type='button']"
                                                    and "//*[@class='fc63351294 a822bdf511 e3c025e003 fa565176a8 cfb238afa1 c334e6f658 ae1678b153 c9fa5fc96d be298b15fa']")
            next_month_button.click()

    search_button = driver.find_element(By.XPATH, "//*[@type='submit']"
                                        and "//*[@class='fc63351294 a822bdf511 d4b6b7a9e7 f7db01295e c938084447 f4605622ad c827b27356']")
    search_button.click()


url = 'https://www.booking.com/searchresults.html?ss=Berlin&ssne=Berlin&ssne_untouched=Berlin&efdco=1&label=gen173nr-1BCAEoggI46AdIM1gEaGqIAQGYAQ64ARfIAQzYAQHoAQGIAgGoAgO4AoD2taIGwAIB0gIkYjUwNGU2YzctYmIxNS00NDEyLWIwZDMtMjYxN2Y4MDg4YmQ32AIF4AIB&sid=77a53ffe11c95ad4fb890587265110d0&aid=304142&lang=en-us&sb=1&src_elem=sb&src=searchresults&dest_id=-1746443&dest_type=city&checkin=2023-05-31&checkout=2023-06-14&group_adults=2&no_rooms=1&group_children=0'

# set up selenium driver
driver = webdriver.Chrome()
driver.get(url)

# set implicit wait time to 2 seconds
driver.implicitly_wait(2)

# wait until the element with ID "my_element" is present
element_present = EC.presence_of_element_located(
    (By.CLASS_NAME, "a826ba81c4"))  # the first class of the property card
WebDriverWait(driver, timeout=10).until(element_present)

# now that the element is present, get the page source
html_source = driver.page_source

# use BeautifulSoup to parse the (MAIN PAGE) page source and extract the data you need
soup = BeautifulSoup(html_source, "html.parser")


# searchDate("2023-07-22", "2023-10-15")

# time.sleep(10)
file_path = 'C:\\Users\\Yuval\\Desktop\\אקדמיה\\B.sc CS COLMAN\\תכנית מצטיינים\\HotelsHTMLSource'  # Replace with your desired file path


property_cards = soup.find_all('div', {'data-testid': 'property-card'})
links = []
for card in property_cards:
    links.append(card.find('a', {'data-testid': 'title-link'})['href'])

i=1
for link in links:
    driver.get(link)
    time.sleep(3)
    html_hotel_source = driver.page_source
    print(i)
    with open(file_path+f'/Berlin_index_{i}_1-2-22_2-2-22.html', 'w', encoding='utf-8') as file:
        file.write(html_hotel_source)
    i=i+1

