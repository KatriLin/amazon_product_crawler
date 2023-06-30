from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import requests
import time
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--user-agent=Chrome/110.0.0.0')
setExperimentalOption = options.add_experimental_option
setExperimentalOption('excludeSwitches', ['enable-automation'])
options.add_argument('--disable-blink-features=AutomationControlled')


load_dotenv()
driver_path = os.getenv('CHROMEDRIVER_PATH')

time.sleep(2)


class AmazonProductDetailsCrawler():

    def __init__(self, productName: str, descriptionMustContain=None, descriptionMustNotContain=None):
        self.url = 'https://www.amazon.it/'
        self.driver = webdriver.Chrome(executable_path=driver_path, options=options)
        self.products = []
        self.productName = productName
        self.descriptionMustContain = descriptionMustContain
        self.descriptionMustNotContain = descriptionMustNotContain

    def run(self):
        self.driver.get(self.url)
        time.sleep(2)
        self.write_name_to_the_search_field()
        self.collect_product_details()

    def write_name_to_the_search_field(self):
        try:
            time.sleep(1)
            find_search_field = self.driver.find_element(By.ID, 'twotabsearchtextbox')
            time.sleep(4)
            find_search_field.send_keys(self.productName)
            time.sleep(4)
            self.driver.find_element(By.ID, 'nav-search-submit-button').click()
            time.sleep(2)
        except NoSuchElementException as e:
            print("Search field not found: ", e)

    def collect_product_details(self):

        page = 1
        PAGE_LIMIT = 4
        while page <= PAGE_LIMIT:
            product_elements = self.driver.find_elements(By.XPATH, './/div[contains(@class, "sg-col-4-of-12 s-result-item s-asin")]')
            if product_elements:
                for i, product in enumerate(product_elements, start=1):
                    try:
                        description = product.find_element(By.CLASS_NAME, 'a-size-mini').text
                    except Exception as e:
                        pass

                    try:
                        if self.descriptionMustContain is not None and self.descriptionMustContain not in description.lower():
                            # If the product description does not contain word given such as "apple" Skip to the next product
                            continue
                        if self.descriptionMustNotContain is not None and self.descriptionMustNotContain in description.lower():
                            # If product description contais unwanted word givensuch as "Ricondizionato"(reconditioned) skip to the next product
                            continue
                    except Exception as e:
                        pass
                    try:
                        price = product.find_element(By.CLASS_NAME, 'a-price-whole').text
                    except Exception as e:
                        # If no price information is available skip to the next product
                        continue
                    try:
                        currency = product.find_element(By.CLASS_NAME, 'a-price-symbol').text

                        price_with_currency = f"{price} {currency}"
                    except Exception as e:
                        print("Error: ", e)
                    try:
                        url = product.find_element(
                            By.XPATH, './/h2[contains(@class, "a-size-mini a-spacing-none a-color-base s-line-clamp-4")]/a').get_attribute('href')
                    except Exception as e:
                        url = None
                    try:
                        image = product.find_element(By.CLASS_NAME, 's-image').get_attribute('src')
                    except Exception as e:
                        image = None
                    product = {
                        'description': description,
                        'price': price_with_currency,
                        'url': url,
                        'image': image
                    }

                    self.products.append(product)
                self.go_to_next_page()
                page += 1

            else:
                print('No items are available')
                return
       
        self.driver.quit()

    def go_to_next_page(self):

        try:
            next_page = self.driver.find_element_by_xpath("//a[contains(text(), 'Avanti')]")
            next_page.click()
            time.sleep(4)
        except Exception as e:
            pass


if __name__ == '__main__':
    crawler = AmazonProductDetailsCrawler("iphone 12 pro max", descriptionMustContain="apple")
    # crawler1 = AmazonProductDetailsCrawler("iphone 11", descriptionMustContain="apple",descriptionMustNotContain="ricondizionato")
    # crawler2 = AmazonProductDetailsCrawler("ipad air 5 generazione", descriptionMustContain="apple",descriptionMustNotContain="ricondizionato")
    #crawler3 = AmazonProductDetailsCrawler("guffie bose")
    crawler.run()