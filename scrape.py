import time
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.chrome.service import Service


#initialisation
ser = Service("BuDjoko-Scraper\chromedriver_win32\chromedriver.exe")
op = webdriver.ChromeOptions()

# disable all the errors getting displayed on Console
op.add_experimental_option('excludeSwitches', ['enable-logging'])
# hide browser (theorically faster)
op.add_argument("--headless")

href = []
products=[]
prices=[]
productCode=[]
itemAvailability=[]
poids = []



driver = webdriver.Chrome(service=ser, options=op)

# pages to parse
pagelinks = ["https://budjoko.fr/fr/epicerie-fine", "https://budjoko.fr/fr/boissons", "https://budjoko.fr/fr/sante-et-soins", "https://budjoko.fr/fr/non-alimentaire"]

#opening those pages
for i in pagelinks:
    print("parsing "+ i)

    ##opening page i
    driver.get(i)

    # scrolling and waiting because it takes time for the page to load (javascript de merde)
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
        itemAvailability.append(e.find('span', {'class':'hikashop_product_stock_count'}).text)


## scraping weight of each item
counter = 1
for item in href:
    print("parsing " , counter , " of " , len(href) , " items")
    counter+=1

    driver.get(item)

    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    itemPageContent = driver.page_source
    itemPageSoup = BeautifulSoup(itemPageContent, features="html.parser")
    
    weight = itemPageSoup.find('span', {'class':'hikashop_product_weight_main'})
    # to avoid AttributeError: 'NoneType' object has no attribute 'text'
    if(weight != None):
        poids.append(weight.text)
    else:
        poids.append("-1")


#creating a data frame and export to excel
## creating data frame based on created list
df = pd.DataFrame(list(zip(products, prices, productCode, itemAvailability, poids, href)),columns=["product name", "price", "product code", "available", "weight", "href"])

## exporting to excel
df.to_excel("test.xlsx")

print("end of the program")

