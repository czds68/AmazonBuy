from selenium import webdriver
import time
import json
import pickle
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import random
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

cookies = [{"name":"a-ogbcbff","value":"1","domain":".amazon.com","path":"\/","httponly":False,"expirationDate":1520753508,"hostOnly":False,"httpOnly":True,"secure":False,"storeId":"0","id":0},
           {"name":"at-main","value":"Atza|IwEBIFiVxLbtnfNJaJkb1-NVkOyUDhTPms2aMpqj0fCGogHewt1VwL7jfox1YIAqH32xjPTmnoI8hsCzUeNAdswWuyCtwha-5R5mkSr4r-2zmYgFm8jfhafCxtu5d0u8W0XIKcPPrNxyoQVxP_uK80d0pLUFBmD3SCBrp3Q0rGvTlTq2n8TJ-2EK8w21DiWTACT0Vx55wJfQmJZrqNvBkoga2MY9uoU16iFhQ8RZ53qnQEbqyjKRwZITUql5sSZlTVWmMNY-GZqIsnCLDEpik9kWjgYilWI-6O3Se3EugASO3Hc8oDpn_s1oMb3mMQFatxAQJwTvJBxWWWy_XNvyDo0qSxdEEsVvcqdOCXPPZ-ENehodK1Wf6hE3rlIeDz3nd1zVQEUiLyKbELbteIMpKkkeg0ZW","domain":".amazon.com","path":"\/","httponly":True,"expirationDate":1520753508,"hostOnly":False,"httpOnly":True,"secure":False,"storeId":"0","id":0},
           {"name":"sess-at-main","value":"\"E2UtzsA+su6pF9k058d4+vwu0QbUW\/xJJxAzCOW84Hk=\"""","domain":".amazon.com","path":"\/","httponly":True,"expirationDate":1520753508,"hostOnly":False,"httpOnly":True,"secure":False,"storeId":"0","id":0},
           {"name":"sst-main","value":"Sst1|PQGzUYZyR4tnQPMpbeFkshQeCPRCtAiHpfdcnoO1I7AixFPgA7l45yT5MWbwUrejdnQRfYyj2uqPNuWN0Ct7voplCcZRf7ZEH9XHTg7D_bbiY9vBNPrV1lNOubuQlmW-AktzrJcVOOzKDSsc6SSx3p_-2FzFO5EjZJY9uFd5ADii6l2TYiGISwiA4diGDF-nl5CtClKTx2wXF5TtrcoIcwJ6aknFnA23s-Sf3HEkFpJt_nsnRrsCYugJfYt1t5EVNh-0gqmMgPZZKV5JuvAjAsSwPw","domain":".amazon.com","path":"\/","httponly":True,"expirationDate":1520753508,"hostOnly":False,"httpOnly":True,"secure":False,"storeId":"0","id":0},
           {"name":"skin","value":"noskin","domain":".amazon.com","path":"\/","httponly":False,"expirationDate":1520753508,"hostOnly":False,"httpOnly":True,"secure":False,"storeId":"0","id":0},
           {"name":"ubid-main","value":"132-9106966-9807463","domain":".amazon.com","path":"\/","httponly":False,"expirationDate":1520753508,"hostOnly":False,"httpOnly":True,"secure":False,"storeId":"0","id":0},
           {"name":"x-main","value":"\"6A4O?90HReQnaL9Ddz@q1zBoF4RPuWIa9xVT3MVFSORn9@sEcQeOg9wkL4s6BYSp\"""","domain":".amazon.com","path":"\/","httponly":False,"expirationDate":1520753508,"hostOnly":False,"httpOnly":True,"secure":False,"storeId":"0","id":0},
           {"name":"lc-main","value":"en_US","domain":".amazon.com","path":"\/","httponly":False,"expirationDate":1520753508,"hostOnly":False,"httpOnly":True,"secure":False,"storeId":"0","id":0},
           {"name":"csm-hit","value":"s-KMVY893PBYK2MHKX3CG0|1518160520119","domain":"www.amazon.com","path":"\/","httponly":False,"expirationDate":1520753508,"hostOnly":False,"httpOnly":True,"secure":False,"storeId":"0","id":0},
           {"name":"session-id","value":"135-8322628-0761201","domain":".amazon.com","path":"\/","httponly":False,"expirationDate":1520753508,"hostOnly":False,"httpOnly":True,"secure":False,"storeId":"0","id":0},
           {"name":"session-id-time","value":"2082787201l","domain":".amazon.com","path":"\/","httponly":False,"expirationDate":1520753508,"hostOnly":False,"httpOnly":True,"secure":False,"storeId":"0","id":0},
           {"name":"session-token","value":"\"SFNqOcSOgMA3QcJr4sBYLsVIQf\/6PwBR3j6LPUYWxLBhXi5yc7QB\/RIgQjZqkaQI\/a6z96iqTq8THYopiBzjoZi+KQmWccYE5yv8HoIqZP4gdCBg9wALPGFGB5x+G8zISmmHvhwjQ7XXjkV2lVmc2rLUdR0hoL7Atr34TVU28K0HnK0BhiP7nircYRElMfJyCtr8sB5ZphTC\/z8sujYUYqbPvh92mWOB2G2EO7Lw15U=\"""","domain":".amazon.com","path":"\/","httponly":False,"expirationDate":1520753508,"hostOnly":False,"httpOnly":True,"secure":False,"storeId":"0","id":0}]


def check_exists_by_xpath(driver,xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

#caps = DesiredCapabilities().CHROME
#caps["pageLoadStrategy"] = "none"
#driver = webdriver.Chrome('./chromedriver', desired_capabilities= caps)
#driver.set_page_load_timeout(10)
#co = Options()
#co.add_extension("./EditThisCookie_v1.4.3.crx")
driver = webdriver.Chrome('./chromedriver')

driver.delete_all_cookies()
driver.get("https://www.amazon.com/")


department_element = driver.find_element_by_id('searchDropdownBox')

select = Select(department_element)
select.select_by_value('search-alias=baby-products')

ttt = driver.find_element_by_xpath("//a[contains(text(),'推广')]").location

driver.find_element_by_xpath("//a[contains(text(),'" + "新闻" + "')]").click()
time.sleep(5)
ttt = driver.current_url
driver.forward()
print (ttt)
print('***********************')
driver.delete_all_cookies()
tt = driver.find_element_by_tag_name()
tt.is_displayed()
time.sleep(1)
for cookie in cookies:
    cookie['expirationDate'] = int(time.time() + 3000)
    print(cookie)
    driver.add_cookie(cookie)
ttt = driver.find_element_by_id('nav-link-accountList').find_element_by_class_name('nav-line-1')
print(ttt)


driver.get("https://www.baidu.com/")
print( "opening website")

ttt = driver.find_element_by_xpath("//a[contains(text(),'新闻')]").location()

driver.get("https://www.amazon.com/gp/your-account/order-history?ref_=ya_d_c_yo")
    #signin = driver.find_element_by_xpath("//a[@data-nav-role='signin']").click
    #signin.click()

psd = 'Yourstupid1'
driver.get_cookies()



if check_exists_by_xpath(driver, "//*[text()='Switch accounts']"):
    temp = driver.find_element_by_xpath("//*[text()='Add account']").click()
    time.sleep(5)
if check_exists_by_xpath(driver, "//span[@id='continue']"):
    temp = driver.find_element_by_xpath("//span[@id='continue']").click()
if check_exists_by_xpath(driver, "//input[@id='ap_password']"):
    temp = driver.find_element_by_xpath("//input[@id='ap_password']")
    print("putting password: %s" % psd)
    temp.send_keys(psd)
if check_exists_by_xpath(driver, "//input[@id='signInSubmit']"):
    temp = driver.find_element_by_xpath("//input[@id='signInSubmit']").click()
    print("logging into account")
    time.sleep(5)