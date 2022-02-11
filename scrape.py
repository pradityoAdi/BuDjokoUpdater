import time
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.chrome.service import Service
from multiprocessing import Pool


def getItemList():
    itemList = []
    # pages to parse
    pagelinks = ["https://budjoko.fr/fr/epicerie-fine", "https://budjoko.fr/fr/boissons", "https://budjoko.fr/fr/sante-et-soins", "https://budjoko.fr/fr/non-alimentaire"]
    href = []
    products=[]
    prices=[]
    productCode=[]
    itemAvailability=[]
    form=[]

    #opening those pages
    for page in pagelinks:
        print("parsing "+ page)

        ##opening page i
        driver.get(page)

        # scrolling and waiting because it takes time for the page to load (javascript de merde)
        ScrollNumber=5
        for i in range(1, ScrollNumber):
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        content = driver.page_source
        soup = BeautifulSoup(content, features="html.parser")
            
        for e in soup.find_all('div', {"class":"hkc-md-2"}):
            # append the product's hyperlink
            href.append(e.find('a')['href'])

            # append the product's title
            products.append(e.find('a')['title'])

            # If the price isn't discounted then append full price.
            # replace comma with point and then convert text to float
            if(e.find('span', {"class":"hikashop_product_price_with_discount"}) == None):
                prices.append(float(e.find('span', {"class":"hikashop_product_price"}).text.replace('€','').replace(' ','').replace(',','.')))
            else:
                prices.append(float(e.find('span', {"class":"hikashop_product_price_with_discount"}).text.replace('€','').replace(' ','').replace(',','.')))
            
            # append the product's code, eliminate whitespaces
            productCode.append(e.find('span', {'class':'hikashop_product_code_list'}).find('a').text.replace('\n','').replace('\t',''))

            # append the product's availability (add "Stock épuisé" if no more stock)
            itemAvailability.append(e.find('span', {'class':'hikashop_product_stock_count'}).text)
            
            # append add to cart hyperlink (will be used to execute orders)
            linkToCart = e.find('a',{'class':'hikabtn hikacart'})
            if(linkToCart==None):
                form.append("not available")
            else:
                form.append(linkToCart['href'])

    # ["product name", "price", "product code", "available", "weight", "href", "form link"]
    
    return (href, products, prices, productCode, itemAvailability, form)

def getWeightItem(url):
    #initialisation
    ser = Service("chromedriver_win32\chromedriver.exe")
    op = webdriver.ChromeOptions()

    # disable all the errors getting displayed on Console
    op.add_experimental_option('excludeSwitches', ['enable-logging'])
    # hide browser
    op.add_argument("--headless")

    driver = webdriver.Chrome(service=ser, options=op)


    driver.get(url)
    print("parsing ", url)
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    itemPageContent = driver.page_source
    itemPageSoup = BeautifulSoup(itemPageContent, features="html.parser")
    
    weight = itemPageSoup.find('span', {'class':'hikashop_product_weight_main'})
    # to avoid AttributeError: 'NoneType' object has no attribute 'text'
    if(weight != None):
        weight = weight.text.replace('\n','').replace('Poids brut: ','')
        if(weight.__contains__("kg")):
            weight = weight.replace('kg','')
            weight = float(weight) * 1000
        else:
            weight = weight.replace('g','')
        
    else:
        weight=float(-1)


    return float(weight)

if __name__ == '__main__':
    #initialisation
    ser = Service("chromedriver_win32\chromedriver.exe")
    op = webdriver.ChromeOptions()

    # disable all the errors getting displayed on Console
    op.add_experimental_option('excludeSwitches', ['enable-logging'])
    # hide browser
    op.add_argument("--headless")

    driver = webdriver.Chrome(service=ser, options=op)


    (href, products, prices, productCode, itemAvailability, form) =getItemList()

    driver.close()


    poids = []
    p = Pool(12)
    poids = p.map(getWeightItem, href)

    p.terminate()
    p.join()
    print("products weight scraped")

    #creating a data frame and export to excel
    ## creating data frame based on created list
    df = pd.DataFrame(list(zip(products, prices, productCode, itemAvailability, poids, href, form)),columns=["product name", "price", "product code", "available", "weight", "href", "form link"])

    ## exporting to excel
    df.to_excel("scraped.xlsx")

    print(df)
    print(type(poids))
    print(type(products))
    print("end of the program")
