####Tentativa de rodar o codigo para os imoveis em sao paulo limitando para as 100 primeiras paginas
#Faltando numero de vagas, quartos, links
#salvar apenas imoveis que atendam certas circunstancias (m2>10k)



# Importing required libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re 
import pandas as pd
import time
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to remove accents and special characters from Portuguese text
def remove_accents(text):
    special_chars = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u',
        'ç': 'c'
    }
    for char, replacement in special_chars.items():
        text = text.replace(char, replacement)
    return text

def slow_scroll(driver, scroll_step, max_retries):
    prev_scroll_pos = driver.execute_script('return window.pageYOffset;')  # Get the current scroll position
    retries = 0
    
    while retries < max_retries:
        # Perform a small scroll
        driver.execute_script(f'window.scrollBy(0, {scroll_step});')
        time.sleep(1)  # Adjust sleep time as needed to allow content to load
        
        # Check if the scroll position has changed, indicating possible new content
        curr_scroll_pos = driver.execute_script('return window.pageYOffset;')
        
        if curr_scroll_pos > prev_scroll_pos:
            retries = 0  # Reset retries as the scroll position changed
            prev_scroll_pos = curr_scroll_pos  # Update the previous scroll position
        else:
            retries += 1  # Increment retries as no change in scroll position
    
    logging.info('Finished scrolling')

# Initialize the WebDriver
driver = webdriver.Chrome()

# Navigate to the homepage
url = 'https://www.zapimoveis.com.br/venda/apartamentos/sp+sao-paulo+zona-oeste+jardins/?__ab=exp-aa-test:control,new-discover-zap:alert,vas-officialstore-social:enabled&transacao=venda&onde=,S%C3%A3o%20Paulo,S%C3%A3o%20Paulo,Zona%20Oeste,Jardins,,,neighborhood,BR%3ESao%20Paulo%3ENULL%3ESao%20Paulo%3EZona%20Oeste%3EJardins,-23.57476,-46.648786,;,S%C3%A3o%20Paulo,S%C3%A3o%20Paulo,Zona%20Sul,Itaim%20Bibi,,,neighborhood,BR%3ESao%20Paulo%3ENULL%3ESao%20Paulo%3EZona%20Sul%3EItaim%20Bibi,-23.583748,-46.678074,&tipos=apartamento_residencial&pagina=1'
driver.get(url)

# Configure the wait
wait = WebDriverWait(driver, 180)

# Initialize list to store all data
all_apartments_data = []

page_number = 1  # Initialize page number

# Define the file name
csv_file = "Imoveis/SP.xlsx"

# Check if the CSV file already exists, if yes, load existing data
if os.path.exists(csv_file):
    all_apartments_data = pd.read_csv(csv_file).to_dict(orient='records')
else:
    all_apartments_data = []  # Initialize list to store all data

while page_number <= 100:  # Limit pages to 100
    logging.info(f'Loading content for page {page_number}')

    # Scroll to 30% of the page to start
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
    time.sleep(1)  # Adjust sleep time as needed to allow initial content to load

    # Call the slow_scroll function to control scrolling
    slow_scroll(driver, scroll_step=1000, max_retries=10)  # Adjust parameters as needed

    # Step 1: Scroll to x% of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
    
    # Step 2: Wait 1 second to load new data
    time.sleep(1)
    
    # Step 3: Scroll down from the current point
    for _ in range(5):
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight / 15);")
        time.sleep(0.5)
        
    # Step 5: Save the information from the page
    try:
        cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="l-card__content"]')))
    except Exception as e:
        logging.error(f'Error locating cards: {e}')
        break  # Exit loop on error

    logging.info(f'Content loaded for page {page_number}')

    apartments_data = []

    # Iterate through the cards to scrape data
    for card in cards:
        apartment_info = {}
        try:
            location = card.find_element(By.XPATH, './/section[@data-testid="card-address"]/div/h2').text
            apartment_info['Location'] = remove_accents(location)
        except:
            apartment_info['Location'] = "N/A"

        try:
            street_address = card.find_element(By.CSS_SELECTOR, 'p.card__street').text
            apartment_info['Street Address'] = remove_accents(street_address)
        except:
            apartment_info['Street Address'] = "N/A"
                            
        try:
            size = card.find_element(By.XPATH, './/section[@class="card__amenities "]/p[@itemprop="floorSize"]').text
            # Remove non-numeric characters from the size string
            size = re.sub(r'\D', '', size)
            apartment_info['Size'] = size
        except:
            apartment_info['Size'] = "N/A"
            
        try:
            bathrooms = card.find_element(By.XPATH, './/section[@class="card__amenities "]/p[@itemprop="numberOfBathroomsTotal"]').text
            apartment_info['Bathrooms'] = remove_accents(bathrooms)
        except:
            apartment_info['Bathrooms'] = "N/A"
            
        try:
            price = card.find_element(By.XPATH, './/div[@class="listing-price"]/p[1]').text
            # Remove non-numeric characters from the price string
            price = re.sub(r'\D', '', price)
            apartment_info['Price'] = price
        except:
            apartment_info['Price'] = "N/A"

        try:
            description = card.find_element(By.XPATH, './/div/p[@itemprop="description"]').text
            apartment_info['Description'] = remove_accents(description)
        except:
            apartment_info['Description'] = "N/A"

        apartments_data.append(apartment_info)

    all_apartments_data.extend(apartments_data)  # Append new data to the main list
    
    logging.info(f'Information scraped for page {page_number}')


    # Step 6: Go to the next page by modifying the URL
    page_number += 1  # Increment page number
    next_page_url = f"https://www.zapimoveis.com.br/venda/apartamentos/sp+sao-paulo+zona-oeste+jardins/?__ab=exp-aa-test:control,new-discover-zap:alert,vas-officialstore-social:enabled&transacao=venda&onde=,S%C3%A3o%20Paulo,S%C3%A3o%20Paulo,Zona%20Oeste,Jardins,,,neighborhood,BR%3ESao%20Paulo%3ENULL%3ESao%20Paulo%3EZona%20Oeste%3EJardins,-23.57476,-46.648786,;,S%C3%A3o%20Paulo,S%C3%A3o%20Paulo,Zona%20Sul,Itaim%20Bibi,,,neighborhood,BR%3ESao%20Paulo%3ENULL%3ESao%20Paulo%3EZona%20Sul%3EItaim%20Bibi,-23.583748,-46.678074,&tipos=apartamento_residencial&pagina={page_number}"
    driver.get(next_page_url)
    logging.info(f'Navigated to page {page_number}')

    all_apartments_data.extend(apartments_data)  # Append new data to the main list
    
    logging.info(f'Information scraped for page {page_number}')

    # Step 6.5: Save the information into a .csv file after each page
    df = pd.DataFrame(all_apartments_data)
    df.to_csv(csv_file, index=False)
    logging.info(f'Information saved to {csv_file}')
    
    # Check for the "Oops" message indicating no more pages
    oops_message = driver.find_elements(By.XPATH, '//h2[text()="Oops."]')
    if oops_message:
        logging.info('Last page reached')
        break  # Exit loop if the "Oops" message is found
    else:
        logging.info('No Oops message found, continuing to next page')


# Step 7: Save all the information into a .csv file
df = pd.DataFrame(all_apartments_data)

# Convert 'Price' and 'Size' columns to numeric (this will convert "N/A" to NaN)
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df['Size'] = pd.to_numeric(df['Size'], errors='coerce')

# Calculate Price per Square Meter and create a new column for it
df['Price per Square Meter'] = df['Price'] / df['Size']

df.to_excel("Imoveis/SP.xlsx", index=False)  # Requires the openpyxl library


logging.info('Information saved to apartments.csv and apartments.xlsx')

# Step 8: Print success message
print("The information was saved in the apartments.xlsx file")

# Step 9: Stop the program
driver.quit()