import re
import json
import requests
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# Настройка Selenium
service = Service(r'C:\Users\Пользователь\Documents\Учеба\Аналитика\Data engenir\Сбор и разметка данных\lesson7\chromedriver-win64\chromedriver-win64\chromedriver.exe')
options = Options()
options.add_argument('start-maximized') 
driver = webdriver.Chrome(service=service, options=options)

try:
    # Открытие сайта Yandex Market
    driver.get('https://market.yandex.ru/')
    sleep(5)

    # Поиск по запросу
    search_input = driver.find_element(By.ID, "header-search")
    search_input.send_keys('планшет samsung')
    search_input.send_keys(Keys.ENTER)
    sleep(5)

    # Прокрутка страницы для загрузки данных
    for _ in range(11): 
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        sleep(2)

    # Создание объекта BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Находим карточки товаров
    product_cards = soup.find_all('div', class_="_2rw4E _2g7lE")
    print(len(product_cards))

    # Собираем ссылки на товары
    product_links = set()
    for card in product_cards:
        link_tag = card.find('a', class_="EQlfk Gqfzd")
        url_link = link_tag['href'] if link_tag else None
        
        if url_link:
            full_link = f"https://market.yandex.ru{url_link}"  # Добавляем базовый URL
            product_links.add(full_link)

    data = []

    for link in product_links:
        try:
            # Загружаем страницу товара
            response = requests.get(link, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'})
            response.raise_for_status()
            sleep(1)
            
            # Создание объекта BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Название товара
            title_tag = soup.find('h1')
            title = title_tag.text.strip() if title_tag else "Название не найдено"

            # Цена товара
            price_classes = ["Jdxhz", "_3oild _6tyDq u1R1k _2qQwh _2O3Fw", "_3oild _6tyDq u1R1k _2O3Fw"]

            price_tag = None
            for class_name in price_classes:
                price_tag = soup.find('h3', class_=class_name)
                if price_tag:  
                    break
            price = price_tag.text.strip() if price_tag else "Цена не найдена"
            
            if price != "Цена не найдена":
                # Удаляем нечисловые символы и преобразуем в число
                price_cleaned = int(re.sub(r'[^\d]', '', price))
            else:
                price_cleaned = None  

            # О товаре
            description_tag = soup.find('div', class_="ds-text ds-text_weight_reg ds-text_typography_text xt_vL ds-text_text_loose ds-text_text_reg")
            description = description_tag.text.strip() if description_tag else 'Описание не найдено'

            data.append({
                'Название': title,
                'Цена': price_cleaned,
                'Описание': description,
                'Ссылка': link})
            
        
        except requests.RequestException as error:
            print(f"Ошибка загрузки страницы {link}: {error}")

finally:
    driver.quit()

with open('yandex_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Сбор данных завершен. Данные сохранены в файл yandex_data.json")
