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
from AmazonTables import SMatch


chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
class AmazonFunction(page_scroll):
    def __init__(self, driver, FunctionInfo={}):
        self.driver = driver
        self.FunctionInfo = FunctionInfo
        self.rank = '0'
        self.time_found = datetime.now()
        self.max_search_pages = 20
        self.speed = 100  # page scroll speed
        self.proxy = ''
        self.start_time = datetime.now()
        self.timeout_time = 1200
        self.SearchOnly = False
        self.VerifyEnhance = True
        self.NewRandomAccount = True
        self.domain_url = {'us': 'https://www.amazon.com/',
                           'ca': 'https://www.amazon.ca/',
                           'uk': 'https://www.amazon.co.uk/'}
        self.captcha = CaptchaUpload('f4ab06a8e3e5be77134312d55c7a7bb4')
        self.Replace = re.compile('[ \.:#,-]')

    def probability_to_do(self, probability):
        if random.random() <= probability:
            return True
        else:
            return False

    def back_to_page(self, url):
        # noinspection PyBroadException
        if self.driver.current_url != url:
            try:
                if not self.check_captch():
                    print('Try to go back')
                    self.driver.get(url)
            except:
                print('Try to go back fail')

    def set_price_interval(self, lowprice='0', highprice='0'):
        # change price interval
        try:
            if float(lowprice) > float(highprice):
                exchange_price = lowprice
                lowprice = highprice
                highprice = exchange_price
        except:
            print("search without price...")
            return True

        if highprice != '0':
            # noinspection PyBroadException
            try:
                WebDriverWait(self.driver, 30, 0.5, ignored_exceptions=TimeoutException)\
                    .until(EC.visibility_of_element_located((By.ID, 'low-price')))
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

    def submit_department(self):
        # select department
        # noinspection PyBroadException
        try:
            department_element = self.driver.find_element_by_id('searchDropdownBox')
            self.ScrollToElement(department_element)
            select = Select(department_element)
            select.select_by_visible_text(self.FunctionInfo['department'])
            return True
        except:
            print("department submit fail!")
            return False

    def submit_keyword(self, keyword=None):
        self.FunctionInfo['errorcode'] = 'SearchStart'
        # check keyword existing
        if keyword is None:
            print("I can't work without ketwords")
            return False
        # submit keyword
        # noinspection PyBroadException
        try:
            WebDriverWait(self.driver, 30, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.element_to_be_clickable((By.ID, 'nav-search')))
            search_box = self.driver.find_element_by_id("twotabsearchtextbox")
            self.ScrollToElement(search_box)
            search_box.clear()
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)
            return True
        except:
            print("keyword submit fail")
            return False

    def SearchProduct(self):
        if self.timeout_error():
            self.FunctionInfo['errorcode'] = 'SearchTimeout'
            self.FunctionInfo['status'] = False
            return False
        self.submit_department()
        # return when keyword error
        if self.submit_keyword(self.FunctionInfo['keyword']) is False:
            self.FunctionInfo['errorcode'] = 'SearchKeywordFail'
            self.FunctionInfo['status'] = False
            return False

        set_price_status = self.set_price_interval(self.FunctionInfo['lowprice'], self.FunctionInfo['highprice'])

        # scroll screen and turn pages to search
        page_number = 1
        while page_number <= self.max_search_pages:
            if self.timeout_error():
                self.FunctionInfo['errorcode'] = 'SearchTimeout'
                self.FunctionInfo['status'] = False
                return False
            # noinspection PyBroadException
            try:
                WebDriverWait(self.driver, 30, 0.5, ignored_exceptions=TimeoutException) \
                    .until(EC.visibility_of_element_located((By.ID, 'pagn')))
                page_element = self.driver.find_element_by_id('pagn')
                self.ScrollToElement(page_element)
                #production_element = self.driver.find_element_by_xpath("//*[@data-asin='" + self.FunctionInfo['asin'] + "']")
                #self.rank = (production_element.get_attribute("id")).split("_")[1]
                #self.ScrollToElement(production_element)
                #time.sleep(2)
                #production_hrefs = production_element.find_elements_by_xpath("//*[@href]")
                production_hrefs = self.driver.find_elements_by_xpath("//*[@href]")
                for production_href in production_hrefs:
                    production_url = production_href.get_attribute("href")
                    if ('dp/' + self.FunctionInfo['asin']) in production_url:
                        self.time_found = datetime.now()
                        if self.SearchOnly:
                            print('Production found!')
                            self.FunctionInfo['errorcode'] = 'SearchFound'
                            self.FunctionInfo['status'] = True
                            return production_url
                        else:
                            self.driver.get(production_url)
                            time.sleep(5)
                            print('Production found!')
                            self.FunctionInfo['errorcode'] = 'SearchClickDone'
                            self.FunctionInfo['status'] = True
                            return production_url
            except :
                print('Production info parse error：' + self.FunctionInfo['asin'])
                print(traceback.print_exc())
                self.FunctionInfo['errorcode'] = 'SearchParseError'
                self.FunctionInfo['status'] = False
                return False
            # noinspection PyBroadException
            try:
                WebDriverWait(self.driver, 30, 0.5, ignored_exceptions=TimeoutException) \
                    .until(EC.element_to_be_clickable((By.ID, 'pagnNextLink')))
                next_page = self.driver.find_element_by_id("pagnNextLink")
            except:
                print('All page checked but not found：' + self.FunctionInfo['asin'])
                #print(traceback.print_exc())
                self.FunctionInfo['errorcode'] = 'SearchNoFound'
                self.FunctionInfo['status'] = False
                return False

            # noinspection PyBroadException
            try:
                self.ScrollToElement(next_page)
                self.ClickElement(next_page)
                time.sleep(1)
                if set_price_status is False:
                    set_price_status = self.set_price_interval(self.FunctionInfo['lowprice'], self.FunctionInfo['highprice'])
            except:
                print('Turn page fail...' + self.FunctionInfo['asin'])
                self.FunctionInfo['errorcode'] = 'SearchTurnPageFail'
                self.FunctionInfo['status'] = False
                return False
            page_number += 1

        print('''
        search fail in the first %d pages with:
        department : %s
        keyword    : %s
        low  price : %s
        high price : %s
        ''' % (self.max_search_pages, self.FunctionInfo['department'], self.FunctionInfo['keyword'], self.FunctionInfo['lowprice'], self.FunctionInfo['highprice']))
        self.FunctionInfo['errorcode'] = 'SearchEnoughPages'
        self.FunctionInfo['status'] = False
        return False

    def stay_time(self):
        if self.time_found:
            return (datetime.now() - self.time_found).seconds
        else:
            return 0

    def view_thumbnail(self):
        # noinspection PyBroadException
        try:
            WebDriverWait(self.driver, 10, 0.5, ignored_exceptions=TimeoutException)\
                .until(EC.visibility_of_element_located((By.ID, 'altImages')))
            thumbnail = self.driver.find_element_by_id('altImages')
            self.ScrollToElement(thumbnail)
            sub_thumbnails = thumbnail.find_elements_by_xpath(
                '//*[@class="a-spacing-small item imageThumbnail a-declarative"]')
            #sub_thumbnails = thumbnail.find_elements_by_tag_name('img')
            ttt = len(sub_thumbnails)
            for i in range(len(sub_thumbnails)):
                if self.probability_to_do(0.8):
                    ActionChains(self.driver).move_to_element(sub_thumbnails[i]).perform()
                    time.sleep(1)
            return True
        except:
            print('Error happen when view thumbnail!')
            return False

    def ViewAllPage(self):
        # noinspection PyBroadException
        try:
            WebDriverWait(self.driver, 30, 0.5, ignored_exceptions=TimeoutException)\
                .until(EC.visibility_of_element_located((By.ID, 'navBackToTop')))
            back_to_top = self.driver.find_element_by_id('navBackToTop')
            self.ScrollToElement(back_to_top)
            self.ClickElement(back_to_top)
            return True
        except :
            print('View all fail!' + str(datetime.now()))
            return False

    def view_reviewer(self):
        # noinspection PyBroadException
        try:
            reviewer_header = self.driver.find_element_by_id('cm-cr-dp-review-header')
            reviewer_footer = self.driver.find_element_by_id("reviews-medley-footer")
            self.ScrollToElement(reviewer_header)
        except :
            print('Scroll to reviewer failed...')
            pass

        # noinspection PyBroadException
        try:
            reviewer_list = self.driver.find_element_by_id('cr-lighthut-1-').find_elements_by_tag_name("a")
        except:
            print('No reviewer yet...')
            return True

        # noinspection PyBroadException
        try:
            reviewer_summary = self.driver.find_element_by_id('reviewSummary')
            for i in range(len(reviewer_list)):
                if self.probability_to_do(0.4):
                    self.ScrollToElement(reviewer_summary)
                    self.ClickElement(reviewer_list[i])
                    time.sleep(2)
                    self.ScrollToElement(reviewer_footer)
            return True
        except:
            print('Error happen when view reviewer!')
            return False

    def view_detail_answer(self):
        # noinspection PyBroadException
        try:
            QandA_zone = self.driver.find_element_by_id("ask_lazy_load_div")
            self.ScrollToElement(QandA_zone)
            detail_answers = QandA_zone.find_elements_by_link_text('see more')
            for i in range(len(detail_answers)):
                if self.probability_to_do(0.4):
                    self.ScrollToElement(detail_answers[i])
                    self.ClickElement(detail_answers[i])
                    time.sleep(1)
            return True
        except:
            print('Error happen when view detail answers!')
            return False

    def view_more_answer(self):
        # noinspection PyBroadException
        try:
            QandA_zone = self.driver.find_element_by_id("ask_lazy_load_div")
            self.ScrollToElement(QandA_zone)
            more_answers = QandA_zone.find_elements_by_partial_link_text('See more answers')
            for i in range(len(more_answers)):
                if self.probability_to_do(0.4):
                    self.ScrollToElement(more_answers[i])
                    self.ClickElement(more_answers[i])
                    time.sleep(2)
            return True
        except:
            print('Error happen when view more answers!')
            return False

    def view_more_question(self, url):
        # noinspection PyBroadException
        try:
            QandA_zone = self.driver.find_element_by_id("ask_lazy_load_div")
            self.ScrollToElement(QandA_zone)
            question_texts = BeautifulSoup(self.driver.page_source, "lxml"). \
                find_all(id=re.compile('question-[0-9a-zA-Z]*'))
            question_ids = []
            for question_text in question_texts:
                question_ids.append(question_text.get("id"))
            for i in range(len(question_ids)):
                if self.probability_to_do(0.4):
                    selected_question = self.driver.find_element_by_id(question_ids[i])
                    self.ScrollToElement(selected_question)
                    #self.ClickElement(selected_question)
                    selected_question.click()
                    if self.driver.current_url != url:
                        time.sleep(5)
                        self.driver.back()
                    if self.driver.current_url != url:
                        self.driver.get(url)
            return True
        except:
            print('Error happen when view more questions!')
            return False

    def add_to_cart(self):
        try:
            if self.probability_to_do(0.05):
                WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException)\
                    .until(EC.element_to_be_clickable((By.ID, 'add-to-cart-button')))
                cart_elemnt = self.driver.find_element_by_id("add-to-cart-button")
                cart_elemnt.click()
                print('Added to cart...')
                time.sleep(10)
                self.driver.back()
            return True
        except:
            print('add to cart fail...')
            return False

    def click_to_select(self):
        # noinspection PyBroadException
        try:
            select_zone = self.driver.find_element_by_id("centerCol")
            self.ScrollToElement(select_zone)
            select_titles = BeautifulSoup(self.driver.page_source, "lxml"). \
                find_all(title=re.compile('Click to select .+'))
            select_options = []
            for select_title in select_titles:
                select_options.append(select_title.get("id"))
            for i in range(len(select_options)):
                if self.probability_to_do(0.6):
                    select_option = self.driver.find_element_by_id(select_options[i])
                    self.ScrollToElement(select_option)
                    select_option.click()
                    time.sleep(3)
            return True
        except:
            print('Error happen when select and click!')
            return False

    def check_captch(self):
        CaptchInPage = False
        try:
            if self.driver.find_element_by_xpath("//input[@id='auth-captcha-guess']"):
                CaptchInPage = True
        except: pass

        RandomName = str(randint(100, 999))

        if "Robot Check" in self.driver.title:
            print('Robot Check test ' )
            print(self.driver.page_source)
            try:
                WebDriverWait(self.driver, 10, 0.5, ignored_exceptions=TimeoutException) \
                    .until(EC.visibility_of_element_located((By.TAG_NAME, 'img')))
                image = self.driver.find_element_by_tag_name('img').get_attribute('src')
                request.urlretrieve(image, "./logs/" + RandomName + ".jpg")
                time.sleep(5)
                captcha_answer = self.captcha.solve("./logs/" + RandomName + ".jpg")
                search = self.driver.find_element_by_xpath("//input[@id='captchacharacters']")
                search.clear()
                search.send_keys(captcha_answer)
                self.driver.find_element_by_xpath("//button[@type='submit']").click()
                time.sleep(5)
            except:
                print('Error when loading image for captch...')
                print(traceback.print_exc())
            finally:
                os.system("rm " + "./logs/" + RandomName + ".jpg")
            if "Robot Check" not in self.driver.title:
                print('check captch done!')
                return True
            else:
                print('check captch fail!!')
                return False

        if CaptchInPage:
            try:
                images = self.driver.find_element_by_id("auth-captcha-image")
                CapthUrl = images.get_attribute('src')
                request.urlretrieve(CapthUrl, "./logs/" + RandomName + ".jpg")
                time.sleep(5)
                answer = self.captcha.solve("./logs/" + RandomName + ".jpg")
                self.driver.find_element_by_id("auth-captcha-guess").click()
                self.driver.find_element_by_id("auth-captcha-guess").clear()
                self.driver.find_element_by_id("auth-captcha-guess").send_keys(answer)
                try: self.driver.find_element_by_id("cnep_1B_submit_button").click()
                except: pass
                try: self.driver.find_element_by_id('signInSubmit').click()
                except: pass
                try: self.driver.find_element_by_id('continue').click()
                except: pass
            except:
                print('check captch fail 0!')
                #print(traceback.print_exc())
            finally:
                os.system("rm " + "./logs/" + RandomName + ".jpg")
            try:
                time.sleep(5)
                self.driver.find_element_by_xpath("//input[@id='auth-captcha-guess']")
                print('check captch fail 1!!')
                return False
            except:
                print('check captch done!')
                return True

        return True

    def timeout_error(self):
        if int((datetime.now() - self.start_time).seconds) > self.timeout_time:
            print('function Time out....')
            return True
        if not self.check_captch():
            print('function captch check not pass....' + str(datetime.now()))
            return True
        return False

    def check_price(self, url):
        price_element = ''
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 60, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located
                                   ((By.CSS_SELECTOR, "#priceblock_ourprice, #priceblock_saleprice, #olp_feature_div")))
        except:
            print('Price url error0:::' + str(datetime.now()))

        if not self.check_captch():
            print('Captcha not pass when check price....')
            return

        try:
            price_element = self.driver.find_element_by_id('priceblock_ourprice')
        except:
            pass

        if not price_element:
            try:
                price_element = self.driver.find_element_by_id('priceblock_saleprice')
            except:
                pass

        if not price_element:
            try:
                price_element = self.driver.find_element_by_id('olp_feature_div')
            except:
                pass
        try:
            lowprice = re.findall('[\$£][ 0-9\.]+', price_element.text)
            lowprice = list(filter(lambda x : x != '', re.split('[\$£ ]+', lowprice[0])))[0]
            highprice = str(round((float(lowprice) + 0.01),2))
            #lowprice = str(round((float(lowprice)),0))
            price = [lowprice, highprice]
            return price
        except:
            print('Price url error1:::' + str(datetime.now()))
            return False

    def login(self):
        try: self.driver.get("https://www.amazon.com/")
        except: pass
        time.sleep(10)
        if self.FunctionInfo['cookies']:
            try:
                self.driver.delete_all_cookies()
                for cookie in json.loads(self.FunctionInfo['cookies']):
                    self.driver.add_cookie(cookie)
            except:
                print('Login: unable to set cookie')
                # print(traceback.print_exc())
                self.FunctionInfo['errorcode'] = 'CookieSetFail'
                self.FunctionInfo['status'] = False
                return False
            self.driver.get("https://www.amazon.com/")
            time.sleep(5)
        try:
            self.driver.get("https://www.amazon.com/gp/your-account/order-history?ref_=ya_d_c_yo")
        except:
            print('Loggin: Fail because Net...')
            self.FunctionInfo['errorcode'] = 'LogginNetFail'
            self.FunctionInfo['status'] = False
            return False

        if not self.check_captch():
            print('Loggin: Fail because of captch...')
            self.FunctionInfo['errorcode'] = 'CookieCaptchError'
            self.FunctionInfo['status'] = False
            return False

        # Login after editting cookie
        try:
            WebDriverWait(self.driver, 10, 0.5, ignored_exceptions=TimeoutException).until(EC.title_contains('Your Orders'))
            print('Login succeeded!!! 0')
            self.FunctionInfo['errorcode'] = 'LoginPass0'
            self.FunctionInfo['status'] = True
            return True
        except:
            print('Login: password shall be input.')

        # Login in by password only
        try:
            self.driver.find_element_by_class_name("cvf-account-switcher-claim").click()
        except:
            pass
        try:
            #self.driver.find_element_by_xpath("//div[contains(text(),'" + self.FunctionInfo['username'] + "')]").click()
            #self.driver.find_element_by_xpath("//input[@name='rememberMe']").click()
            self.driver.find_element_by_id("ap_password").send_keys(self.FunctionInfo['password'])
            self.driver.find_element_by_id("signInSubmit").click()
        except: pass
        try:
            WebDriverWait(self.driver, 10, 0.5, ignored_exceptions=TimeoutException).until(
                EC.title_contains('Your Orders'))
            print('Login succeeded!!! 1')
            self.FunctionInfo['errorcode'] = 'LoginPass1'
            self.FunctionInfo['status'] = True
            return True
        except:
            print('Login: account shall be changed.')

        # Login by username & password
        try:
            self.driver.find_element_by_id("ap_switch_account_link").click()
        except:
            pass

        try:
            self.driver.find_element_by_id("cvf-account-switcher-add-accounts-link").click()
        except:
            pass

        # input Email
        try:
            self.driver.find_element_by_id("ap_email").send_keys(self.FunctionInfo['username'])
        except:
            print("Login: email input error...")
            self.FunctionInfo['errorcode'] = 'EmailSubmitFail'
            self.FunctionInfo['status'] = False
            #return False
        try: self.driver.find_element_by_xpath('//input[@id="continue"]').click()
        except: pass
        # check bad email
        try:
            WebDriverWait(self.driver, 10, 0.5, ignored_exceptions=TimeoutException).until(
                EC.visibility_of_element_located((By.ID, 'auth-error-message-box')))
            print('Login: We cannot find an account with that email address')
            self.FunctionInfo['errorcode'] = 'BadEmail'
            self.FunctionInfo['status'] = False
            return False
        except:
            pass

        # input Password
        try:
            self.driver.find_element_by_id("ap_password").send_keys(self.FunctionInfo['password'])
            self.driver.find_element_by_id("signInSubmit").click()
        except:
            print('Login: Fail to submit password.')
            self.FunctionInfo['errorcode'] = 'PasswordSubmitFail'
            self.FunctionInfo['status'] = False
            #return False

        # Use otp verification Code for login
        if self.VerifyEnhance:
            try:
                if 'Important Message!' in self.driver.find_element_by_xpath("//h4[@class='a-alert-heading']").text:
                    self.driver.find_element_by_id('auth-login-via-otp-btn').click()
            except:
                #print(traceback.print_exc())
                pass
            try:
                WebDriverWait(self.driver, 10, 0.5, ignored_exceptions=TimeoutException).until(
                    EC.visibility_of_element_located((By.ID, 'auth-login-via-otp-btn')))
                self.driver.find_element_by_id('auth-login-via-otp-btn').click()
            except:
                #print(traceback.print_exc())
                pass

        # Send Verification code
        try:
            WebDriverWait(self.driver, 10, 0.5, ignored_exceptions=TimeoutException).until(
                EC.visibility_of_element_located((By.ID,'cvf-page-content')))
            SenfCodeBtn = self.driver.find_element_by_class_name('cvf-widget-btn')
            if 'Send code' in SenfCodeBtn.text:
                SenfCodeBtn.click()
                time.sleep(3)
        except:
            #print(traceback.print_exc())
            pass
        try:
            if self.driver.find_element_by_class_name('cvf-widget-input-code'):
                time.sleep(60)
                verifycode = getverifycode(self.FunctionInfo['username'], self.FunctionInfo['password'])
                Entercode = self.driver.find_element_by_class_name('cvf-widget-input-code')
                Entercode.click()
                Entercode.send_keys(verifycode)
                self.driver.find_element_by_class_name('cvf-widget-btn-verify').click()
                time.sleep(3)
        except:
            #print(traceback.print_exc())
            pass

        self.check_captch()
        # re-input Password and check
        try:
            self.driver.find_element_by_id("ap_password").send_keys(self.FunctionInfo['password'])
            self.driver.find_element_by_id("signInSubmit").click()
        except:
            pass

        try:
            if self.driver.find_element_by_id('auth-error-message-box'):
                print('Login: Your password is incorrect')
                self.FunctionInfo['errorcode'] = 'BadPassword'
                self.FunctionInfo['status'] = False
                return False
        except:
            pass

        try:
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException). \
                until(EC.title_contains('Your Orders'))
            print('Login succeeded!!! 2')
            self.FunctionInfo['errorcode'] = 'LoginPass2'
            self.FunctionInfo['status'] = True
            time.sleep(5)
            return True
        except:
            print('Login: Fail after Email and password ' + self.FunctionInfo['username'] + ' : ' + self.FunctionInfo['password'])
            self.FunctionInfo['errorcode'] = 'Email&PasswordFail'
            self.FunctionInfo['status'] = False
            return False


    def SecurityPage(self):
        try:
            self.driver.get("https://www.amazon.com/gp/css/homepage.html/ref=nav_youraccount_btn")
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException). \
                until(EC.visibility_of_element_located((By.XPATH, "//div[@data-card-identifier='SignInAndSecurity']")))
            self.driver.find_element_by_xpath("//div[@data-card-identifier='SignInAndSecurity']").click()
        except:
            print('ChangeEmail: fail to view security page')
            print(traceback.print_exc())
            self.FunctionInfo['errorcode'] = 'PageViewFail'
            self.FunctionInfo['status'] = False
            return False
        try:
            self.driver.find_element_by_xpath("//input[@id='ap_password']").send_keys(self.FunctionInfo['password'])
            self.driver.find_element_by_xpath("//input[@id='signInSubmit']").click()
        except:
            pass
        print('View security page')
        self.FunctionInfo['errorcode'] = 'PageViewPass'
        self.FunctionInfo['status'] = True
        return True

    def AddCreditCard(self):
        try:
            self.driver.get("https://www.amazon.com/gp/css/homepage.html/ref=nav_youraccount_btn")
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException). \
                until(EC.visibility_of_element_located((By.XPATH, "//div[@data-card-identifier='PaymentOptions']")))
            self.driver.find_element_by_xpath("//div[@data-card-identifier='PaymentOptions']").click()
        except:
            print('Add Credit card: fail to view payment page')
            #print(traceback.print_exc())
            self.FunctionInfo['errorcode'] = 'PaymentViewFail'
            self.FunctionInfo['status'] = False
            return False
        try:
            self.driver.find_element_by_xpath("//input[@id='ap_password']").send_keys(self.FunctionInfo['password'])
            self.driver.find_element_by_xpath("//input[@id='signInSubmit']").click()
        except:
            pass

        #delete old card
        try:
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException). \
                until(EC.visibility_of_element_located((By.ID, "walletWebsiteContentColumn")))
        except: pass
        while True:
            try: CardFound = self.driver.find_element_by_class_name('pmts-instrument-display-name')
            except: CardFound = False
            if CardFound:
                try:
                    CardFound.click()
                    #CardEdit = self.driver.find_element_by_class_name('pmts-instrument-list-item-expander-content')
                    DeleteCard = self.driver.find_element_by_class_name("pmts-instrument-list-item-button-js")
                    DeleteCard.click()
                    time.sleep(5)
                except:
                    print('CreditCardAdd: fail to delete card')
                    print(traceback.print_exc())
                    self.FunctionInfo['errorcode'] = 'CreditCardDeleteFail'
                    self.FunctionInfo['status'] = False
                    return False
                try:
                    self.driver.find_element_by_class_name('pmts-delete-instrument').click()
                    self.ClickElement(self.driver.find_element_by_class_name('pmts-delete-instrument'))
                    time.sleep(1)
                    self.driver.refresh()
                    time.sleep(5)
                except:
                    #print(traceback.print_exc())
                    pass
            else:
                try:self.driver.refresh()
                except: pass
                break

        # add new card
        try:
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException). \
                until(EC.visibility_of_element_located((By.ID, "walletWebsiteContentColumn")))
            if not self.driver.find_element_by_xpath("//div[contains(text(),'Enter your card information:')]").is_displayed():
                self.driver.find_element_by_xpath("//span[contains(text(),'Add a card')]").click()
            self.driver.find_element_by_xpath("//input[@name='ppw-accountHolderName']").send_keys(self.FunctionInfo['nameoncard'])
            self.driver.find_element_by_xpath("//input[@name='addCreditCardNumber']").send_keys(self.FunctionInfo['ccnumber'])
            select = Select(self.driver.find_element_by_xpath("//select[@name='ppw-expirationDate_month']"))
            select.select_by_visible_text(self.FunctionInfo['ccmonth'])
            select = Select(self.driver.find_element_by_xpath("//select[@name='ppw-expirationDate_year']"))
            select.select_by_visible_text(self.FunctionInfo['ccyear'])
            AddCardButton = self.driver.find_element_by_xpath("//input[@name='ppw-widgetEvent:AddCreditCardEvent']")
            self.move_to_element(AddCardButton)
            AddCardButton.click()
        except:
            print('CreditCardAdd: fail to add new card')
            print(traceback.print_exc())
            self.FunctionInfo['errorcode'] = 'CreditCardAddFail'
            self.FunctionInfo['status'] = False
            return False

        # set billing address
        try:
            WebDriverWait(self.driver, 15, 0.5, ignored_exceptions=TimeoutException). \
                until(EC.visibility_of_element_located((By.CLASS_NAME, "pmts-add-address")))
            AddAddress = self.driver.find_element_by_xpath('//input[@name="ppw-widgetEvent:ShowAddAddressEvent"]')
            self.ClickElement(AddAddress)
            time.sleep(2)
        except:
            #print(traceback.print_exc())
            pass

        try:
            self.driver.find_element_by_class_name('pmts-use-this-address').click()
        except:
            pass

        try:
            WebDriverWait(self.driver, 5, 0.5, ignored_exceptions=TimeoutException). \
                until(EC.visibility_of_element_located((By.ID, "fullName")))
            fullname = self.driver.find_element_by_xpath("//input[@name='ppw-fullName']")
            fullname.clear()
            fullname.send_keys(self.FunctionInfo['fullname'])
            self.driver.find_element_by_xpath("//input[@name='ppw-line1']").send_keys(self.FunctionInfo['address'])
            self.driver.find_element_by_xpath("//input[@name='ppw-city']").send_keys(self.FunctionInfo['city'])
            self.driver.find_element_by_xpath("//input[@name='ppw-stateOrRegion']").send_keys(self.FunctionInfo['state'])
            self.driver.find_element_by_xpath("//input[@name='ppw-postalCode']").send_keys(self.FunctionInfo['postalcode'])
            self.driver.find_element_by_xpath("//input[@name='ppw-phoneNumber']").send_keys(self.FunctionInfo['phonenumber'])
            UseAddress = self.driver.find_element_by_xpath("//input[@name='ppw-widgetEvent:AddAddressEvent']")
            self.move_to_element(UseAddress)
            UseAddress.click()
        except:
            print('CreditCardAdd: fail to set billing address')
            print(traceback.print_exc())
            self.FunctionInfo['errorcode'] = 'BillAddresssetFail'
            self.FunctionInfo['status'] = False
            return False

        # No use Original address
        try:
            self.ClickElement(self.driver.find_element_by_xpath('//input[@name="ppw-widgetEvent:UseOriginalAddressEvent"]'))
        except:
            pass

        try:
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException). \
                until(EC.visibility_of_element_located((By.CLASS_NAME, "pmts-instrument-display-name")))
            print('Credit Card Add pass')
            self.FunctionInfo['errorcode'] = 'CreditCardPass'
            self.FunctionInfo['status'] = True
            return True
        except:
            print('CreditCardAdd: fail to set default payment!')
            print(traceback.print_exc())
            self.FunctionInfo['errorcode'] = 'DefaultPaymentFail'
            self.FunctionInfo['status'] = False
            return False

    def ChangeEmail(self, EmailDomain = '@foxairmail.com'):
        self.FunctionInfo['errorcode'] = 'ChangeEmailstart'
        self.FunctionInfo['status'] = False
        NewEmail = names.get_first_name() + names.get_last_name() + str(randint(0, 999)) + EmailDomain
        print('ChangeEmail: new eMail is ' + NewEmail + ' == Original: ' + self.FunctionInfo['username'])
        self.FunctionInfo['newemail'] = NewEmail
        try:
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException). \
                until(EC.visibility_of_element_located((By.ID,"auth-cnep-edit-email-button")))
            self.driver.find_element_by_id("auth-cnep-edit-email-button").click()
            self.driver.find_element_by_id("ap_email_new").click()
            self.driver.find_element_by_id("ap_email_new").clear()
            self.driver.find_element_by_id("ap_email_new").send_keys(NewEmail)
            self.driver.find_element_by_id("ap_email_new_check").clear()
            self.driver.find_element_by_id("ap_email_new_check").send_keys(NewEmail)
            self.driver.find_element_by_id("ap_password").clear()
            self.driver.find_element_by_id("ap_password").send_keys(self.FunctionInfo['password'])
        except:
            print('ChangeEmail: fail to submit new eMail')
            self.FunctionInfo['errorcode'] = 'EmailSubmitFail'
            self.FunctionInfo['status'] = False
            return False

        if not self.check_captch():
            print('ChangeEmail: Captch Fail')
            self.FunctionInfo['errorcode'] = 'ChangeEmailCaptchFail'
            self.FunctionInfo['status'] = False
            return False

        try:
            self.driver.find_element_by_id('auth-error-message-box')
            print('Please check that your e-mail addresses match and try again.')
            print('ChangeEmail: eMail no match')
            self.FunctionInfo['errorcode'] = 'ChangeEmailNoMatch'
            self.FunctionInfo['status'] = False
            return False
        except:
            pass

        try:
            self.driver.find_element_by_xpath("//h4[text()='Success']")
            print('Change eMail succeeded')
            self.FunctionInfo['errorcode'] = 'ChangeEmailPass'
            self.FunctionInfo['status'] = True
            return True
        except:
            print('Fail to change eMail as last step...')
            self.FunctionInfo['errorcode'] = 'ChangeEmailEndFail'
            self.FunctionInfo['status'] = False
            return False

    def ChangePassword(self):
        self.FunctionInfo['errorcode'] = 'ChangePosswordstart'
        self.FunctionInfo['status'] = False
        NewPassword = ''.join(random.sample(chars, 10))
        print('ChangePassword: new password is ' + NewPassword + ' == Original: ' + self.FunctionInfo['password'])
        self.FunctionInfo['newpassword'] = NewPassword
        try:
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException). \
                until(EC.visibility_of_element_located((By.ID,"auth-cnep-edit-password-button")))
            self.driver.find_element_by_id("auth-cnep-edit-password-button").click()
            self.driver.find_element_by_id("ap_password").clear()
            self.driver.find_element_by_id("ap_password").send_keys(self.FunctionInfo['password'])
            self.driver.find_element_by_id("ap_password_new").clear()
            self.driver.find_element_by_id("ap_password_new").send_keys(NewPassword)
            self.driver.find_element_by_id("ap_password_new_check").clear()
            self.driver.find_element_by_id("ap_password_new_check").send_keys(NewPassword)
            self.driver.find_element_by_id("cnep_1D_submit_button").click()
        except:
            print('ChangePassword: fail to submit new Password')
            self.FunctionInfo['errorcode'] = 'PWDSubmitFail'
            self.FunctionInfo['status'] = False
            return False

        if not self.check_captch():
            print('ChangePassword: Captch Fail')
            self.FunctionInfo['errorcode'] = 'ChangePWDCaptchFail'
            self.FunctionInfo['status'] = False
            return False

        try:
            self.driver.find_element_by_xpath("//h4[text()='Success']")
            print('Change Password succeeded')
            self.FunctionInfo['errorcode'] = 'ChangePWDlPass'
            self.FunctionInfo['status'] = True
            return True
        except:
            print('Fail to change password as last step...')
            self.FunctionInfo['errorcode'] = 'ChangePWDEndFail'
            self.FunctionInfo['status'] = False
            return False

    def CleanCart(self):
        self.FunctionInfo['status'] = False
        try: self.driver.get("https://www.amazon.com/gp/cart/view.html/ref=nav_cart")
        except: pass
        try:
            WebDriverWait(self.driver, 10, 0.5, ignored_exceptions=TimeoutException). \
                until(EC.visibility_of_element_located((By.XPATH, "//input[@value='Delete']")))
            Delete_element = self.driver.find_element_by_xpath("//input[@value='Delete']")
            while Delete_element:
                Delete_element.click()
                time.sleep(5)
                Delete_element = self.driver.find_element_by_xpath("//input[@value='Delete']")
        except:
            pass
        try:
            if 'Your Shopping Cart is empty.' in self.driver.find_element_by_id("sc-active-cart").text:
                print('Cart clean done.')
                self.FunctionInfo['errorcode'] = 'EmptyCartPass'
                self.FunctionInfo['status'] = True
                return True
        except:
            print('Cart clean fail...')
            self.FunctionInfo['errorcode'] = 'EmptyCartFail'
            self.FunctionInfo['status'] = False
            return False

    def SetAddress(self):
        self.FunctionInfo['status'] = False
        self.FunctionInfo['errorcode'] = 'AddressSetStart'
        try:
            time.sleep(2)
            self.driver.get("https://www.amazon.com/a/addresses?ref_=ya_d_c_addr")
            time.sleep(2)
        except:
            pass
        try:
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "ya-myab-address-add-link")))
        except:
            print('Address set: fail to address book!!')
            self.FunctionInfo['errorcode'] = 'AddressViewFail'
            self.FunctionInfo['status'] = False
            return False

        AllAddressText = ''
        try:
            AddressElements = self.driver.find_elements_by_class_name("normal-desktop-address-tile")
        except:
            AddressElements = ''
        for item in AddressElements:
            try:
                AllAddressText += self.Replace.sub(repl='',string=item.text.lower())
            except:
                pass

        # select country for address
        # add new address
        print('Address set: start to add address')
        if not SMatch(self.Replace.sub(repl='',string=self.FunctionInfo['fullname'].lower()), AllAddressText) or \
            not SMatch(self.Replace.sub(repl='',string=self.FunctionInfo['address'].lower()), AllAddressText) or \
            not SMatch(self.Replace.sub(repl='',string=self.FunctionInfo['phonenumber']), AllAddressText):
            try:
                self.driver.find_element_by_id('ya-myab-address-add-link').click()
                #self.driver.get("https://www.amazon.com/a/addresses/add?ref=ya_address_book_add_button")
                WebDriverWait(self.driver, 30, 0.5, ignored_exceptions=TimeoutException) \
                    .until(EC.visibility_of_element_located((By.ID, "address-ui-address-form")))
                #Select(self.driver.find_element_by_id("address-ui-widgets-countryCode-dropdown-nativeId")).\
                #    select_by_visible_text(self.FunctionInfo['country'])
                self.driver.find_element_by_id("address-ui-widgets-enterAddressFullName").send_keys(
                    self.FunctionInfo['fullname'])
                self.driver.find_element_by_id("address-ui-widgets-enterAddressLine1").send_keys(
                    self.FunctionInfo['address'])
                self.driver.find_element_by_id("address-ui-widgets-enterAddressCity").send_keys(
                    self.FunctionInfo['city'])
                self.driver.find_element_by_id("address-ui-widgets-enterAddressStateOrRegion").send_keys(self.FunctionInfo['state'])
                self.driver.find_element_by_id("address-ui-widgets-enterAddressPostalCode").send_keys(self.FunctionInfo['postalcode'])
                self.driver.find_element_by_id("address-ui-widgets-enterAddressPhoneNumber").send_keys(self.FunctionInfo['phonenumber'])
                #self.driver.find_element_by_class_name("a-button-input").click()
                self.ClickElement(self.driver.find_element_by_class_name("a-button-input"))
                time.sleep(5)
            except:
                print('Adding New Address fail...')
                self.FunctionInfo['errorcode'] = 'AddressAddFail'
                self.FunctionInfo['status'] = False
                print(traceback.print_exc())
                return False
            # confirm if review address
            try:
                if 'Review your address' in self.driver.find_element_by_xpath("//h4[@class='a-alert-heading']").text:
                    self.driver.find_element_by_class_name("a-button-input").click()
                    print('Address setting is double confirmed...')
            except:
                pass
            # check if address is valid
            try:
                if self.driver.find_element_by_id("address-ui-address-form"):
                    AlertInfo = ''
                    for AlertText in self.driver.find_elements_by_xpath("//div[@class='a-alert-content']"):
                        AlertInfo +=  AlertText.text
                    if 'Please' in AlertInfo:
                        print('Please check address, it can not set... ')
                        self.FunctionInfo['errorcode'] = 'FixAddress'
                        self.FunctionInfo['status'] = False
                        return False
                    if 'do not match' in AlertInfo:
                        print('Please check address, address you provided do not match.... ')
                        self.FunctionInfo['errorcode'] = 'AddressNotMatch'
                        self.FunctionInfo['status'] = False
                        return False
            except:
                pass
        # not to correct address, use original
        try:
            self.driver.find_element_by_id("address-ui-widgets-original-address-block_id-input").click()
            self.driver.find_element_by_xpath('//input[@name="address-ui-widgets-saveOriginalOrSuggestedAddress"]').click()
            print('No correcting address, select original...')
        except:
            pass
        # go back and check address book
        try:
            WebDriverWait(self.driver, 30, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "ya-myab-address-add-link")))
            AddressElements = self.driver.find_elements_by_class_name("address-column")
            #AddressElements = self.driver.find_elements_by_class_name("normal-desktop-address-tile")
            #AddressOptions = self.driver.find_elements_by_class_name("edit-address-desktop-link")
        except:
            print('Address set: fail back to address book!!')
            self.FunctionInfo['errorcode'] = 'AddressEditFail'
            self.FunctionInfo['status'] = False
            return False
        # set as default
        for item in AddressElements:
            #print(item.text)
            time.sleep(1) #important
            try: AddressText = self.Replace.sub(repl='',string=item.text.lower())
            except: AddressText = ''
            if self.Replace.sub(repl='',string=self.FunctionInfo['fullname'].lower()) in AddressText and \
                    self.Replace.sub(repl='', string=self.FunctionInfo['address'].lower()) in AddressText and \
                    self.Replace.sub(repl='', string=self.FunctionInfo['phonenumber']) in AddressText:
                try:
                    SetDefualt = item.find_element_by_class_name("set-address-default")
                    self.ClickElement(SetDefualt)
                    time.sleep(5)
                    break
                except:
                    print(traceback.print_exc())
                    print('Address set: fail to set as default')
                    pass
        # check default setting
        try:
            AddressText = self.Replace.sub(repl='',string=self.driver.find_element_by_class_name("address-section-with-default").text.lower())
            if SMatch(self.Replace.sub(repl='',string=self.FunctionInfo['fullname'].lower()) , AddressText) and \
                SMatch(self.Replace.sub(repl='', string=self.FunctionInfo['address'].lower()), AddressText) and \
                SMatch(self.Replace.sub(repl='', string=self.FunctionInfo['phonenumber']), AddressText):
                print('Address set done!')
                self.FunctionInfo['errorcode'] = 'AddressSetPass'
                self.FunctionInfo['status'] = True
            return True
        except:
            print('Setting default address fail!!')
            self.FunctionInfo['errorcode'] = 'DefaultAddressFail'
            self.FunctionInfo['status'] = True
            return True

    def SelectAsinFromBuyBox(self, asin):
        # noinspection PyBroadException
        try:
            SwatchAvailable = self.driver.find_elements_by_class_name('swatchAvailable')
            for item in SwatchAvailable:
                if asin in item.get_attribute('data-defaultasin'):
                    self.ScrollToElement(item)
                    item.click()
                    time.sleep(1)
                    break
        except:
            print('Error happen when select and click!')
            return False
        try:
            SwatchSelect = self.driver.find_element_by_class_name('swatchSelect')
            if asin in SwatchSelect.get_attribute('data-defaultasin'):
                return True
        except:
            pass

    def AddCart(self):
        self.FunctionInfo['status'] = False
        # no danate
        time.sleep(5)
        try:
            self.driver.find_element_by_class_name("dismiss").click()
            self.ClickElement(self.driver.find_element_by_class_name("dismiss"))
            time.sleep(2)
        except: pass
        if not self.check_captch():
            print('Add cart Fail because of captch...')
            self.FunctionInfo['errorcode'] = 'CaptchWhenAddCard'
            self.FunctionInfo['status'] = True
            return False

        self.SelectAsinFromBuyBox(self.FunctionInfo['asin'])
        try:
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "feature-bullets")))
            NewButtons = self.driver.find_elements_by_partial_link_text('from')
            for item in NewButtons:
                if 'offer-listing' in str(item.get_attribute("href")):
                    ProductLink = item.get_attribute("href")
                    self.move_to_element(item)
                    self.ClickElement(item)
                    break
        except:
            print('Production link error!!!'+ self.FunctionInfo['asin'])
            print(traceback.print_exc())
            self.FunctionInfo['errorcode'] = 'ProductionLinkError'
            self.FunctionInfo['status'] = False
            pass
            #return False

        try:
            while self.driver.title == "Sorry!Something went wrong!":
                print("Something went wrong page...")
                self.driver.get(ProductLink)
        except:
            pass
        # Add to Cart
        AddCartDone = False
        try:
            WebDriverWait(self.driver, 30, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "olpOfferList")))
            #CartElements = self.driver.find_elements_by_xpath("//span[@class='a-size-large a-color-price olpOfferPrice a-text-bold']")
            CartElements = self.driver.find_elements_by_class_name("olpOfferPrice")
            AddCartButtons = self.driver.find_elements_by_class_name('a-button-input')
            for i in range(len(CartElements)):
                if float(CartElements[i].text.strip('[$£]')) == float(self.FunctionInfo['orderprice']):
                    print('Price compare : ' + CartElements[i].text.strip('[$£]') + '===' + self.FunctionInfo['orderprice'])
                    self.ClickElement(AddCartButtons[i])#AddCartButtons[i].click()
                    AddCartDone = True
                    break
        except:
            #print(traceback.print_exc())
            print('Add to cart: Not found in offer list:: ' + self.FunctionInfo['asin'])
            pass
        # if no 'from new'
        if AddCartDone:
            print('Adding to cart...'+ self.FunctionInfo['asin'])
        else:
            try:
                self.move_to_element(self.driver.find_element_by_id('add-to-cart-button'))
                self.driver.find_element_by_id('add-to-cart-button').click()
            except:
                print('Failed to add to cart... '+ self.FunctionInfo['asin'])
                self.FunctionInfo['errorcode'] = 'AddCartClickFail'
                self.FunctionInfo['status'] = False
                return False


        # cancel coverage
        try:
            self.driver.find_element_by_xpath("//button[@id='siNoCoverage-announce']").click()
        except:
            pass
        # affirm in user's cart
        try:
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "huc-v2-order-row-confirm-text")))
            self.driver.find_element_by_id('huc-v2-order-row-confirm-text')
            print("Added to cart ...")
            self.FunctionInfo['errorcode'] = 'AddCartPass'
            self.FunctionInfo['status'] = True
            return True
        except:
            print("Not added to cart ...")
            self.FunctionInfo['errorcode'] = 'CartStillEmpty'
            self.FunctionInfo['status'] = False
            return False

    def PlaceOrder(self):
        self.FunctionInfo['status'] = False
        self.driver.get("https://www.amazon.com/gp/cart/view.html/ref=nav_cart")
        # proceed to check out, returun if cart is empty
        try:
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "sc-buy-box-ptc-button")))
            OrderPrice = re.findall('[0-9\.]+', self.driver.find_element_by_xpath("//span[@class='a-size-medium a-color-price sc-price sc-white-space-nowrap  sc-price-sign']").text)[0]
            self.driver.find_element_by_id("sc-buy-box-ptc-button").click()
        except:
            print('Nothing in cart...')
            self.FunctionInfo['errorcode'] = 'CartEmpty'
            self.FunctionInfo['status'] = False
            return False
        # cancel coverage
        try: self.driver.find_element_by_xpath("//button[@id='siNoCoverage-announce']").click()
        except: pass
        # skip advertising
        try: self.driver.find_element_by_xpath("//*[text()='Continue placing your order']").click()
        except: pass
        # prime-nothanks-button
        try:
            self.driver.find_element_by_class_name('prime-nothanks-button').click()
            time.sleep(5)
            self.driver.refresh()
            time.sleep(5)
        except: pass
        try:
            if 'Prime Student' in self.driver.title:
                self.driver.refresh()
                time.sleep(5)
        except:
            pass
        # select shipping address
        AddressSet = False
        FullNameLower = self.Replace.sub(repl='',string=self.FunctionInfo['fullname'].lower())
        PhonenumberLower = self.Replace.sub(repl='',string=self.FunctionInfo['phonenumber'])
        AddressLower = self.Replace.sub(repl='',string=self.FunctionInfo['address'].lower())
        try: # address select method 0
            WebDriverWait(self.driver, 30, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.CLASS_NAME, "address-book")))
            AddressNames = self.driver.find_elements_by_class_name("displayAddressFullName")
            AddressPhones = self.driver.find_elements_by_class_name("displayAddressPhoneNumber")
            AddressLine1 = self.driver.find_elements_by_class_name("displayAddressAddressLine1")
            AddressButtons = self.driver.find_elements_by_class_name("ship-to-this-address")
            for i in range(len(AddressNames)):
                AddressText = self.Replace.sub(repl='',string=AddressNames[i].text.lower()) + \
                              self.Replace.sub(repl='', string=AddressPhones[i].text.lower()) + \
                              self.Replace.sub(repl='', string=AddressLine1[i].text.lower())
                if SMatch(FullNameLower, AddressText) \
                        and SMatch(PhonenumberLower , AddressText) \
                        and SMatch(AddressLower , AddressText):
                    self.ClickElement(AddressButtons[i])
                    time.sleep(3)
                    AddressSet = True
                    break
        except: pass
        if not AddressSet:
            pass
        try: # address select method 1
            try:
                AddressName = self.Replace.sub(repl='',string=self.driver.find_element_by_class_name("displayAddressFullName").text.lower())
                AddressLine1 = self.Replace.sub(repl='',string=self.driver.find_element_by_class_name("displayAddressAddressLine1").text.lower())
            except:
                AddressName = ''
                AddressLine1 = ''
            AddressText = AddressName + AddressLine1
            if SMatch(self.Replace.sub(repl='',string=self.FunctionInfo['fullname'].lower()), AddressText) \
                    and SMatch(self.Replace.sub(repl='',string=self.FunctionInfo['address'].lower()), AddressText):
                AddressSet = True
            else:
                AddressBook = self.driver.find_elements_by_xpath("//span[@class='a-label a-radio-label']")
                for i in range(len(AddressBook)):
                    AddressBookText = self.Replace.sub(repl='',string=AddressBook[i].text.lower())
                    if SMatch(FullNameLower , AddressBookText) and SMatch(AddressLower, AddressBookText):
                        self.ClickElement(self.driver.find_element_by_id("orderSummaryPrimaryActionBtn-announce"))
                        AddressSet = True
                        break
        except:
            print(traceback.print_exc())
            pass
        '''
        # affrirm address setting done
        if AddressSet:
            print('PlaceOrder: address set done...')
        else:
            print('PlaceOrder: address set fail... ')
            self.FunctionInfo['errorcode'] = 'AddressSetFail'
            self.FunctionInfo['status'] = False
            return False
        '''


        # if address selecting no pass
        time.sleep(5)
        if 'Update this shipping address' in self.driver.title:
            print('Default address error when order...')
            self.FunctionInfo['errorcode'] = 'AddressShallUpdate'
            self.FunctionInfo['status'] = False
            return False
        if 'Select Shipping Addresses' in self.driver.title:
            print("Sorry, this item can't be shipped to your selected address.")
            self.FunctionInfo['errorcode'] = 'AddressNoShipped'
            self.FunctionInfo['status'] = False
            return False

        # prime-nothanks-button
        try: self.driver.find_element_by_class_name('prime-nothanks-button').click()
        except: pass

        #Choose your shipping options -> frees hipping
        try:
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "shippingOptionFormId")))
            FreeShipping = self.driver.find_element_by_xpath("//div[contains(text(),'FREE Shipping')]")
            self.ClickElement(FreeShipping)
            time.sleep(2)
        except:
            pass
        try: self.ClickElement(self.driver.find_element_by_xpath("//input[@class='a-button-text']"))
        except: pass
        #skip advertising
        try:
            self.driver.find_element_by_xpath("//*[text()='Continue placing your order']").click()
        except:
            pass

        '''
        # checkout by giftcard
        try: # checkout by giftcard methord 0
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException)\
                .until(EC.visibility_of_element_located((By.ID, "gc-link-expander")))
            try:
                GiftCardBalance = re.findall('[0-9\.]+', self.driver.find_element_by_xpath("//label[@class='balance-checkbox']").text)[0]
            except:
                GiftCardBalance = '0'
            # Continue to place order if already affordable
            if float( GiftCardBalance) < float(OrderPrice):
                try:
                    gift_card_element = self.driver.find_element_by_xpath("//a[@id='gc-link-expander']")
                    self.ClickElement(gift_card_element)
                    self.driver.find_element_by_xpath("//input[@id='gcpromoinput']").send_keys(self.FunctionInfo['giftcardnumber'])
                    self.ClickElement(self.driver.find_element_by_xpath("//input[@id='button-add-gcpromo']"))
                except:
                    print('Gift Card add fail...')
                    self.FunctionInfo['errorcode'] = 'GiftCardAddFail'
                    self.FunctionInfo['status'] = False
                    return False
                # gift card Error
                try:
                    GiftCardNewBalance = re.findall('[0-9\.]+', self.driver.find_element_by_xpath(
                        "//label[@class='balance-checkbox']").text)[0]
                    if float(GiftCardBalance) == float(GiftCardNewBalance):
                        print('Error reports when adding gift card!')
                        self.FunctionInfo['errorcode'] = 'GiftCardAddFail'
                        self.FunctionInfo['status'] = False
                        return False
                except:
                    print(traceback.print_exc())
                    pass
            else:
                print('It is already affordable, needs no gift card!')
            # continue to pay
            try:
                self.driver.find_element_by_xpath("//input[@id='continue-top']").click()
            except:
                pass
        except:
            pass
        try: # checkout by giftcard methord 1
            WebDriverWait(self.driver, 5, 0.5, ignored_exceptions=TimeoutException)\
                .until(EC.visibility_of_element_located((By.ID, "existing-payment-methods")))
            try:
                GiftCardBalance = re.findall('[0-9\.]+', self.driver.find_element_by_xpath("//label[@for='pm_gc_radio']").text)[0]
            except:
                GiftCardBalance = '0'
            # Continue to place order if already affordable
            if float( GiftCardBalance) < float(OrderPrice):
                try:
                    self.driver.find_element_by_xpath("//input[@id='gcpromoinput']").send_keys(self.FunctionInfo['giftcardnumber'])
                    self.ClickElement(self.driver.find_element_by_xpath("//input[@id='button-add-gcpromo']"))
                except:
                    print('Gift Card add fail...')
                    self.FunctionInfo['errorcode'] = 'GiftCardAddFail'
                    self.FunctionInfo['status'] = False
                    return False
                # gift card Error
                try:
                    GiftCardNewBalance = re.findall('[0-9\.]+', self.driver.find_element_by_xpath(
                        "//label[@class='balance-checkbox']").text)[0]
                    if float(GiftCardBalance) == float(GiftCardNewBalance):
                        print('Error reports when adding gift card!')
                        self.FunctionInfo['errorcode'] = 'GiftCardAddFail'
                        self.FunctionInfo['status'] = False
                        return False
                except:
                    print(traceback.print_exc())
                    pass
            else:
                print('It is already affordable, needs no gift card!')
            try:
                self.driver.find_element_by_xpath(
                    "//input[@aria-labelledby='orderSummaryPrimaryActionBtn-announce']").click()
            except:
                pass
        except:
            pass
        '''
        # continue to pay
        try:
            self.driver.find_element_by_id('order-summary-container').find_element_by_id('continue-top').click()
            #time.sleep(5)
        except:
            pass
        # place order
        try:
            self.driver.find_elements_by_partial_link_text('No thanks, continue without Amazon Prime benefits').click()
        except:
            pass
        try:
            self.driver.find_element_by_class_name('prime-checkout-continue-link').click()
        except:
            pass
        # skip advertising
        try:
            self.driver.find_element_by_xpath("//*[text()='Continue placing your order']").click()
        except:
            pass
        # select free shipping
        try:
            for item in self.driver.find_elements_by_class_name('ship-option'):
                if 'FREE Shipping' in item.text:
                    item.click()
                    time.sleep(5)
                    break
        except:
            pass
        # check shipping address
        try:
            ShippingAddress = self.Replace.sub(repl='',string=self.driver.find_element_by_id('desktop-shipping-address-div').text.lower())
            if SMatch(FullNameLower, ShippingAddress) and SMatch(PhonenumberLower, ShippingAddress) and SMatch(AddressLower, ShippingAddress):
                print('shipping address checked..')
            else:
                print('Place order fail: shippingaddress not right')
                self.FunctionInfo['errorcode'] = 'PlaceOrderAddressError'
                self.FunctionInfo['status'] = False
                #return False
        except:
            print('Place order fail: shippingaddress not found')
            self.FunctionInfo['errorcode'] = 'PlaceOrderAddressFail'
            self.FunctionInfo['status'] = False
            return False

        try:  # place order methord0
            self.ClickElement(self.driver.find_element_by_class_name("place-order-button-link"))
        except:
            pass
        try: # place order methord1
            self.ClickElement(self.driver.find_element_by_id("submitOrderButtonId-announce"))
        except:
            pass

        try:
            WebDriverWait(self.driver, 10, 0.5, ignored_exceptions=TimeoutException).until(EC.title_contains('Amazon.com Thanks You'))
            self.FunctionInfo['ordernumber'] = self.driver.find_element_by_xpath("//h5/span[@class='a-text-bold']").text
            print('Place order succeed! Order number:' + self.FunctionInfo['ordernumber'])
            self.FunctionInfo['errorcode'] = 'OrderPass'
            self.FunctionInfo['status'] = True
            return True
        except:
            print('Place order fail...')
            self.FunctionInfo['errorcode'] = 'PlaceOrderFail'
            self.FunctionInfo['status'] = False
            return False

    def GoToReview(self):
        self.FunctionInfo['status'] = False
        self.FunctionInfo['errorcode'] = 'GoToReview'
        try:
            self.driver.get("https://www.amazon.com/gp/your-account/order-history?ref_=ya_d_c_yo")
        except:
            pass

        if not self.check_captch():
            print('Add cart Fail because of captch...')
            self.FunctionInfo['status'] = False
            self.FunctionInfo['errorcode'] = 'CaptchWhenReview'
            return False
        try:
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.LINK_TEXT, "Write a product review")))
            ReviewButton = self.driver.find_element_by_link_text("Write a product review")
            ReviewButton.click()
            print('Go to reviewer page through order page.')
        except:
            try: self.driver.get("https://www.amazon.com/review/create-review/#")
            except: pass
            print('No review button. Go to review by link')

        try:
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "reviewProductsViewport")))
            print('Ready to write reviewer.')
            self.FunctionInfo['status'] = True
            self.FunctionInfo['errorcode'] = 'ReadyToReview'
            return True
        except:
            print('View reviewer fail.')
            self.FunctionInfo['status'] = False
            self.FunctionInfo['errorcode'] = 'ViewReviewFail'
            return False

    def WriteReview(self):
        # move to botton for loading all production info
        try:
            self.speed = 20
            self.ScrollToElement(self.driver.find_element_by_id('navBackToTop'))
            self.driver.find_element_by_id('navBackToTop').click()
        except: pass
        # click submit button if any not clicked
        try:
            Reviews = self.driver.find_elements_by_xpath("//div[@class='a-section a-spacing-none desktop overflow']")
        except:
            Reviews = ''
        for i in range(len(Reviews)):
            try:
                SelectReview = self.driver.find_element_by_id('reviewSection' + str(i))
                ReviewBotton = SelectReview.find_element_by_class_name('submitButton')
                ReviewBotton.click()
            except:
                pass

        # find review for ASIN
        try:
            ReviewFound = False
            Reviews = self.driver.find_elements_by_xpath("//div[@class='a-section a-spacing-none desktop overflow']")
            for i in range(len(Reviews)):
                try: LinkofReview = Reviews[i].find_element_by_tag_name("a").get_attribute("href")
                except: LinkofReview = ''
                if self.FunctionInfo['asin'] in LinkofReview:
                    SelectReview = Reviews[i]
                    SelectNum = i
                    ReviewFound = True
                    break
            if not ReviewFound:
                print('Sorry, ASIN not found in Reviews!!')
                self.FunctionInfo['status'] = False
                self.FunctionInfo['errorcode'] = 'NoASINReview'
                return False
        except:
            print('Review: Error happen when find ASIN in Reviews!!')
            self.FunctionInfo['status'] = False
            self.FunctionInfo['errorcode'] = 'ReviewLoadError'
            return False
        # check if star exist
        try:
            SelectReview.find_element_by_class_name('starsContainer')
        except:
            print('Review: Sorry, No review Star button!!')
            self.FunctionInfo['status'] = False
            self.FunctionInfo['errorcode'] = 'ReviewNoStar'
            return False
        # skip if star already clicked.
        ReviewStarSet = False
        try:
            SelectReview.find_element_by_class_name('yellowStar')
            ReviewStarSet = True
        except:
            pass
        try:
            if not ReviewStarSet:
                if self.FunctionInfo['reviewstar'] in '12345':
                    ReviewStar = SelectReview.find_element_by_class_name('rating_' + self.FunctionInfo['reviewstar'])
                else:
                    ReviewStar = SelectReview.find_element_by_class_name('rating_5')
                self.move_to_element(ReviewStar)
                ActionChains(self.driver).move_to_element(ReviewStar).perform()
                ReviewStar.click()
        except:
            print('Review: Error happen when Click star!!')
            print(traceback.print_exc())
            self.FunctionInfo['status'] = False
            self.FunctionInfo['errorcode'] = 'ReviewStarError'
            return False

        # check if reviewable
        try:
            time.sleep(10)
            SelectReview = self.driver.find_element_by_id('reviewSection' + str(SelectNum))
            if 'Sorry, we are unable to accept' in SelectReview.text:
                print('Sorry, Review is unable to accept!!')
                self.FunctionInfo['status'] = False
                self.FunctionInfo['errorcode'] = 'CannotReview'
                return False
        except:
            print(traceback.print_exc())
            pass
        # submit review
        try:
            SelectReview = self.driver.find_element_by_id('reviewSection' + str(SelectNum))
            ReviewContent = SelectReview.find_element_by_tag_name("textarea")
            ReviewContent.clear()
            ReviewContent.send_keys(self.FunctionInfo['reviewercontent'])
            SelectReview = self.driver.find_element_by_id('reviewSection' + str(SelectNum))
            ReviewTitle = SelectReview.find_element_by_class_name("reviewTitle")
            ReviewTitle.clear()
            ReviewTitle.send_keys(self.FunctionInfo['reviewertitle'])
            SelectReview = self.driver.find_element_by_id('reviewSection' + str(SelectNum))
            SubmitButton = SelectReview.find_element_by_class_name('submitButton')
            SubmitButton.click()
        except:
            print('Sorry, Failed to submit review....')
            #print(traceback.print_exc())
            self.FunctionInfo['status'] = False
            self.FunctionInfo['errorcode'] = 'ReviewSubmitFail'
            return False

        try:
            time.sleep(5)
            SelectReview = self.driver.find_element_by_id('reviewSection' + str(SelectNum))
            if "Sorry, we've experienced a problem." in SelectReview.text:
                print('Sorry, Rreview cannot be submitted....')
                self.FunctionInfo['status'] = False
                self.FunctionInfo['errorcode'] = 'BadReview'
                return False
        except:
            pass

        try:
            ReviewerText = self.driver.find_element_by_id('reviewSection' + str(SelectNum)).text
            if 'Thanks for your review' in ReviewerText:
                print('Review done!!!')
                self.FunctionInfo['status'] = True
                self.FunctionInfo['errorcode'] = 'ReviewPass'
                return True
            pass
        except:
            print('Review failed, please try again...')
            self.FunctionInfo['status'] = False
            self.FunctionInfo['errorcode'] = 'ReviewRetry'
            return False

    def CreatAcount(self, EmailDomain):
        self.FunctionInfo['errorcode'] = 'CreatAcountstart'
        self.FunctionInfo['status'] = False
        Lastname = names.get_last_name()
        Firstname = names.get_first_name()
        if not self.FunctionInfo['customername']:
            self.FunctionInfo['customername'] = Firstname + " " + Lastname
        if self.NewRandomAccount:
            self.FunctionInfo['username'] = Firstname + Lastname + str(randint(0, 999)) + EmailDomain
            self.FunctionInfo['password'] = ''.join(random.sample(chars, 10))
        print('CreatAcount:: ' + self.FunctionInfo['username'] + '  Password:: ' + self.FunctionInfo['password'])

        try:
            self.driver.get("https://www.amazon.com/")
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "nav-link-accountList")))
            self.driver.find_element_by_id("nav-link-accountList").click()
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "createAccountSubmit")))
            self.driver.find_element_by_id("createAccountSubmit").click()
        except:
            print('Go to create account page fail...')
            self.FunctionInfo['status'] = False
            self.FunctionInfo['errorcode'] = 'CreatPageFail'
            return False

        try:
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "ap_register_form")))
            CustomerName = self.driver.find_element_by_id("ap_customer_name")
            CustomerName.send_keys(self.FunctionInfo['customername'])
            EmailInput = self.driver.find_element_by_id("ap_email")
            EmailInput.send_keys(self.FunctionInfo['username'])
            PasswordInput = self.driver.find_element_by_id("ap_password")
            PasswordInput.click()
            PasswordInput.send_keys(self.FunctionInfo['password'])
            PasswordCheck = self.driver.find_element_by_id("ap_password_check")
            PasswordCheck.send_keys(self.FunctionInfo['password'])
            CreatButton = self.driver.find_element_by_id("continue")
            CreatButton.click()
        except:
            print('Submit new account fail...')
            self.FunctionInfo['status'] = False
            self.FunctionInfo['errorcode'] = 'AccountSubmitFail'
            return False

        if not self.check_captch():
            print('CreatAcount: Fail because of captch...')
            self.FunctionInfo['errorcode'] = 'CaptchError'
            self.FunctionInfo['status'] = False
            return False
        # re send password if there is capth
        try:
            WebDriverWait(self.driver, 20, 0.5, ignored_exceptions=TimeoutException) \
                .until(EC.visibility_of_element_located((By.ID, "image-captcha-section")))
            PasswordInput = self.driver.find_element_by_id("ap_password")
            PasswordInput.click()
            PasswordInput.send_keys(self.FunctionInfo['password'])
            PasswordCheck = self.driver.find_element_by_id("ap_password_check")
            PasswordCheck.send_keys(self.FunctionInfo['password'])
            self.driver.find_element_by_id("continue").click()
            if not self.check_captch():
                print('CreatAcount: Fail because of captch...')
                self.FunctionInfo['errorcode'] = 'CaptchError'
                self.FunctionInfo['status'] = False
                return False
        except:
            pass

        print('Creat acount done')
        self.FunctionInfo['errorcode'] = 'CreatAcountPass'
        self.FunctionInfo['status'] = True
        return True

    def Walkaround(self, ClickCounter = 0):
        time.sleep(5)
        if ClickCounter >= randint(0, 5):
            return True
        try:
            self.driver.find_element_by_id('btnNoThanks').click()
        except:
            pass
        try:
            PageSize = self.get_page_size()
            # scroll page
            for i in range(randint(2, 5)):
                self.speed = randint(10, 40)
                self.sroll_to_position(randint(0, PageSize))
            # click Items
            while True:
                PageItems = self.driver.find_elements_by_class_name("a-link-normal")
                SelectedItem = random.sample(PageItems, 1)[0]
                if ('/dp/' in SelectedItem.get_attribute("href") or '/gp/slredirect/' in SelectedItem.get_attribute("href")) \
                    and SelectedItem.is_enabled() and SelectedItem.is_displayed():
                    self.move_to_element(SelectedItem)
                    SelectedItem.click()
                    break
        except:
            #print(traceback.print_exc())
            return False

        ClickCounter += 1
        self.Walkaround(ClickCounter)
