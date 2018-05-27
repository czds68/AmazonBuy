from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib import request
from captcha2upload import CaptchaUpload
import traceback
from random import randint
import os


def SolveCaptha(driver):
    RandomName = str(randint(1000, 9999))
    CaptchaFunc = CaptchaUpload('f4ab06a8e3e5be77134312d55c7a7bb4')
    time.sleep(5)
    # get captcha Image
    Image = False
    try:
        if 'Robot Check' in driver.title:
            Image = driver.find_element_by_tag_name('img').get_attribute('src')
    except:
        pass
    try:
        Image = driver.find_element_by_id("auth-captcha-image")
    except:
        pass
    if not Image:
        return True
    # download Image
    try:
        request.urlretrieve(Image, "./logs/" + RandomName + ".jpg")
        time.sleep(5)
        CaptchaAnswer = CaptchaFunc.solve("./logs/" + RandomName + ".jpg")
    except:
        print('Captcha fail to solve')
        return False
    finally:
        try: os.system("rm " + "./logs/" + RandomName + ".jpg")
        except: pass

    # fill captcha
    try:
        FillAnswer = driver.find_element_by_id("captchacharacters")
    except:
        pass
    try:
        FillAnswer = driver.find_element_by_id("auth-captcha-guess")
    except:
        pass
    try:
        FillAnswer.click()
        FillAnswer.clear()
        FillAnswer.send_keys(CaptchaAnswer)
    except:
        print('Captcha fail to fill')
        return False

    #submit captcha
    try:
        driver.find_element_by_id('continue').click()
    except: pass

    try:
        driver.find_element_by_xpath("//button[@type='submit']").click()
    except: pass

    try:
        driver.find_element_by_id("cnep_1B_submit_button").click()
    except: pass

    try:
        driver.find_element_by_id('signInSubmit').click()
    except: pass

    return True