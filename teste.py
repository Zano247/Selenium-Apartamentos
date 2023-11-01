from selenium import webdriver

# Inicialize o driver
driver = webdriver.Chrome()

# Obtenha a versão
version = driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]

# Feche o driver
driver.quit()

print(f"ChromeDriver version: {version}")
