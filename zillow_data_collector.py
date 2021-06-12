from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time

LISTINGS = YOUR_ZILLOW_LISTINGS_LINK
chrome_driver_path = YOUR_CHROME_DRIVER_PATH
form_link = YOUR_GOOLGE_FORMS_LINK


class RetrieveListings:

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=chrome_driver_path)
        self.driver.get(LISTINGS)
        self.listings = []
        self.prices = []
        self.links = []
        self.addresses = []

    def get_listings(self):
        time.sleep(5)
        scroller = self.driver.find_element_by_xpath("//*[@id='search-page-list-container']")
        scroll = 0
        while scroll < 13:  # this will scroll 13 times (to the bottom of the page)
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;',
                                       scroller)
            scroll += 1
            # Waits 1s between each scroll
            time.sleep(1)
        time.sleep(2)
        self.listings = self.driver.find_elements_by_css_selector("ul li article[role='presentation']")
        for listing in self.listings:
            # Only gets the price in the form $0,000, change if price is more or less than 4 digits long
            price = listing.find_element_by_class_name("list-card-price").text[0:6]
            address = listing.find_element_by_class_name("list-card-addr").text
            # Zillow can put the listing link in 2 different spots, makes sure to grab it every time
            try:
                link = listing.find_element_by_css_selector("div a.list-card-link.list-card-link-top-margin").get_attribute('href')
            except NoSuchElementException:
                link = listing.find_element_by_css_selector("div a.list-card-link").get_attribute('href')
            self.prices.append(price)
            self.addresses.append(address)
            self.links.append(link)

    def compiler(self):
        # Inputs the data from get_listings() into a google form that can then be used to create a google sheet of the data
        self.driver.get(form_link)
        time.sleep(1)

        for (price, link, address) in zip(self.prices, self.links, self.addresses):
            address_box = self.driver.find_element_by_xpath("//*[@id='mG61Hd']/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input")
            price_box = self.driver.find_element_by_xpath("//*[@id='mG61Hd']/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input")
            link_box = self.driver.find_element_by_xpath("//*[@id='mG61Hd']/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input")
            submit_button = self.driver.find_element_by_xpath("//*[@id='mG61Hd']/div[2]/div/div[3]/div[1]/div/div/span")
            address_box.send_keys(address)
            price_box.send_keys(price)

            # For broken links that start with /b/
            if link[0:3] == '/b/':
                link = f"https://www.zillow.com{link}"
            link_box.send_keys(link)
            submit_button.click()
            time.sleep(1)
            # Click on make a new entry
            self.driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div/div[4]/a").click()
            time.sleep(1)


my_listings = RetrieveListings()
my_listings.get_listings()
my_listings.compiler()
