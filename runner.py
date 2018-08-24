from LRest import LRest

runner = LRest('http://169.254.235.45:5004','6803-10.20.51.218')
#print(runner.get('Device Type'))

'''
from selenium import webdriver
from bs4 import BeautifulSoup
import time
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('disable-gpu')
driver = webdriver.Chrome(chrome_options=options)
driver.get('http://169.254.235.45:5004/#/clients/6803-10.20.51.218')
time.sleep(2)
encoded_source=driver.execute_script("return document.documentElement.outerHTML").encode('utf-8')
driver.close()
soup = BeautifulSoup(encoded_source,'html.parser')
print(soup.prettify().encode('utf-8'))
'''