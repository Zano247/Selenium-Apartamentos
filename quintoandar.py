from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

driver = webdriver.Chrome()
url = "https://www.quintoandar.com.br/comprar/imovel/itaim-bibi-sao-paulo-sp-brasil/de-150000-a-1200000-venda"
driver.get(url)
wait = WebDriverWait(driver, 10)

xlsx_file = "QuintoAndar.xlsx"
if os.path.exists(xlsx_file):
    apartments = pd.read_excel(xlsx_file).to_dict(orient='records')
else:
    apartments = []

def remove_accents(text):
    special_chars = {'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'é': 'e', 'ê': 'e', 'í': 'i', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ú': 'u', 'ç': 'c'}
    for char, replacement in special_chars.items():
        text = text.replace(char, replacement)
    return text

last_processed_card = 0
while True:
    try:
        apartment_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='house-card-container']")))
        logging.info(f"Found {len(apartment_cards)} apartment cards.")
    except Exception as e:
        logging.error(f"Error locating cards: {e}")

    for i in range(last_processed_card, len(apartment_cards)):
        card = apartment_cards[i]
        apartment_data = {}
        try:
            street = card.find_element(By.XPATH, ".//span[@data-testid='house-card-address']").text
            neighborhood = card.find_element(By.XPATH, ".//span[@data-testid='house-card-region']").text
            apartment_data['Street'] = remove_accents(street)
            apartment_data['Neighborhood'] = remove_accents(neighborhood)
        except Exception as e:
            logging.error(f"Failed to extract street or neighborhood. Error: {e}")

        try:
            details = card.find_element(By.XPATH, ".//small[@data-testid='house-card-area']").text
            size, rooms, parking = map(int, re.findall(r'(\d+)', details))
            apartment_data['Size'] = size
            apartment_data['Rooms'] = rooms
            apartment_data['Parking'] = parking
        except Exception as e:
            logging.error(f"Failed to extract details. Error: {e}")

        try:
            price_elements = card.find_elements(By.XPATH, ".//div[@data-testid='house-card-footer-sale']//small[contains(., 'R$')]")
            if len(price_elements) >= 2:
                iptu = int(re.sub(r'[^\d]', '', price_elements[0].text))
                price = int(re.sub(r'[^\d]', '', price_elements[1].text))
                apartment_data['IPTU'] = iptu
                apartment_data['Price'] = price
                apartment_data['Price/m2'] = price / apartment_data['Size']
            else:
                logging.warning("Less than two price-related elements found. Data might be incomplete.")
        except Exception as e:
            apartment_data['IPTU'] = None
            apartment_data['Price'] = None
            apartment_data['Price/m2'] = None
            logging.error(f"Failed to extract price or IPTU. Error: {e}")

        try:
            link = card.find_element(By.XPATH, ".//a").get_attribute('href')
            apartment_data['Link'] = link
        except:
            apartment_data['Link'] = None

        # Calcula o preço por m² e salva apenas se for menor que 10,000
        if apartment_data.get('Price') and apartment_data.get('Size'):
            try:
                price_per_m2 = apartment_data['Price'] / apartment_data['Size']
                apartment_data['Price/m2'] = price_per_m2
                if price_per_m2 < 10000:
                    apartments.append(apartment_data)
            except Exception as e:
                apartment_data['Price/m2'] = None
                logging.error(f"Could not calculate price/m². Error: {e}")
                              
    last_processed_card = len(apartment_cards)

        
    df = pd.DataFrame(apartments)
    df.to_excel(xlsx_file, index=False)
    logging.info(f'Information saved to {xlsx_file}')

    try:
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Ver mais"]')))
        next_button.click()
        time.sleep(2)
    except Exception as e:
        logging.error(f"Could not find 'Ver mais' button or failed to click. Error: {e}")
        break

driver.quit()
logging.info('Scraping completed and information saved.')
