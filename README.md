# Selenium Web Scraping for Apartments

Este repositório contém códigos para web scraping de informações sobre apartamentos utilizando a biblioteca Selenium. Os sites alvo são:

- VivaReal (`vivareal.py`)
- Zap Imóveis (`zapimoveis.py`)
- QuintoAndar (`quintoandar.py`)

## Requisitos

- Python 3.x
- Selenium
- Chrome WebDriver version 118.0.x
- Pandas

## Como instalar

1. Clone o repositório
2. Instale as dependências usando `pip install -r requirements.txt`

## Chrome WebDriver

Este projeto utiliza o Chrome WebDriver para automatizar a navegação no Google Chrome. Você precisa baixar e instalar o WebDriver compatível com a sua versão do Chrome.

**Link para download:** [Chrome WebDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)

## Execução

Execute qualquer um dos scripts Python para iniciar o web scraping:

```bash
python vivareal.py
python zapimoveis.py
python quintoandar.py
