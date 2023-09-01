import threading
import time
import os
import sys
from selenium import webdriver
from selenium.common import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import logging

citiesList = ['Tokyo', 'Berlin', 'New York', 'Madrid', 'Milano', 'Tel Aviv', 'Rome', 'Amsterdam', 'Barcelona',
              'Las Vegas',
              'Miami', 'San Francisco', 'Hanoi']
propertyCardData = [
    ('div', {'data-testid': 'title'}),
    ('span', {'data-testid': 'address'}),
    ('span', {'data-testid': 'distance'}),
    ('div', {'data-testid': 'review-score'}),
    # ('div', {'data-testid': 'availability-rate-information'}),
    ('div', {'data-testid': 'price-for-x-nights'}),  # nights and adults: x nights y adults
    ('div', {'data-testid': 'price-and-discounted-price'}),  # price
    ('div', {'data-testid': 'taxes-and-charges'}),  # taxes-and-charges
    ('div', {'class': 'e4755bbd60'}),  # stars: x out of 5
    # ('div', {'data-testid': 'recommended-units'}),
    ('span', {'class': 'e2f34d59b1'}),  # promotional stuff (newToBooking, getawayDeal, promoted, sustainability etc...)
    ('a', {'data-testid': 'secondary-review-score-link'}),  # location: rank
    ('div', {'data-testid': 'rating-circles'}),  # circles: aria-label x out of 5
    ('span', {'data-testid': 'preferred-badge'}),  # preferred badge - the 'thumb' badge
    ('div', {'data-testid': 'notices-container'})  # notice container on the page
]


def getPropertyCardDetails(card):
    name = card.find(propertyCardData[0][0], propertyCardData[0][1])  # title
    address = card.find(propertyCardData[1][0], propertyCardData[1][1])  # address
    distance = card.find(propertyCardData[2][0], propertyCardData[2][1])  # distance
    locationRank = card.find(propertyCardData[9][0], propertyCardData[9][1])
    numOfReviews = card.find(propertyCardData[3][0], propertyCardData[3][1])  # review-score
    xNightsAndAdults = card.find(propertyCardData[4][0], propertyCardData[4][1])  # price-for-x-nights
    extras = card.find(propertyCardData[5][0], propertyCardData[5][1])  #
    stars = card.find(propertyCardData[7][0], propertyCardData[7][1])  # class: e4755bbd60
    # price = card.find('span', {'data-testid': 'price-and-discounted-price'})
    # taxesAndCharges = card.find('div', {'data-testid': 'taxes-and-charges'})
    promotionalStuff = card.findAll(propertyCardData[8][0], propertyCardData[8][1])
    circles = card.find(propertyCardData[10][0], propertyCardData[10][1])
    preferredBadge = card.find(propertyCardData[11][0], propertyCardData[11][1])

    result = ''
    result += f'Name: {name.text.strip()}\n'
    result += f'Address: {address.text.strip()}\n'
    result += f'Distance from Center: {distance.text.strip()}\n'
    for i in range(0, len(promotionalStuff)):
        result += f'Promotional Stuff: {promotionalStuff[i].text}\n' if promotionalStuff[i] else ''
    if numOfReviews:
        numOfReviewsSplittedText = re.sub(r'(\d+(\.\d+)?)([A-Za-z]+)', r'\1 \3', numOfReviews.text)
    result += f'Reviews: {numOfReviewsSplittedText}\n' if numOfReviews else 'Reviews: No reviews yet\n'
    result += f'{locationRank.attrs["aria-label"]}\n' if locationRank else ""
    result += f'Extras: {extras.text}\n' if extras else ''
    result += f'Nights and people: {xNightsAndAdults.text.strip()}\n' if xNightsAndAdults else ''
    result += f'Stars: {stars.attrs["aria-label"]}\n' if stars else 'Stars: Unranked\n'
    result += f'Circles: {len(circles.contents)} out of 5\n' if circles else 'Circles: Unranked\n'
    result += f'Preffered Badge (thumb): True' if preferredBadge else f'Preffered Badge (thumb): False'

    # Circles?
    # result += f'Price: {price.text.strip()}\n' if price else '\t Price: No price\n'
    # result += f'Taxes and charges: {taxesAndCharges.text.strip()}\n' if taxesAndCharges else '\t Taxes and charges: No info\n'

    return result


def searchDate(checkInDate, checkOutDate, cityToSearch):
    searchbox_present = EC.presence_of_element_located(
        (By.CLASS_NAME, "d47738b911"))  # the first search box
    WebDriverWait(driver, timeout=10).until(searchbox_present)

    check_in_button = driver.find_element(By.XPATH, "//*[@data-testid='date-display-field-start']")
    check_out_button = driver.find_element(By.XPATH, "//*[@data-testid='date-display-field-end']")

    # get the city selection input element -> clear its value and write our city
    input_element = driver.find_element(By.XPATH, "//input[@name='ss']")
    input_element.send_keys(Keys.CONTROL + "a")  # Select all text
    input_element.send_keys(Keys.BACKSPACE)
    input_element.send_keys(cityToSearch)
    ul_element = driver.find_element(By.XPATH,
                                     '//ul[@data-testid="autocomplete-results-options"]')  # the autocomplete list of cities
    time.sleep(1.5)
    li_element = ul_element.find_element(By.TAG_NAME, "li")
    li_element.click()
    input_element.click()

    check_in_button.click()

    # Reset the searchbox all the way to the left (fix for the bug where we couldn't find the correct dates after
    # completing a city and searching for a new city.
    try:
        while True:
            prev_month_button = driver.find_element(By.XPATH, "//*[@type='button']"
                                                    and "//*[@class='a83ed08757 c21c56c305 f38b6daa18 d691166b09 f671049264 deab83296e f4552b6561 dc72a8413c c9804790f7']")
            prev_month_button.click()
    except NoSuchElementException:
        pass

    # keep advance the dates until we find the desire month.
    while True:
        try:
            check_in_date = driver.find_element(By.XPATH, f"//*[@data-date='{checkInDate}']")
            check_in_date.click()
            break
        except NoSuchElementException:
            next_month_button = driver.find_element(By.XPATH, "//*[@type='button']"
                                                    and "//*[@class='a83ed08757 c21c56c305 f38b6daa18 d691166b09 f671049264 deab83296e f4552b6561 dc72a8413c f073249358']")
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
                                            and "//*[@class='a83ed08757 c21c56c305 a4c1805887 f671049264 d2529514af c082d89982 aa11d0d5cd']")

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
# def save_data_from_search_results(date, city):
#     today = datetime.today()
#     date_string = today.strftime("%d-%m-%Y")
#     fDate = (datetime.strptime(date[0], '%Y-%m-%d').strftime('%d-%m-%Y'),
#              datetime.strptime(date[1], '%Y-%m-%d').strftime('%d-%m-%Y'))
#
#     current_directory = os.path.dirname(os.path.abspath(__file__))
#     data_directory = os.path.join(current_directory, f'../Data/{date_string}')
#     city_folder_path = os.path.join(data_directory, city)
#     os.makedirs(city_folder_path, exist_ok=True)
#     folder_name = f"{fDate[0]}---{fDate[1]}"
#     folder_path = os.path.join(city_folder_path, folder_name)
#     os.makedirs(folder_path, exist_ok=True)
#
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     property_cards = soup.find_all('div', {'data-testid': 'property-card'})
#     noticesContainer = soup.find(propertyCardData[12][0], propertyCardData[12][1])
#     notices_file = 'Notices.txt'
#     file_path = os.path.join(folder_path, notices_file)
#     if noticesContainer:
#         with open(file_path, 'a', encoding='utf-8') as file:
#             for notice in noticesContainer.contents:
#                 file.write(f'• {notice.text}\n')
#
#     links = []
#     for index, card in enumerate(property_cards):
#         links.append(card.find('a', {'data-testid': 'title-link'})['href'])
#         tags_file = f'index_{index + 1}_property_card.txt'
#         file_path = os.path.join(folder_path, tags_file)
#         with open(file_path, 'w', encoding='utf-8') as file:
#             file.write(getPropertyCardDetails(card))
#
#     i = 1
#     for link in links:
#         driver.get(link)
#         time.sleep(1)
#         html_hotel_source = driver.page_source
#         file_name = f'index_{i}.html'
#         file_path = os.path.join(folder_path, file_name)
#         with open(file_path, 'w', encoding='utf-8') as file:
#             file.write(html_hotel_source)
#         i += 1


def save_property_cards_for_x_pages(date, city):
    today = datetime.today()
    date_string = today.strftime("%d-%m-%Y")
    fDate = (datetime.strptime(date[0], '%Y-%m-%d').strftime('%d-%m-%Y'),
             datetime.strptime(date[1], '%Y-%m-%d').strftime('%d-%m-%Y'))

    current_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
    data_directory = os.path.join(current_directory, f'../Data/{date_string}---{getStartHour()}')
    city_folder_path = os.path.join(data_directory, city)
    os.makedirs(city_folder_path, exist_ok=True)  # Create City folder
    folder_name = f"{fDate[0]}---{fDate[1]}"
    folder_path = os.path.join(city_folder_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)  # Create search dates folder
    # Make file for notices container
    soup = BeautifulSoup(driver.page_source, "html.parser")
    notices_container = soup.find(propertyCardData[12][0], propertyCardData[12][1])
    notices_file = 'Notices.txt'
    file_path = os.path.join(folder_path, notices_file)
    if notices_container:
        with open(file_path, 'a', encoding='utf-8') as file:
            for notice in notices_container.contents:
                file.write(f'• {notice.text}\n')

    # List of urls for pages 1-10
    pages_urls = []
    search_url = driver.current_url
    for i in range(10):
        pages_urls.append(search_url + "&offset=" + str(i * 25))

    # Inner function for each thread to create the property cards of their specific page
    def event(page_url, page_number):
        browser = webdriver.Chrome()
        browser.get(page_url)
        property_cards = soup.find_all('div', {'data-testid': 'property-card'})
        for index, card in enumerate(property_cards):
            tags_file = f'index_{(index + 1) + (page_number * 25)}_property_card.txt'
            file_path = os.path.join(folder_path, tags_file)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(getPropertyCardDetails(card))
        browser.quit()

    threads = []
    for i in range(10):
        thread = threading.Thread(target=event, args=(pages_urls[i], i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


# Main scrape loop for the relevant dates starting from today.
# While loop is used to search the current dates incase the popup interfered while trying to search.
def scrape():
    initDate = datetime.today() + timedelta(days=1)  # we start to search from tomorrow bcz GMT problems
    date_string = initDate.strftime("%Y-%m-%d")
    dates = generate_date_tuples(date_string)
    for city in citiesList:
        for date in dates:
            # Go back to the original page we started searching from, removes the need of handling multiple cases for random stuff that happens...
            driver.get(url)
            pop_up = True
            while pop_up:
                # New outer try catch incase other exceptions happen -> just refresh the page.
                try:
                    try:
                        searchDate(date[0], date[1], city)
                        # save_data_from_search_results(date, city)
                        save_property_cards_for_x_pages(date, city)
                        pop_up = False
                    except ElementClickInterceptedException as e:
                        button_xpath = '//button[@aria-label="Dismiss sign-in info."]'
                        button = driver.find_element(By.XPATH, button_xpath)
                        button.click()

                except Exception as e:
                    logging.error(e)
                    driver.get(url)


# This function returns one of "04:00, 12:00, 20:00". Used with the creation of "data/{date}-{start_hour}"
# for saving the data from 3 different searches on the same day
def getStartHour():
    now = datetime.now()
    current_hour = now.hour
    run_start_times = [4, 12, 20]

    if run_start_times[0] <= current_hour < run_start_times[1]:
        return f"{run_start_times[0]:02d}-00"

    if run_start_times[1] <= current_hour < run_start_times[2]:
        return f"{run_start_times[1]:02d}-00"

    if run_start_times[2] <= current_hour or current_hour < run_start_times[0]:
        return f"{run_start_times[2]:02d}-00"




# Default URL - where we start scraping
url = 'https://www.booking.com/'

# set up selenium driver
driver = webdriver.Chrome()
driver.get(url)

# set implicit wait time to 2 seconds
driver.implicitly_wait(2)

# Configure the logging system to write to a file
logging.basicConfig(filename='error_log.txt', level=logging.ERROR)

scrape()
