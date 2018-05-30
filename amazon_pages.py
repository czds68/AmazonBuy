from page_scroll import page_scroll
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
from datetime import datetime
import random
import re
from urllib import request
from captcha2upload import CaptchaUpload
import traceback
import json
import names
from random import randint
import os
from verificationcode import getverifycode
from AmazonTables import chars
from AmazonTables import DepartmentTable
import threading

class AmazonPages(page_scroll):
    def __init__(self, driver):
        self.driver = driver
        self.speed = 20  # page scroll speed
        self.captcha = CaptchaUpload('f4ab06a8e3e5be77134312d55c7a7bb4')

    def Probability(self, probability):
        if random.random() <= probability:
            return True
        else:
            return False

    def WalkAround(self, RetryNum = [2, 5], ScrollSpeed = [10,40]):
        try:
            PageSize = self.get_page_size()
            # scroll page
            for i in range(randint(RetryNum[0], RetryNum[1])):
                self.speed = randint(ScrollSpeed[0], ScrollSpeed[1])
                self.sroll_to_position(randint(0, PageSize))
            return True
        except:
            print(traceback.print_exc())
            return False



    def NoThanks(self):
        try: self.ClickElement(self.driver.find_element_by_id('btnNoThanks'))
        except:pass
        try: self.ClickElement(self.driver.find_element_by_class_name("dismiss"))
        except: pass
        try: self.ClickElement(self.driver.find_element_by_id('siNoCoverage-announce'))
        except: pass

    def NoDonate(self):
        try: self.ClickElement(self.driver.find_element_by_class_name("dismiss"))
        except: pass
    def NoCoverage(self):
        try: self.ClickElement(self.driver.find_element_by_id('siNoCoverage-announce'))
        except: pass

    def ClosePopUps(self):
        ThreadGroup = []
        ElementFuncs = [self.NoCoverage(), self.NoDonate(), self.NoThanks()]
        for Func in ElementFuncs:
            task_thread = threading.Thread(target=Func)
            task_thread.setDaemon(daemonic=True)
            task_thread.start()
            self.ThreadGroup.append(task_thread)
        for item in ThreadGroup:
            while item.is_alive():
                time.sleep(1)

    def RandomClick(self, exclude = 'xxxxxxxxxx'):
        try:
            # click Items
            while True:
                PageItems = self.driver.find_elements_by_class_name("a-link-normal")
                SelectedItem = random.sample(PageItems, 1)[0]
                if ('/dp/' in SelectedItem.get_attribute("href") or \
                    '/gp/slredirect/' in SelectedItem.get_attribute("href")) and \
                    SelectedItem.is_enabled() and SelectedItem.is_displayed() and \
                    (exclude not in SelectedItem.get_attribute("href")):
                    self.move_to_element(SelectedItem)
                    SelectedItem.click()
                    return True
        except:
            print('View other Product fail!')
            return False

    def GoToNextPage(self):
        try:
            next_page = self.driver.find_element_by_id("pagnNextLink")
            self.ScrollToElement(next_page)
            next_page.click()
            return True
        except:
            return False

    def ViewOtherProduct(self, asin):
        urlreccored = self.driver.current_url
        self.RandomClick(exclude = asin)
        self.ViewWholePage(ScrollSpeed=[20, 60])
        self.WalkAround(RetryNum = [1, 3], ScrollSpeed=[20, 60])
        self.driver.back()
        time.sleep(5)
        if self.driver.current_url != urlreccored:
            try:
                self.driver.get(urlreccored)
                time.sleep(5)
            except:
                print('Try to go back fail')

    def ViewOurProduct(self, timeout = 200):
        StartTime = datetime.now()
        if not self.ViewWholePage():
            return False
        if not self.WalkAround(RetryNum=[1, 5]):
            return False
        #if not self.view_thumbnail():
        #    return False
        self.ViewReviewer()
        if (datetime.now() - StartTime).seconds > timeout:
            return True
        self.ViewDetailAnswers()
        self.ViewMoreAnswer()
        while (datetime.now() - StartTime).seconds < timeout:
            self.WalkAround(RetryNum=[1, 2])
        return True


    def SubmitDepartment(self, department = ''):
        # select department
        try:
            department_element = self.driver.find_element_by_id('searchDropdownBox')
            self.ScrollToElement(department_element)
            select = Select(department_element)
            select.select_by_value(DepartmentTable[department])
            return True
        except:
            print(traceback.print_exc())
            print("department submit fail!")
            return False

    def SubmitKeyword(self, keyword=None):
        # check keyword existing
        if not keyword:
            print("I can't work without ketwords")
            return False
        # submit keyword
        try:
            search_box = self.driver.find_element_by_id("twotabsearchtextbox")
            self.ScrollToElement(search_box)
            search_box.clear()
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)
            return True
        except:
            print("keyword submit fail")
            return False

    def SetPrice(self, lowprice=None, highprice=None):
        # change price interval
        try:
            if float(lowprice) > float(highprice):
                exchange_price = lowprice
                lowprice = highprice
                highprice = exchange_price
        except:
            print("search without price...")
            return True
        if highprice and lowprice:
            # noinspection PyBroadException
            try:
                lowprice_element = self.driver.find_element_by_id('low-price')
                highprice_element = self.driver.find_element_by_id('high-price')
                self.ScrollToElement(lowprice_element)
                lowprice_element.clear()
                lowprice_element.send_keys(lowprice)
                highprice_element.clear()
                highprice_element.send_keys(highprice)
                highprice_element.send_keys(Keys.RETURN)
                print("price set done!")
                return True
            except:
                print("price set fail!")
                return False
        else:
            print("search without price...")
            return True

    def FindProduct(self, asin, ClickProduct =True):
        try:
            PageItems = self.driver.find_elements_by_class_name("a-link-normal") + self.driver.find_elements_by_class_name("a-button-inner")
            for item in PageItems:
                if (('dp/' + asin) in item.get_attribute("href")) and item.is_enabled() and item.is_displayed():
                    print('Production found!')
                    if ClickProduct:
                        self.ScrollToElement(item)
                        item.click()
                    return True
        except:
            print(traceback.print_exc())
            pass
        return False

    def ViewWholePage(self, ScrollSpeed = [10,40]):
        # noinspection PyBroadException
        try:
            WebDriverWait(self.driver, 30, 0.5, ignored_exceptions=TimeoutException)\
                .until(EC.visibility_of_element_located((By.ID, 'navBackToTop')))
            back_to_top = self.driver.find_element_by_id('navBackToTop')
            self.speed = randint(ScrollSpeed[0], ScrollSpeed[1])
            self.ScrollToElement(back_to_top)
            return True
        except :
            print('View whole page fail!')
            return False

    def ViewReviewer(self, probability = 0.4, ScrollSpeed = [10,40]):
        # noinspection PyBroadException
        try:
            self.driver.find_element_by_id('cm-cr-dp-review-list').find_elements_by_tag_name("a")
        except:
            print('No reviewer yet...')
            return True

        # noinspection PyBroadException
        try:
            reviewer_header = self.driver.find_element_by_id('cm-cr-dp-review-header')
            reviewer_footer = self.driver.find_element_by_id("reviews-medley-footer")
            self.speed = randint(ScrollSpeed[0], ScrollSpeed[1])
            self.ScrollToElement(reviewer_header)
            self.ScrollToElement(reviewer_footer)
        except :
            print('Scroll to reviewer failed...')
            pass

        # noinspection PyBroadException
        try:
            reviewerlighthut = self.driver.find_element_by_id('cr-lighthut-1-')
            reviewer_list = reviewerlighthut.find_elements_by_tag_name("a")
        except:
            reviewer_list = ''
            pass

        try:
            reviewer_summary = self.driver.find_element_by_id('reviewSummary')
            for item in reviewer_list:
                if self.Probability(probability) and item.is_displayed() and item.is_enabled():
                    self.speed = randint(ScrollSpeed[0], ScrollSpeed[1])
                    self.ScrollToElement(reviewer_summary)
                    item.click()
                    time.sleep(2)
                    self.ScrollToElement(self.driver.find_element_by_id("reviews-medley-footer"))
            return True
        except:
            print(traceback.print_exc())
            print('Error happen when view reviewer!')
            return False

    def view_thumbnail(self, probability = 0.4, interval = [1,5]):
        # noinspection PyBroadException
        try:
            WebDriverWait(self.driver, 10, 0.5, ignored_exceptions=TimeoutException)\
                .until(EC.visibility_of_element_located((By.ID, 'altImages')))
            thumbnail = self.driver.find_element_by_id('altImages')
            self.ScrollToElement(thumbnail)
            sub_thumbnails = thumbnail.find_elements_by_class_name('a-button-thumbnail')
            for item in sub_thumbnails:
                if probability:
                    ActionChains(self.driver).move_to_element(item).perform()
                    time.sleep(randint(interval[0], interval[1]))
            return True
        except:
            print('Error happen when view thumbnail!')
            return False


    def ViewDetailAnswers(self, probability = 0.1, ScrollSpeed = [10,40]):
        # noinspection PyBroadException
        try:
            QandA_zone = self.driver.find_element_by_id("ask_lazy_load_div")
            self.ScrollToElement(QandA_zone)
            detail_answers = QandA_zone.find_elements_by_class_name('askWidgetSeeAllAnswersInline')
            for item in detail_answers:
                if probability:
                    self.speed = randint(ScrollSpeed[0], ScrollSpeed[1])
                    self.ScrollToElement(item)
                    self.ClickElement(item)
                    time.sleep(1)
            return True
        except:
            print('Error happen when view detail answers!')
            return False

    def ViewMoreAnswer(self, probability = 0.1, ScrollSpeed = [10,40]):
        # noinspection PyBroadException
        try:
            QandA_zone = self.driver.find_element_by_id("ask_lazy_load_div")
            self.ScrollToElement(QandA_zone)
            more_answers = QandA_zone.find_elements_by_class_name('askLoadMoreQuestionsLink')
            for i in range(len(more_answers)):
                if probability:
                    self.speed = randint(ScrollSpeed[0], ScrollSpeed[1])
                    self.ScrollToElement(more_answers[i])
                    self.ClickElement(more_answers[i])
                    time.sleep(2)
            return True
        except:
            print('Error happen when view more answers!')
            return False

    def SelectAsinFromBuyBox(self, asin):
        # noinspection PyBroadException
        try:
            self.driver.find_element_by_id('twisterContainer')
        except:
            print('No other ASINs to Select')
            return True
        try:
            SwatchAvailable = self.driver.find_elements_by_class_name('swatchAvailable')
            for item in SwatchAvailable:
                if asin in item.get_attribute('data-defaultasin'):
                    self.ScrollToElement(item)
                    item.click()
                    time.sleep(1)
                    break
        except:
            print('Error happen when select ASIN and click!')
            return False
        try:
            SwatchSelect = self.driver.find_element_by_class_name('swatchSelect')
            if asin in SwatchSelect.get_attribute('data-defaultasin'):
                return True
        except:
            pass
        return False

    def GoOfferList(self):
        try:
            WebDriverWait(self.driver, 10, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "feature-bullets")))
            NewButtons = self.driver.find_elements_by_partial_link_text('from')
            for item in NewButtons:
                if 'offer-listing' in str(item.get_attribute("href")):
                    self.move_to_element(item)
                    self.ClickElement(item)
                    break
        except:
            print('OfferList link error!!!')
            print(traceback.print_exc())
            return False

    def AddCartByOfferList(self, OrderPrice, Seller = 'NotInput', SelectBy = 'Price'):
        # Add to Cart
        try:
            WebDriverWait(self.driver, 10, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "olpOfferList")))
            OfferLists = self.driver.find_elements_by_class_name("olpOffer")
            for item in OfferLists:
                if SelectBy == 'Price':
                    if OrderPrice in item.find_element_by_class_name("olpOfferPrice").text:
                        item.find_element_by_class_name('a-button-input').click()
                        break
                if SelectBy == 'Seller':
                    if Seller in item.find_element_by_class_name("olpSellerName").text:
                        item.find_element_by_class_name('a-button-input').click()
                        break
        except:
            pass
        # affirm in user's cart
        try:
            WebDriverWait(self.driver, 10, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "huc-v2-order-row-confirm-text")))
            self.driver.find_element_by_id('huc-v2-order-row-confirm-text')
            print("Added to cart ...")
            return True
        except:
            print("Not added to cart ...")
            return False

    def AddCartByButton(self):
        try:
            AddCartButton = self.driver.find_element_by_id('add-to-cart-button')
            self.ClickElement(AddCartButton)
            True
        except:
            return False

    def AddCart(self,asin, OrderPrice, Seller = 'NotInput', SelectBy = 'Price'):
        if not self.SelectAsinFromBuyBox(asin):
            return False
        if self.GoOfferList() and self.AddCartByOfferList(OrderPrice, Seller, SelectBy):
            return True
        if self.AddCartByButton():
            return True
        return False


    def SearchProduct(self, Info, PageNum = 20, ClickProduct =True):
        try:
            WebDriverWait(self.driver, 10, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "nav-search")))
        except:
            print('No search bar!')
            return False
        if not self.SubmitDepartment(Info['department']):
            return False
        if not self.SubmitKeyword(Info['keyword']):
            return False
        self.ViewWholePage(ScrollSpeed=[30, 60])
        if not self.SetPrice(Info['lowprice'], Info['highprice']):
            return False
        for i in range(PageNum):
            self.ViewWholePage(ScrollSpeed=[30, 60])
            self.ViewOtherProduct(asin=Info['asin'])
            self.ViewOtherProduct(asin=Info['asin'])
            self.speed = randint(30, 60)
            if self.FindProduct(asin=Info['asin'], ClickProduct=ClickProduct):
                return True
            if not self.GoToNextPage():
                return False

    def SearchAndView(self, Info):
        if not self.SearchProduct(Info):
            return False
        if not self.ViewOurProduct(timeout=600):
            return False
        #self.ViewOtherProduct(asin=Info['asin'])
        return True