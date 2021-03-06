# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pdb
from myorator import db
import time

SCROLL_PAUSE_TIME = 0.5

chrome_options=Options()
#设置chrome浏览器无界面模式
chrome_options.add_argument('--headless')
chrome_prefs = {}
chrome_options.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

browser = webdriver.Chrome(options=chrome_options)
browser.get("https://show.1688.com/pinlei/industry/pllist.html?spm=a260k.dacugeneral.home2019category.11.6633436c2TKsNU&sceneSetId=869&sceneId=2626")
# Get scroll height
last_height = browser.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)
    # Calculate new scroll height and compare with last scroll height
    new_height = browser.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

category_name = browser.find_element_by_xpath('/html/body/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div/div[1]/div[2]/div/ul/li/div/label/span[2]/a').text
detail_page_arr = []

for item in browser.find_element_by_class_name('list').find_elements_by_tag_name('a'):
    try:
        detail_url = item.get_attribute('href')
        detail_page_arr.append(detail_url)
    except Exception as e:
        print(e)
        continue

print('detail_page_arr: %s'.format(len(detail_page_arr)))

for url in detail_page_arr:
    try:
        print(url)
        browser.get(url)
        # Get scroll height
        last_height = browser.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)
            # Calculate new scroll height and compare with last scroll height
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        name = browser.find_element_by_class_name('d-title').text
        price = browser.find_element_by_class_name('price-data-wrap').text
        start_amount = browser.find_element_by_class_name('price-begin-wrap').text
        delivery = browser.find_element_by_class_name('mod-detail-postage').text
        seller_service = browser.find_element_by_class_name('mod-detail-guarantee').text
        paid_types = browser.find_element_by_class_name('mod-detail-tradetype').text
        detail_info = browser.find_element_by_id('mod-detail-attributes').text

        item_id = db.table('items').insert_get_id({
            'name': name,
            'category_name': category_name,
            'url': url,
            'price': price,
            'start_amount': start_amount,
            'delivery': delivery,
            'seller_service': seller_service,
            'paid_types': paid_types,
            'detail_info': detail_info,
        })

        try:
            units = browser.find_element_by_class_name('list-leading').find_elements_by_tag_name('li')
            for i in units:
                data_unit_config = i.find_element_by_tag_name('div').get_attribute('data-unit-config')
                img32 = i.find_element_by_tag_name('img').get_attribute('src')
                db.table('colors').insert({
                    'item_id': item_id,
                    'data-unit-config': data_unit_config,
                    'img32': img,
                })
        except Exception as e:
            print(e)
            pass
        
        skus = browser.find_element_by_class_name('table-sku').find_elements_by_tag_name('tr')
        for i in skus:
            try:
                sku_config = i.get_attribute('data-sku-config')
                img = i.find_element_by_tag_name('img').get_attribute('src')
                price = i.find_element_by_class_name('price').text
                count = i.find_element_by_class_name('count').text
                db.table('skus').insert({
                    'item_id': item_id,
                    'sku_config': sku_config,
                    'img': img,
                    'price': price,
                    'count': count,
                })
            except Exception as e:
                print(e)
                continue
        
        tabs = browser.find_elements_by_xpath('//*[@id="dt-tab"]/div/ul/li')
        for i in tabs:
            try:
                data_img = i.get_attribute('data-imgs')
                img60 = i.find_element_by_tag_name('img').get_attribute('src')
                db.table('tabs').insert({
                    'item_id': item_id,
                    'data_img': data_img,
                    'img60': img60,
                })
            except Exception as e:
                print(e)
                continue
        imgs = browser.find_elements_by_xpath('//*[@id="desc-lazyload-container"]/div[2]/p')
        for i in imgs:
            try:
                inner_imgs = i.find_elements_by_tag_name('img')
                for j in inner_imgs:
                    try:
                        img = j.get_attribute('src')
                        db.table('imgs').insert({
                            'item_id': item_id,
                            'img': img,
                        })
                    except Exception as e:
                        print(e)
                        continue
            except Exception as e:
                print(e)
                continue
    except Exception as e:
        print(e)
        continue
#关闭浏览器
browser.close()
#关闭chreomedriver进程
browser.quit()