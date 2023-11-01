from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time
import re

def remove_accents(text):
    special_chars = {'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'é': 'e', 'ê': 'e', 'í': 'i', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ú': 'u', 'ç': 'c'}
    for char, replacement in special_chars.items():
        text = text.replace(char, replacement)
    return text

# Carregar o arquivo Excel existente para um DataFrame (se o arquivo existir)
try:
    existing_df = pd.read_excel('vivareal.xlsx')
    existing_links = set(existing_df['Link'])
except FileNotFoundError:
    existing_links = set()

# Inicializar o webdriver
driver = webdriver.Chrome()

# Lista para armazenar os dados
data = []

# Número da página inicial
page_num = 1

while True:
    # Acessar o URL
    if page_num == 1:
        url = "https://www.vivareal.com.br/venda/sp/sao-paulo/zona-sul/itaim-bibi/apartamento_residencial/"
    else:
        url = f"https://www.vivareal.com.br/venda/sp/sao-paulo/zona-sul/itaim-bibi/apartamento_residencial/?pagina={page_num}#onde=Brasil,S%C3%A3o%20Paulo,S%C3%A3o%20Paulo,Zona%20Sul,Itaim%20Bibi,,,,BR%3ESao%20Paulo%3ENULL%3ESao%20Paulo%3EZona%20Sul%3EItaim%20Bibi,,,"
        
    driver.get(url)

    # Pausa para garantir que a página tenha carregado
    time.sleep(5)
    
    # Encontrar todos os cartões de propriedades na página
    property_cards = driver.find_elements(By.CSS_SELECTOR, "article.property-card__container")
    
    # Se não há cartões de propriedades, encerrar o loop
    if not property_cards:
        break

    # Loop para extrair informações de cada cartão
    for card in property_cards:
        try:
            title = remove_accents(card.find_element(By.CSS_SELECTOR, "span.property-card__title").text)
        except NoSuchElementException:
            title = 'N/A'
        try:
            address = remove_accents(card.find_element(By.CSS_SELECTOR, "span.property-card__address").text)
        except NoSuchElementException:
            address = 'N/A'
        try:
            size = card.find_element(By.CSS_SELECTOR, "span.property-card__detail-area").text
        except NoSuchElementException:
            size = 'N/A'
        try:
            rooms = card.find_element(By.CSS_SELECTOR, "li.property-card__detail-room").text
        except NoSuchElementException:
            rooms = 'N/A'
        try:
            bathrooms = card.find_element(By.CSS_SELECTOR, "li.property-card__detail-bathroom").text
        except NoSuchElementException:
            bathrooms = 'N/A'
        try:
            parking = card.find_element(By.CSS_SELECTOR, "li.property-card__detail-garage").text
        except NoSuchElementException:
            parking = 'N/A'
        try:
            price = card.find_element(By.CSS_SELECTOR, "div.property-card__price").text
        except NoSuchElementException:
            price = 'N/A'
        try:
            condo = card.find_element(By.CSS_SELECTOR, "strong.js-condo-price").text
        except NoSuchElementException:
            condo = 'N/A'
        try:
            link = card.find_element(By.CSS_SELECTOR, "a.property-card__content-link").get_attribute('href')
        except NoSuchElementException:
            link = 'N/A'

        # Verificar se o link já existe
        if link not in existing_links:
        # Se não existir, adicione à lista e ao set de links existentes
            existing_links.add(link)
            
            # Armazenar as informações em um dicionário e adicionar à lista
            data.append({
                'Titulo': title,
                'Endereço': address,
                'Tamanho': size,
                'Quartos': rooms,
                'Banheiros': bathrooms,
                'Vagas': parking,
                'Price': price,
                'Condominio': condo,
                'Link': link
            })

    # Criar um DataFrame com os dados coletados
    df = pd.DataFrame(data)

    # Converter as colunas de preço e tamanho para números para cálculo
    df['Price'] = df['Price'].apply(lambda x: re.sub(r'\D', '', x) if pd.notnull(x) else 'NaN')
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

    # Remover linhas onde 'Price' ou 'Tamanho' são NaN ou 0
    df = df.dropna(subset=['Price', 'Tamanho'])
    df = df[df['Price'] != 0]
    df = df[df['Tamanho'] != 'N/A']
    df['Tamanho'] = pd.to_numeric(df['Tamanho'], errors='coerce')
    df = df.dropna(subset=['Tamanho'])
    df = df[df['Tamanho'] != 0]

    # Calcular o preço por metro quadrado
    df['Preço por m²'] = df['Price'] / df['Tamanho']

    # Filtrar apartamentos com preço por m² menor que 10000
    filtered_df = df[df['Preço por m²'] < 10000]

    # Salvar o DataFrame final como um único arquivo .xlsx
    filtered_df.to_excel('vivareal.xlsx', index=False)

    # Incrementar o número da página
    page_num += 1

# Fechar o navegador
driver.quit()
