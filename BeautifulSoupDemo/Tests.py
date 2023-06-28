import time
import os
from selenium import webdriver
from selenium.common import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

citiesList = ['Berlin', 'New York', 'Madrid', 'Milano', 'Tel Aviv', 'Rome', 'Amsterdam', 'Barcelona', 'Las Vegas',
              'Miami', 'San Francisco']
propertyCardData = [
    ('div', {'data-testid': 'title'}),
    ('span', {'data-testid': 'address'}),
    ('span', {'data-testid': 'distance'}),
    ('div', {'data-testid': 'review-score'}),
    # ('div', {'data-testid': 'availability-rate-information'}),
    ('div', {'data-testid': 'price-for-x-nights'}),  #nights and adults: x nights y adults
    ('div', {'data-testid': 'price-and-discounted-price'}),  # price
    ('div', {'data-testid': 'taxes-and-charges'}),  # taxes-and-charges
    ('div', {'class': 'e4755bbd60'}),  #stars: x out of 5
    # ('div', {'data-testid': 'recommended-units'}),
    # ('span', {'class': 'e2f34d59b1'}),  ## maybe class_= (newToBooking)
]


def getPropertyCardDetails(card):
    name = card.find(propertyCardData[0][0], propertyCardData[0][1])
    address = card.find(propertyCardData[1][0], propertyCardData[1][1])
    distance = card.find(propertyCardData[2][0], propertyCardData[2][1])
    numOfReviews = card.find(propertyCardData[3][0], propertyCardData[3][1])
    xNightsAndAdults = card.find(propertyCardData[4][0], propertyCardData[4][1])
    extras = card.find(propertyCardData[5][0], propertyCardData[5][1])
    newToBooking = card.find(propertyCardData[6][0], propertyCardData[6][1])
    stars = card.find(propertyCardData[7][0], propertyCardData[7][1])
    # price = card.find('span', {'data-testid': 'price-and-discounted-price'})
    # taxesAndCharges = card.find('div', {'data-testid': 'taxes-and-charges'})

    result = ''
    result += f'Name: {name.text.strip()}\n'
    result += f'Address: {address.text.strip()}\n'
    result += f'Distance from Center: {distance.text.strip()}\n'
    if newToBooking and newToBooking.text == "New to Booking.com":
        result += 'New to Booking.com\n'
    result += f'Reviews: {numOfReviews.text}\n' if numOfReviews else 'Reviews: No reviews yet\n'
    result += f'Extras: {extras.text}\n' if extras else 'Extras: No extras\n'
    result += f'Nights and people: {xNightsAndAdults.text.strip()}\n' if xNightsAndAdults else 'Nights and people: No info\n'
    result += f'Stars: {stars.attrs["aria-label"]}\n' if stars else 'Stars: unranked\n'

    # Circles?
    # result += f'Price: {price.text.strip()}\n' if price else '\t Price: No price\n'
    # result += f'Taxes and charges: {taxesAndCharges.text.strip()}\n' if taxesAndCharges else '\t Taxes and charges: No info\n'
    result += "----------------------------------------------\n"

    return result


def searchDate(checkInDate, checkOutDate, cityToSearch):
    searchbox_present = EC.presence_of_element_located(
        (By.CLASS_NAME, "d47738b911"))  # the first search box
    WebDriverWait(driver, timeout=10).until(searchbox_present)

    check_in_button = driver.find_element(By.XPATH, "//*[@data-testid='date-display-field-start']")
    check_out_button = driver.find_element(By.XPATH, "//*[@data-testid='date-display-field-end']")

    # get the city selection input element -> clear its value and write our city
    input_element = driver.find_element(By.XPATH, "//input[@id=':Ra9:']")
    input_element.send_keys(Keys.CONTROL + "a")  # Select all text
    input_element.send_keys(Keys.BACKSPACE)
    input_element.send_keys(cityToSearch)
    ul_element = driver.find_element(By.XPATH,
                                     '//ul[@data-testid="autocomplete-results"]')  # the autocomplete list of cities
    time.sleep(1.5)
    li_element = ul_element.find_element(By.TAG_NAME, "li")
    li_element.click()
    input_element.click()
    print('succeeded to click on city')

    check_in_button.click()

    # keep advance the dates untill we fint the desire month.
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
def save_data_from_search_results(date, city):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(current_directory, '../Data')
    city_folder_path = os.path.join(data_directory, city)
    os.makedirs(city_folder_path, exist_ok=True)
    folder_name = f"{date[0]}---{date[1]}"
    folder_path = os.path.join(city_folder_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    property_cards = soup.find_all('div', {'data-testid': 'property-card'})
    links = []
    for index, card in enumerate(property_cards):
        links.append(card.find('a', {'data-testid': 'title-link'})['href'])
        tags_file = f'index_{index + 1}_property_card.txt'
        file_path = os.path.join(folder_path, tags_file)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(getPropertyCardDetails(card))

    i = 1
    for link in links[:1]:
        driver.get(link)
        time.sleep(1)
        html_hotel_source = driver.page_source
        file_name = f'index_{i}.html'
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
    for city in citiesList:
        for date in dates[:1]:
            # Go back to the original page we started searching from, removes the need of handling multiple cases for random stuff that happens...
            driver.get(url)
            pop_up = True
            while pop_up:
                try:
                    searchDate(date[0], date[1], city)
                    save_data_from_search_results(date, city)
                    pop_up = False
                except ElementClickInterceptedException:
                    button_xpath = '//button[@aria-label="Dismiss sign-in info."]'
                    button = driver.find_element(By.XPATH, button_xpath)
                    button.click()
                    print('pop up but continued')


# Default URL - where we start scraping
url = 'https://www.booking.com/'

# set up selenium driver
driver = webdriver.Chrome()
driver.get(url)

# set implicit wait time to 2 seconds
driver.implicitly_wait(2)

scrape()
