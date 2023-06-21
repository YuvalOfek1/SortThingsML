import time
import os
from selenium import webdriver
from selenium.common import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def searchDate(checkInDate, checkOutDate):
    searchbox_present = EC.presence_of_element_located(
        (By.CLASS_NAME, "d47738b911"))  # the first search box
    WebDriverWait(driver, timeout=10).until(searchbox_present)

    check_in_button = driver.find_element(By.XPATH, "//*[@data-testid='date-display-field-start']")
    check_out_button = driver.find_element(By.XPATH, "//*[@data-testid='date-display-field-end']")
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

    try:
        driver.find_element(By.XPATH, "//*[@data-testid='searchbox-datepicker']")
    except:
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

    try:
        search_button = driver.find_element(By.XPATH, "//*[@type='submit']"
                                            and "//*[@class='fc63351294 a822bdf511 d4b6b7a9e7 cfb238afa1 c938084447 f4605622ad aa11d0d5cd']")

    except NoSuchElementException:
        search_button = driver.find_element(By.XPATH, "//*[@type='submit']"
                                            and "//*[@class='fc63351294 a822bdf511 d4b6b7a9e7 f7db01295e c938084447 f4605622ad c827b27356']")
    search_button.click()

"""
# Given a date of "yyyy-mm-dd" returns a list of tuples:
    Example:
        date_str = '2023-06-14'
        result = generate_date_tuples(date_str)
        print(result)
        # Output: [('2023-06-14', '2023-06-15'), ('2023-06-14', '2023-06-16'), ('2023-06-14', '2023-06-17'), ('2023-06-14', '2023-06-18'),
        #          ('2023-06-21', '2023-06-15'), ('2023-06-21', '2023-06-16'), ('2023-06-21', '2023-06-17'), ('2023-06-21', '2023-06-18'),
        #          ('2023-07-14', '2023-06-15'), ('2023-07-14', '2023-06-16'), ('2023-07-14', '2023-06-17'), ('2023-07-14', '2023-06-18')]

    """
def generate_date_tuples(date_str):
    # Convert date string to datetime object
    date = datetime.strptime(date_str, "%Y-%m-%d")

    # Calculate one week and one month offsets
    one_week_offset = timedelta(weeks=1)
    one_month_offset = timedelta(days=30)

    # Initialize the list of tuples
    date_tuples = []

    # Generate tuples for given date + 1 to 4 days
    for i in range(1, 5):
        next_date = (date + timedelta(days=i)).strftime("%Y-%m-%d")
        date_tuples.append((date_str, next_date))

    # Generate tuples for given date + one week and 1 to 4 days
    for i in range(1, 5):
        next_date = (date + one_week_offset + timedelta(days=i)).strftime("%Y-%m-%d")
        date_tuples.append(((date + one_week_offset).strftime("%Y-%m-%d"), next_date))

    # Generate tuples for given date + one month and 1 to 4 days
    for i in range(1, 5):
        next_date = (date + one_month_offset + timedelta(days=i)).strftime("%Y-%m-%d")
        date_tuples.append(((date + one_month_offset).strftime("%Y-%m-%d"), next_date))

    return date_tuples


# Save the html source from each link to a desired file path
def save_data_from_search_results(date):
    file_path = r"C:\Users\liavb\Desktop\SortThingsML\data" # Replace with your desired file path
    folder_name = f"{date[0]}---{date[1]}"
    folder_path = os.path.join(file_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    property_cards = soup.find_all('div', {'data-testid': 'property-card'})
    links = []
    for card in property_cards:
        links.append(card.find('a', {'data-testid': 'title-link'})['href'])

    i = 1
    for link in links[:2]:
        driver.get(link)
        time.sleep(1)
        html_hotel_source = driver.page_source
        file_name = f'Berlin_index_{i}_{date[0]}_{date[1]}.html'
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html_hotel_source)
        i += 1


# Main scrape loop for the relevant dates starting from today.
# While loop is used to search the current dates incase the popup interfered while trying to search.
def scrape():
    today = datetime.today()
    date_string = today.strftime("%Y-%m-%d")
    dates = generate_date_tuples(date_string)

    for date in dates:
        # Go back to the original page we started searching from, removes the need of handling multiple cases for random stuff that happens...
        driver.get(url)
        pop_up = True
        while pop_up:
            try:
                searchDate(date[0], date[1])
                save_data_from_search_results(date)
                pop_up = False
            except ElementClickInterceptedException:
                button_xpath = '//button[@aria-label="Dismiss sign-in info."]'
                button = driver.find_element(By.XPATH, button_xpath)
                button.click()
                print('pop up but continued')


# Default URL - where we start scraping
url = 'https://www.booking.com/searchresults.html?ss=Berlin%2C+Berlin+Federal+State%2C+Germany&ssne=Dafna&ssne_untouched=Dafna&label=gen173nr-1FCAEoggI46AdIM1gEaGqIAQGYATG4ARfIAQzYAQHoAQH4AQOIAgGoAgO4Av6myqQGwAIB0gIkN2NiZTVhMWEtNjdiNy00ODA4LTllNzEtZTQ2ZTVjN2NhYjYz2AIF4AIB&aid=304142&lang=en-us&sb=1&src_elem=sb&src=index&dest_id=-1746443&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=en&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=92ee2aff31a3024e&ac_meta=GhA5MmVlMmFmZjMxYTMwMjRlIAAoATICZW46BmJlcmxpbkAASgBQAA%3D%3D&checkin=2023-06-30&checkout=2023-07-27&group_adults=2&no_rooms=1&group_children=0&sb_travel_purpose=leisure'

# set up selenium driver
driver = webdriver.Chrome()
driver.get(url)

# set implicit wait time to 2 seconds
driver.implicitly_wait(2)

scrape()
