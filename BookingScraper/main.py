import time
import os
import sys

from selenium import webdriver
from selenium.common import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import logging
from fake_useragent import UserAgent

citiesList = ['Tokyo', 'Berlin', 'New York', 'Madrid', 'Milano', 'Tel Aviv', 'Rome', 'Amsterdam', 'Barcelona', 'Hanoi']
propertyCardData = [
    ('div', {'data-testid': 'title'}),
    ('span', {'data-testid': 'address'}),
    ('span', {'data-testid': 'distance'}),
    ('span', {'class': 'f419a93f12'}),  # subway access
    ('span', {'class': 'b30f8eb2d6'}),  # promotional stuff (newToBooking, getawayDeal, promoted, sustainability etc...)
    ('div', {'data-testid': 'review-score'}),  # Reviews
    ('a', {'data-testid': 'secondary-review-score-link'}),  # location: rank
    ('div', {'data-testid': 'recommended-units'}),  # Reviews
    ('div', {'data-testid': 'price-for-x-nights'}),  # nights and adults: x nights y adults
    ('span', {'data-testid': 'price-and-discounted-price'}),  # price
    ('div', {'data-testid': 'taxes-and-charges'}),  # taxes-and-charges
    ('div', {'class': 'e4755bbd60'}),  # stars: x out of 5
    ('div', {'data-testid': 'rating-circles'}),  # circles: aria-label x out of 5
    ('span', {'data-testid': 'preferred-badge'}),  # preferred badge - the 'thumb' badge
]


def getPropertyCardDetails(card):
    name =              card.find(propertyCardData[0][0], propertyCardData[0][1])  # title
    address =           card.find(propertyCardData[1][0], propertyCardData[1][1])  # address
    distance =          card.find(propertyCardData[2][0], propertyCardData[2][1])  # distance
    subwayAccess =      card.find(propertyCardData[3][0], propertyCardData[3][1])  # subway access
    promotionalStuff =  card.findAll(propertyCardData[4][0], propertyCardData[4][1])
    numOfReviews =      card.find(propertyCardData[5][0], propertyCardData[5][1])  # review-score
    locationRank =      card.find(propertyCardData[6][0], propertyCardData[6][1])  # secondary-review-score-link

    unit =              card.find(propertyCardData[7][0], propertyCardData[7][1]).find('span', {'class': 'df597226dd'})  # Room details
    bed =               card.find(propertyCardData[7][0], propertyCardData[7][1]).find('div', {'class': 'cb5b4b68a4'})  # Bed details
    roomsLeft =         card.find(propertyCardData[7][0], propertyCardData[7][1]).find('div', {'class': 'cb1f9edcd4'})  # Rooms left details

    xNightsAndAdults =  card.find(propertyCardData[8][0], propertyCardData[8][1])  # price-for-x-nights
    price =             card.find(propertyCardData[9][0], propertyCardData[9][1])  # price-and-discounted-price
    taxesAndCharges =   card.find(propertyCardData[10][0], propertyCardData[10][1])  # taxes-and-charges
    stars =             card.find(propertyCardData[11][0], propertyCardData[11][1])  # class: e4755bbd60
    circles =           card.find(propertyCardData[12][0], propertyCardData[12][1])
    preferredBadge =    card.find(propertyCardData[13][0], propertyCardData[13][1])

    result = ''
    result += f'Name: {name.text.strip()}\n'
    result += f'Address: {address.text.strip()}\n'
    result += f'Distance from Center: {distance.text.strip()}\n'
    result += f'Subway Access: Yes\n' if subwayAccess else f'Subway Access: No\n'
    for i in range(0, len(promotionalStuff)):
        result += f'Promotional Stuff: {promotionalStuff[i].text}\n' if promotionalStuff[i] else ''
    if numOfReviews:
        numOfReviewsSplittedText = re.sub(r'(\d+(\.\d+)?)([A-Za-z]+)', r'\1 \3', numOfReviews.text)
        result += f'Reviews: {numOfReviewsSplittedText}\n'
    else:
        'Reviews: No reviews yet\n'
    result += f'{locationRank.attrs["aria-label"]}\n' if locationRank else 'Location: Unranked\n'
    result += f'Recommended Unit: {unit.text}, {bed.text}, {roomsLeft.text}\n' if roomsLeft else f'Recommended Unit: {unit.text}, {bed.text}\n'
    result += f'Nights and Adults: {xNightsAndAdults.text.strip()}\n' if xNightsAndAdults else f'Nights and Adults: '
    result += f'Price: {price.text.strip()}\n' if price else 'Price: No price\n'
    result += f'Taxes and Charges: {taxesAndCharges.text}\n'
    result += f'Stars: {stars.attrs["aria-label"]}\n' if stars else 'Stars: Unranked\n'
    result += f'Circles: {len(circles.contents)} out of 5\n' if circles else 'Circles: Unranked\n'
    result += f'Preferred Badge (thumb): True\n' if preferredBadge else 'Preferred Badge (thumb): False\n'

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
    notices_container = soup.find('div', {'data-testid': 'notices-container'})
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
    def process_page(page_number):
        driver.switch_to.window(opened_tabs[page_number])
        current_page = BeautifulSoup(driver.page_source, "html.parser")
        property_cards = current_page.find_all('div', {'data-testid': 'property-card'})
        for index, card in enumerate(property_cards):
            tags_file = f'index_{(index + 1) + (page_number * 25)}_property_card.txt'
            file_path = os.path.join(folder_path, tags_file)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(getPropertyCardDetails(card))

    opened_tabs = []

    async def open_tabs():
        for url in pages_urls:
            driver.execute_script(f'window.open("{url}");')
            opened_tabs.append(driver.window_handles[-1])

        time.sleep(1.5)

    asyncio.new_event_loop().run_until_complete(open_tabs())

    # Process the data from the first to the last tab after the loading has completed
    for i in range(10):
        process_page(i)

    curr = driver.current_window_handle
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if handle != curr:
            driver.close()


# Main scrape loop for the relevant dates starting from today.
# While loop is used to search the current dates incase the popup interfered while trying to search.
def scrape():
    initDate = datetime.today() + timedelta(days=1)  # we start to search from tomorrow bcz GMT problems
    date_string = initDate.strftime("%Y-%m-%d")
    dates = generate_date_tuples(date_string)
    for city in citiesList:
        for date in dates:
            # Go back to the original page we started searching from, removes the need of handling multiple cases for random stuff that happens...
            driver.switch_to.window(driver.window_handles[0])
            driver.get(bookingHomePage)
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
                    driver.get(bookingHomePage)


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
bookingHomePage = 'https://www.booking.com/'

# set up selenium driver
options = webdriver.ChromeOptions()

options.add_argument("--headless")
options.add_argument("--incognito")
options.add_argument("--enable-javascript")
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")

options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.141 Safari/537.36')

driver = webdriver.Chrome(options=options)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
  "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
})
# set implicit wait time to 2 seconds
driver.implicitly_wait(2)

# Configure the logging system to write to a file
logging.basicConfig(filename='error_log.txt', level=logging.ERROR)

scrape()

driver.quit()
