import time
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.chrome.service import Service
from multiprocessing import Pool


def getItemList(url):
    #initialisation
    ser = Service("chromedriver_win32\chromedriver.exe")
    op = webdriver.ChromeOptions()

    # disable all the errors getting displayed on Console
    op.add_experimental_option('excludeSwitches', ['enable-logging'])
    # hide browser
    op.add_argument("--headless")

    driver = webdriver.Chrome(service=ser, options=op)

    ##
    hrefList = list()
    productList= list()
    priceList= list()
    productCodeList= list()
    itemAvailabilityList= list()
    formList= list()

    ##opening page 
    driver.get(url)

    # scrolling and waiting because it takes time for the page to load (javascript de merde)
    ScrollNumber=5
    for i in range(1, ScrollNumber):
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")
    print(url)

    for e in soup.find_all('div', {"class":"hkc-md-2"}):
        # append the product's hyperlink
        href = e.find('a')['href']
        hrefList.append(href)


        # append the product's title
        product = e.find('a')['title']
        productList.append(product)

        # If the price isn't discounted then append full price.
        # replace comma with point and then convert text to float
        if(e.find('span', {"class":"hikashop_product_price_with_discount"}) == None):
            price = float(e.find('span', {"class":"hikashop_product_price"}).text.replace('€','').replace(' ','').replace(',','.'))
        else:
            price = float(e.find('span', {"class":"hikashop_product_price_with_discount"}).text.replace('€','').replace(' ','').replace(',','.'))
        priceList.append(price)
        
        # append the product's code, eliminate whitespaces
        productCode = e.find('span', {'class':'hikashop_product_code_list'}).find('a').text.replace('\n','').replace('\t','') 
        productCodeList.append(productCode)

        # append the product's availability (add "Stock épuisé" if no more stock)
        if(e.find('span', {'class':'hikashop_product_stock_count'}).text.replace('\n','').replace('\t','') != None):
            itemAvailability = "disponible"
        else:
            itemAvailability = e.find('span', {'class':'hikashop_product_stock_count'}).text.replace('\n','').replace('\t','')
        
        itemAvailabilityList.append(itemAvailability)

        # append add to cart hyperlink (will be used to execute orders)
        linkToCart = e.find('a',{'class':'hikabtn hikacart'})
        
        if(linkToCart==None):
            form = "not available"
        else:
            form = linkToCart['href']

        formList.append(form)

    driver.close()
    
    return [hrefList, productList, priceList, productCodeList, itemAvailabilityList, formList]
    
    

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

    driver.close()

    return float(weight)

if __name__ == '__main__':
    
    href = []
    products=[]
    prices=[]
    productCode=[]
    itemAvailability=[]
    form=[]

    itemsProcesses = Pool(4)

    pages = ["https://budjoko.fr/fr/epicerie-fine", "https://budjoko.fr/fr/boissons", "https://budjoko.fr/fr/sante-et-soins", "https://budjoko.fr/fr/non-alimentaire"]
    
    itemList = itemsProcesses.map(getItemList, pages)
    
    
    
    
    itemsProcesses.terminate()
    itemsProcesses.join()

    for e in itemList:
        
        href.append( e[0])
        products.append(e[1])
        prices.append(e[2])
        productCode.append(e[3])
        itemAvailability.append(e[4])
        form.append(e[5])


    href=href[0]
    products=products[0]
    prices=prices[0]
    productCode=productCode[0]
    itemAvailability=itemAvailability[0]
    form=form[0]

    print("main page scraped")

    # driver.close()


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
    print("end of the program")
