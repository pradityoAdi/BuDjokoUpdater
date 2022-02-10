import time
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.chrome.service import Service

ser = Service("BuDjoko-Scraper\chromedriver_win32\chromedriver.exe")
op = webdriver.ChromeOptions()


pagelinks = ["https://budjoko.fr/fr/epicerie-fine", "https://budjoko.fr/fr/boissons", "https://budjoko.fr/fr/sante-et-soins", "https://budjoko.fr/fr/non-alimentaire"]

href = []
products=[]
prices=[]
productCode=[]



driver = webdriver.Chrome(service=ser, options=op)


for i in pagelinks:
    print("parsing "+ i)

    # driver.get("https://budjoko.fr/fr/boissons")
    driver.get(i)


    ScrollNumber=5
    for i in range(1, ScrollNumber):
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")
        
    for e in soup.find_all('div', {"class":"hkc-md-2"}):
        href.append(e.find('a')['href'])
        products.append(e.find('a')['title'])
        prices.append(e.find('span', {"class":"hikashop_product_price"}).text)
        productCode.append(e.find('span', {'class':'hikashop_product_code_list'}).find('a').text.replace('\n','').replace('\t',''))


print(href)
print(products)
print(prices)
print(productCode)

print(len(href))
print(len(products))
print(len(prices))
print(len(productCode))

# expecting 260 items 
print("end of the program")

