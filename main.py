from requests_html import HTMLSession
from bs4 import BeautifulSoup
import requests
import csv
from selenium import webdriver
from urllib.parse import urljoin
import string
from PIL import Image
import shutil
import os

# main function to call other functions
def main():
    driver = webdriver.Chrome()
    catalog_links_list = get_catalog_links(url_catalog='http://carefood.kz/catalog')
    print(catalog_links_list)
    for link in catalog_links_list:
        print(link)
        get_product_data(driver, link)

    driver.quit()

# Code to activate driver and open main page
def get_product_data(driver, url):
    driver.get(url)
    content = driver.page_source.encode('utf-8').strip()
    soup = BeautifulSoup(content, 'lxml')
    carefood_img = 'carefood_img'

    data = []
    parse_product_data(soup, data, carefood_img)

    # Check for pagination and navigate through pages
    pagination = soup.find('div', class_='modern-page-navigation')
    if pagination:
        pages = pagination.find_all('a')
        last_page = pages[-2].text.strip()
        last_page = int(last_page)

        for page_num in range(2, last_page + 1):
            page_url = url + f'?PAGEN_1={page_num}'
            driver.get(page_url)
            content = driver.page_source.encode('utf-8').strip()
            soup = BeautifulSoup(content, 'lxml')
            parse_product_data(soup, data, carefood_img)

    write_to_csv(data)

# This code is responsible for finding the images of all products in each page and take data that we need
def parse_product_data(soup, data, carefood_img):
    product_class = soup.find('div', class_='main_content')
    cards_class = product_class.find('div', class_='product__list row m-0')
    item_class = cards_class.find_all('div', class_='product-item-container col-md-4 col-sm-6 col-12')

    for item in item_class:
        card_class = item.find('div', class_='product_item product-item').find('div', class_='product_item_img')
        img_class = card_class.find('span', class_='product-item-image-alternative').find('img',
                                                                                          class_='product_item_img-bg')
        product_title = item.find('div', class_='product_item_title').find('a').get('title')
        product_img_url = img_class.get('src')
        absolute_url = urljoin("http://carefood.kz/", product_img_url)
        response = requests.get(absolute_url, stream=True)

        if product_title:
            image_name = (product_title.replace(' ', '').replace('&', '').replace('№', '').replace('/', '').replace(',',
                                                                                                                    '').replace(
                '\\', '').replace('|', '').replace('_', '')
                          .translate(str.maketrans('', '', string.punctuation)) + 'carefood')

            with open(f'{image_name}.webp', 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)

            image_path = os.path.join(carefood_img, image_name)

            with open(image_path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)

            data.append({'Title': product_title, 'Image URL': product_img_url, 'Image Path': image_path})

        del response

# Creates the csv file and write all the Image titles, URLs and image paths
def write_to_csv(data):
    csv_path = 'carefood_data.csv'

    with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Image URL', 'Image Path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerows(data)

# Collects links from catalog(лучшие предложения, алкоголь и напитки и т.д.)
def get_catalog_links(url_catalog):
    driver = webdriver.Chrome()
    driver.get(url_catalog)
    content = driver.page_source
    soup = BeautifulSoup(content, 'lxml')
    catalog_links_list = []
    menu = soup.find_all('div', class_='col-sm-6 col-md-4 col-lg-3 catalog-section-list-item')

    for m in menu:
        catalog_link = m.find('a').get('href')
        catalog_links_list.append('http://carefood.kz' + catalog_link)

    driver.quit()

    return catalog_links_list


if __name__ == "__main__":
    main()



