from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup


def printPropertyCards(propertyCards):
    for index, card in enumerate(propertyCards):
        name = card.find('div', {'data-testid': 'title'})
        address = card.find('span', {'data-testid': 'address'})
        distance = card.find('span', {'data-testid': 'distance'})
        numOfReviews = card.find('div', {'class': 'd8eab2cf7f c90c0a70d3 db63693c62'})
        extras = card.find('div', class_='d506630cf3')
        newToBooking = card.find('span', class_='e2f34d59b1')
        xNightsAndAdults = card.find('div', {'data-testid': 'price-for-x-nights'})
        price = card.find('span', {'data-testid': 'price-and-discounted-price'})
        taxesAndCharges = card.find('div', {'data-testid': 'taxes-and-charges'})

        print(f'Hotel {index + 1}:\n\t Name: {name.text.strip()}')
        print(f'\t Address: {address.text.strip()}')
        print(f'\t Distance from Center: {distance.text.strip()}')
        if newToBooking and newToBooking.text == "New to Booking.com": print(f'\t New to Booking.com')
        print(f'\t Reviews: {numOfReviews.text}') if numOfReviews else print('\t Reviews: No reviews yet')
        print(f'\t Extras: {extras.text}') if extras else print('\t Extras: No extras')
        print(f'\t Nights and people: {xNightsAndAdults.text.strip()}') if xNightsAndAdults else print(
            '\t Nights and people: No info')
        print(f'\t Price: {price.text.strip()}') if price else print('\t Price: No price')
        print(f'\t Taxes and charges: {taxesAndCharges.text.strip()}') if taxesAndCharges else print(
            '\t Taxes and charges: No info')
        print("----------------------------------------------")


if __name__ == '__main__':
    url = 'https://www.booking.com/searchresults.html?ss=Berlin&ssne=Berlin&ssne_untouched=Berlin&label=gen173nr-1BCAEoggI46AdIM1gEaGqIAQGYAQ64ARfIAQzYAQHoAQGIAgGoAgO4AoD2taIGwAIB0gIkYjUwNGU2YzctYmIxNS00NDEyLWIwZDMtMjYxN2Y4MDg4YmQ32AIF4AIB&sid=77a53ffe11c95ad4fb890587265110d0&aid=304142&lang=en-us&sb=1&src_elem=sb&src=index&dest_id=-1746443&dest_type=city&checkin=2023-05-08&checkout=2023-05-11&group_adults=2&no_rooms=1&group_children=0&sb_travel_purpose=leisure'
    url2 = 'https://www.booking.com/searchresults.en-gb.html?ss=Naples%2C+Campania%2C+Italy&efdco=1&label=gen173nr-1BCAEoggI46AdIM1gEaGqIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4AuuzwKIGwAIB0gIkNTE1ZWQ3YWEtNTA1MS00N2M3LTg2YjItODc5YTM0YjFmMzA32AIF4AIB&sid=d45dec0944d969c573da02f0f248813e&aid=304142&lang=en-gb&sb=1&src_elem=sb&src=index&dest_id=-122902&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=en&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=84f58c76d2ee01c6&ac_meta=GhA4NGY1OGM3NmQyZWUwMWM2IAAoATICZW46A05hcEAASgBQAA%3D%3D&checkin=2023-05-16&checkout=2023-05-20&group_adults=2&no_rooms=1&group_children=0&sb_travel_purpose=leisure&selected_currency=EUR'
    # set up selenium driver
    driver = webdriver.Chrome()
    driver.get(url)

    # set implicit wait time to 10 seconds
    driver.implicitly_wait(10)

    # wait until the element with ID "my_element" is present
    element_present = EC.presence_of_element_located(
        (By.CLASS_NAME, "a826ba81c4"))  # the first class of the property card
    WebDriverWait(driver, timeout=10).until(element_present)

    # now that the element is present, get the page source
    html_source = driver.page_source

    # close the browser
    driver.quit()

    # use BeautifulSoup to parse the page source and extract the data you need
    soup = BeautifulSoup(html_source, "html.parser")

    source = requests.get(url)
    property_cards = soup.find_all('div', {'data-testid': 'property-card'})

    printPropertyCards(property_cards)
