# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import requests
# from bs4 import BeautifulSoup
#
#
# def printPropertyCards(propertyCards):
#     for index, card in enumerate(propertyCards):
#         name = card.find('div', {'data-testid': 'title'})
#         address = card.find('span', {'data-testid': 'address'})
#         distance = card.find('span', {'data-testid': 'distance'})
#         numOfReviews = card.find('div', {'class': 'd8eab2cf7f c90c0a70d3 db63693c62'})
#         extras = card.find('div', class_='d506630cf3')
#         newToBooking = card.find('span', class_='e2f34d59b1')
#         xNightsAndAdults = card.find('div', {'data-testid': 'price-for-x-nights'})
#         price = card.find('span', {'data-testid': 'price-and-discounted-price'})
#         taxesAndCharges = card.find('div', {'data-testid': 'taxes-and-charges'})
#
#         print(f'Hotel {index + 1}:\n\t Name: {name.text.strip()}')
#         print(f'\t Address: {address.text.strip()}')
#         print(f'\t Distance from Center: {distance.text.strip()}')
#         if newToBooking and newToBooking.text == "New to Booking.com": print(f'\t New to Booking.com')
#         print(f'\t Reviews: {numOfReviews.text}') if numOfReviews else print('\t Reviews: No reviews yet')
#         print(f'\t Extras: {extras.text}') if extras else print('\t Extras: No extras')
#         print(f'\t Nights and people: {xNightsAndAdults.text.strip()}') if xNightsAndAdults else print(
#             '\t Nights and people: No info')
#         print(f'\t Price: {price.text.strip()}') if price else print('\t Price: No price')
#         print(f'\t Taxes and charges: {taxesAndCharges.text.strip()}') if taxesAndCharges else print(
#             '\t Taxes and charges: No info')
#         print("----------------------------------------------")
#
#
# if __name__ == '__main__':
#     url = 'https://www.booking.com/searchresults.html?ss=Berlin&ssne=Berlin&ssne_untouched=Berlin&efdco=1&label=gen173nr-1BCAEoggI46AdIM1gEaGqIAQGYAQ64ARfIAQzYAQHoAQGIAgGoAgO4AoD2taIGwAIB0gIkYjUwNGU2YzctYmIxNS00NDEyLWIwZDMtMjYxN2Y4MDg4YmQ32AIF4AIB&sid=77a53ffe11c95ad4fb890587265110d0&aid=304142&lang=en-us&sb=1&src_elem=sb&src=searchresults&dest_id=-1746443&dest_type=city&checkin=2023-05-31&checkout=2023-06-14&group_adults=2&no_rooms=1&group_children=0'
#     url2 = 'https://www.booking.com/searchresults.html?ss=Berlin&ssne=Berlin&ssne_untouched=Berlin&efdco=1&label=gen173nr-1BCAEoggI46AdIM1gEaGqIAQGYAQ64ARfIAQzYAQHoAQGIAgGoAgO4AoD2taIGwAIB0gIkYjUwNGU2YzctYmIxNS00NDEyLWIwZDMtMjYxN2Y4MDg4YmQ32AIF4AIB&sid=77a53ffe11c95ad4fb890587265110d0&aid=304142&lang=en-us&sb=1&src_elem=sb&src=searchresults&dest_id=-1746443&dest_type=city&checkin=2023-05-31&checkout=2023-06-14&group_adults=2&no_rooms=1&group_children=0'
#     # set up selenium driver
#     driver = webdriver.Chrome()
#     driver.get(url)
#
#     # set implicit wait time to 10 seconds
#     driver.implicitly_wait(10)
#
#     # wait until the element with ID "my_element" is present
#     element_present = EC.presence_of_element_located(
#         (By.CLASS_NAME, "a826ba81c4"))  # the first class of the property card
#     WebDriverWait(driver, timeout=10).until(element_present)
#
#     # now that the element is present, get the page source
#     html_source = driver.page_source
#
#     # close the browser
#     driver.quit()
#
#     # use BeautifulSoup to parse the page source and extract the data you need
#     soup = BeautifulSoup(html_source, "html.parser")
#
#     source = requests.get(url)
#     property_cards = soup.find_all('div', {'data-testid': 'property-card'})
#
#     printPropertyCards(property_cards)


from datetime import datetime, timedelta

from datetime import datetime, timedelta


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


date_str = "2023-11-29"
result = generate_date_tuples(date_str)
print(result)
