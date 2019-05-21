import time
import uuid
import os
import csv
import uuid
from bs4 import BeautifulSoup as bs
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options


search_list = [
    'noise cancelling headphones',
    'true wireless earbuds',
    'over ear headphones',
    'running earphones',
    'running headphones',
    'in ear headphones',
    'workout headphones',
    'truly wireless earbuds',
    'cordless headphones',
    'sport headphones',
    'waterproof headphones',
    'wireless earbuds with charging case',
    'noise canceling headphones',
    'cordless earbuds',
    'wireless noise cancelling headphones',
    'sports headphones',
    'waterproof earbuds',
    'waterproof bluetooth headphones',
    'active noise cancelling headphones',
    'noise cancelling bluetooth headphones',
    'bluetooth noise cancelling headphones',
    'sport earphones',
    'bluetooth headphones for running',
    'sport earbuds',
    'over the ear bluetooth headphones',
    'headphones noise cancelling',
    'running earbuds',
    'gym headphones',
    'cordless earbuds for android',
    'in ear bluetooth headphones',
    'wireless earbuds waterproof',
    'bluetooth running headphones',
    'wireless headphones for running',
    'bluetooth sport headphones',
    'waterproof wireless earbuds',
    'waterproof bluetooth earbuds',
    'bluetooth earbuds for running',
    'bluetooth headphones sport',
    'true wireless headphones',
    'wireless sports headphones',
    'workout bluetooth headphones',
    'noise-cancelling headphones',
    'bluetooth headphones noise canceling',
    'bluetooth headphones waterproof',
    'sport wireless earbuds',
    'sport bluetooth headphones',
    'jogging headphones',
    'sport earbuds wireless',
    'workout earbuds',
    'wireless in ear headphones'
]


class Amazon:

    base_url = 'https://www.amazon.com'
    current_page = 1
    wait_delay_seconds_amount = 5

    def __init__(self):
        self.driver = self.driver_settings()
        self.wait = WebDriverWait(self.driver, 0.5, ignored_exceptions=TimeoutException)

    def driver_settings(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.set_window_size(1920, 1080)

        return driver

    def wait_delay(self, delay=0):

        if delay:
            time.sleep(delay)
        else:
            time.sleep(self.wait_delay_seconds_amount)

    def save_screenshot(self, name=None):

        if name:
            self.driver.save_screenshot(f'screenshots/{str(name)}.png')
            print(f'Screenshot saved! {str(name)}.png')
        else:
            hash = str(uuid.uuid4())[:4]
            self.driver.save_screenshot(f'screenshots/{hash}.png')
            print(f'Screenshot saved! {hash}.png')

    def get_soup(self):
        """get current html """
        return bs(self.driver.page_source, 'lxml')

    def init_search(self, query):
        search_id = 'twotabsearchtextbox'
        search_field = self.wait.until(EC.presence_of_element_located((By.ID, search_id)))
        search_field.clear()
        search_field.send_keys(query)
        search_field.submit()

    def excepted_block(self, soup):
        """checks whether current block is ADs"""

        title = soup.find(lambda tag: tag.name == 'span' and tag.get('class') == ['a-size-large', 'a-color-base'])

        if title:
            if title.text == 'Editorial recommendations':
                return True

        return False

    def get_current_page(self):

        first_page = True
        current_page = False

        url = self.driver.current_url

        url_list = url.split('&')

        for arg in url_list:
            if 'page=' in arg:

                first_page = False
                current_page = int(arg.split('=')[-1])

        if first_page:
            self.current_page = 1
        else:
            self.current_page = current_page

    def next_page(self):

        next_page_x = '//*[@id="search"]/div[1]/div[2]/div/span[7]/div/div/div/ul/li[last()]/a'
        next_page_field = self.wait.until(EC.presence_of_element_located((By.XPATH, next_page_x)))
        next_page_field.click()

    def parse(self):

        data = []

        soup = self.get_soup()
        self.get_current_page()

        items_list = soup.find(lambda tag: tag.name == 'div' and tag.get('class') == ['s-result-list', 'sg-row'])
        if items_list:

            clean_items_list = items_list.findAll(lambda tag: tag.name == 'div' and tag.get('data-asin'))

            for item in clean_items_list:

                if not self.excepted_block(item):

                    image_block = item.find('img', class_='s-image')
                    image_link = image_block.get('src') if image_block else None

                    name_span = item.find(lambda tag: tag.name == 'span' and
                                 tag.get('class') == ['a-size-medium', 'a-color-base', 'a-text-normal'])

                    name = name_span.text if name_span else None

                    rating_block_link = item.find('a', class_='a-popover-trigger a-declarative')
                    rating = rating_block_link.span.text if rating_block_link else None

                    reviews = item.find('span', {'aria-label': rating}).parent.findAll('span')[-1].text if rating else None

                    coupon_block = item.find('span', class_='s-coupon-unclipped')
                    coupon = coupon_block.span.text.strip() if coupon_block else None

                    price_block = item.findAll('span', class_='a-price')

                    try:
                        if not price_block:
                            price = item.find(lambda tag: tag.name == 'span' and
                                                              tag.get('class') == ['a-color-base']).text
                        if len(price_block) == 1:
                            price = price_block[0].find('span', class_='a-offscreen').text

                        if len(price_block) == 2:
                            partial_price_1 = price_block[0].find('span', class_='a-offscreen').text
                            partial_price_2 = price_block[1].find('span', class_='a-offscreen').text
                            price = partial_price_1 + partial_price_2

                    except:
                        # traceback.print_exc()
                        pass

                    else:
                        data.append({
                            'image_link': image_link,
                            'page': self.current_page,
                            'name': name,
                            'rating': rating,
                            'reviews': reviews,
                            'coupon': coupon,
                            'price': price
                        })
        return data


if __name__ == '__main__':

    a = Amazon()

    file_name = os.getcwd() + '/products.csv'
    exists = os.path.isfile(file_name)

    if exists:
        os.remove(file_name)

    with open('products.csv', mode='w') as products:

        products_writer = csv.writer(products, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        products_writer.writerow(['page', 'name', 'rating', 'reviews', 'coupon', 'price'])

        a.driver.get(a.base_url)
        a.wait_delay(2)

        try:

            for product in search_list:

                a.init_search(product)
                a.wait_delay(3)
                a.get_current_page()
                results = a.parse()

                print(f'{a.current_page}/20 of {product}')
                for item in results:

                    products_writer.writerow(
                        [
                            item['page'],
                            item['name'],
                            item['rating'],
                            item['reviews'],
                            item['coupon'],
                            item['price']
                        ]
                    )

                while True:

                    a.next_page()
                    a.wait_delay(3)
                    a.get_current_page()
                    results = a.parse()

                    print(f'{a.current_page}/20 of {product}')
                    for item in results:
                        products_writer.writerow(
                            [
                                item['page'],
                                item['name'],
                                item['rating'],
                                item['reviews'],
                                item['coupon'],
                                item['price']
                            ]
                        )

                    if a.current_page > 19:
                        break

        except Exception as e:
            a.save_screenshot()
            # traceback.print_exc()
            a.driver.quit()
