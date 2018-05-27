#coding: utf-8
from amazon_production import amazon_production
import requests
import re
import os
import csv
import random
import time
from datetime import datetime
import traceback
import threading
import pandas as pd
import sys
import queue


log_file_path = './logs/'
print_path = './code_log/'
order_file_path = './order.csv'
rank_retry_num = 5
order_retry_num = 2
review_retry_num = 2
change_mac = True
__console__ = sys.stdout

def update_price(production_header, production_infos, day_date):
    file_lock = ''
    proxy_pool = []
    proxy_time = datetime.now()

    while True:
        print('Begin to update price...')
        for i in range(len(production_infos)):
            asin, country, sections, keywords, production_info = make_info(production_infos[i])
            price_got = False
            print('Update price for ' + asin)
            for test_num in range(6):
                try:
                    proxy_pool, proxy_time = get_proxy(proxy_pool, proxy_time)
                    proxy = proxy_pool.pop() if proxy_pool else ''
                    task = amazon_production(production_info, proxy, file_lock)
                    price = task.amazon_price()
                    if price:
                        price_got = True
                        break
                except:
                    try:
                        task.driver.delete_all_cookies()
                        task.driver.quit()
                    except:
                        pass
                    print('Price update fail...')

            if price_got is False:
                print('Price update for ' + production_info['asin'] +' failed, please check the URL!!!!!!')
                continue

            for j in range(len(production_infos)):
                if production_info['asin'] in production_infos[j]:
                    production_infos[j][2] = price[0]
                    production_infos[j][3] = price[1]

            if day_date != datetime.now().day:
                print('Today is over, sorry...')
                return
            time.sleep(5)

        task_file = open(source_file_path, 'w', newline='')
        info_file_write = csv.writer(task_file)
        info_file_write.writerow(production_header)
        for i in range(len(production_infos)):
            info_file_write.writerow(production_infos[i])
        task_file.close()
        print('Update price done...')
        time.sleep(7200)

def submit_task(production_info = None, proxy = None, file_lock = threading.RLock()):
    try:
        task = amazon_production(production_info, proxy, file_lock)
        return task.amazon_run()
    except:
        try:
            task.driver.delete_all_cookies()
            task.driver.quit()
        except:
            pass
        try:
            task.fill_log('FAIL_TO', task.stay_time())
        except:
            pass
        print(traceback.print_exc())
        return False

def submit_rank_task(production_info, proxy = None, file_lock = threading.RLock()):
    try:
        task = amazon_production(production_info, proxy, file_lock)
        rank_report = task.amazon_search()
        #print('RANK report:::::: ' + str(rank_report))
        if rank_report:
            fill_rank_log(rank_report, file_lock)
            production_info['rank'] = rank_report['rank']
            return True
    except:
        try:
            task.driver.delete_all_cookies()
            task.driver.quit()
        except:
            pass
        print(traceback.print_exc())
        return False

def submit_order_task(order_info, order_queue, proxy = None, file_lock = threading.RLock()):
    ordernumber = False
    error_code = ''
    try:
        task = amazon_production(order_info, proxy, file_lock)
        ordernumber, error_code = task.amazon_buy(order_info)
    except:
        print(traceback.print_exc())
        try:
            task.driver.delete_all_cookies()
            task.driver.quit()
        except:
            pass
    finally:
        try:
            task.driver.delete_all_cookies()
            task.driver.quit()
        except:
            pass
        if not ordernumber:
            if  error_code == 'GiftCardUsed' or \
                error_code == 'BadGiftCard' or \
                error_code == 'AddressNoShipped' or \
                error_code == 'AddressShallUpdate':
                order_info['retrynumber'] = order_retry_num
            else:
                order_info['retrynumber'] += 1
            order_info['errorcode'] = error_code
            file_lock.acquire()
            order_queue.put(order_info)
            file_lock.release()
        fill_order_log(order_info, ordernumber, file_lock)

def fill_order_log(order_info, ordernumber, file_lock):
    file_lock.acquire()
    date_path = str(time.strftime("%Y%m%d", time.localtime())) + '/'
    if not os.path.exists(log_file_path):
        os.mkdir(log_file_path)
    if not os.path.exists(log_file_path + date_path):
        os.mkdir(log_file_path + date_path)
    report_info = []
    report_info.append(str(datetime.now()))
    report_info.append(order_info['username'])
    report_info.append(order_info['asin'])
    report_info.append(ordernumber)
    report_info.append(order_info['ccnumber'])
    report_info.append(order_info['trackingnumber'])
    report_info.append(order_info['price'])

    if ordernumber:
        order_log_path = log_file_path + date_path + 'order.csv'
    else:
        report_info.append(order_info['retrynumber'])
        report_info.append(order_info['errorcode'])
        order_log_path = log_file_path + date_path + 'order_fail.csv'

    order_file = open(order_log_path, "a")
    log_file_write = csv.writer(order_file)
    log_file_write.writerow(report_info)
    order_file.close()
    file_lock.release()

def submit_review_task(order_info, review_queue, proxy = None, file_lock = threading.RLock()):
    status = False
    error_code = ''
    try:
        task = amazon_production(order_info, proxy)
        status, error_code = task.amazon_review(order_info)
    except:
        print(traceback.print_exc())
        try:
            task.driver.delete_all_cookies()
            task.driver.quit()
        except:
            pass
    finally:
        if not status:
            if  error_code == 'NoReview' or \
                error_code == 'BadReview' or \
                error_code == 'CanotReview' :
                order_info['retrynumber'] = review_retry_num
            else:
                order_info['retrynumber'] += 1
            order_info['errorcode'] = error_code
            file_lock.acquire()
            review_queue.put(order_info)
            file_lock.release()
        fill_review_log(order_info, status, file_lock)


def fill_review_log(order_info, status, file_lock):
    file_lock.acquire()
    date_path = str(time.strftime("%Y%m%d", time.localtime())) + '/'
    if not os.path.exists(log_file_path):
        os.mkdir(log_file_path)
    if not os.path.exists(log_file_path + date_path):
        os.mkdir(log_file_path + date_path)
    report_info = []
    report_info.append(str(datetime.now()))
    report_info.append(order_info['username'])
    report_info.append(order_info['asin'])
    report_info.append(order_info['ccnumber'])
    report_info.append(order_info['trackingnumber'])
    report_info.append(order_info['price'])
    report_info.append(order_info['reviewstar'])
    report_info.append(order_info['reviewheadline'])
    report_info.append(order_info['reviewcontent'])

    if status:
        order_log_path = log_file_path + date_path + 'review.csv'
    else:
        report_info.append(order_info['retrynumber'])
        report_info.append(order_info['errorcode'])
        order_log_path = log_file_path + date_path + 'review_fail.csv'

    review_file = open(order_log_path, "a")
    log_file_write = csv.writer(review_file)
    log_file_write.writerow(report_info)
    review_file.close()
    file_lock.release()


def fill_rank_log(rank_report = None, file_lock = threading.RLock()):
    file_lock.acquire()

    date_path = str(time.strftime("%Y%m%d", time.localtime())) + '/'
    if not os.path.exists(log_file_path):
        os.mkdir(log_file_path)
    if not os.path.exists(log_file_path + date_path):
        os.mkdir(log_file_path + date_path)

    # create new file if not exist
    rank_file_path = log_file_path + date_path + 'rank.csv'
    if not os.path.exists(rank_file_path):
        log_file = open(rank_file_path, 'a+', newline='')
        log_file_write = csv.writer(log_file)
        log_file_write.writerow(['Timestamp', 'Country', 'ASIN', 'Keyword', 'Department', 'Rank'])
    else:
        log_file = open(rank_file_path, 'a', newline='')
        log_file_write = csv.writer(log_file)

    new_log = [str(datetime.now().date()), rank_report['country'], rank_report['asin'], rank_report['keyword'], \
               rank_report['department'], rank_report['rank']]
    log_file_write.writerow(new_log)
    log_file.close()
    file_lock.release()

def get_proxy(proxy_pool, proxy_time, time_out = 300):
    if proxy_pool == [] or int((datetime.now() - proxy_time).seconds) > time_out:
        #proxy_get_url = 'http://api.xdaili.cn/xdaili-api//\
        #    privateProxy/applyStaticProxy?spiderId=c0e4dc4f348e4dc9b791f96880ca912e&returnType=1&count=5'
        #proxy_get_url ='http://webapi.http.zhimacangku.com/getip?num=5&type=1&pro=&city=0&yys=0&port=11&pack=15066&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        proxy_get_url = 'http://webapi.http.zhimacangku.com/getip?num=5&type=1&pro=&city=0&yys=0&port=11&time=5&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        try:
            proxy_text = requests.get(proxy_get_url).text
            #while "ERRORCODE" in proxy_text:
            while "false" in proxy_text:
                print('Retry for proxy...  Last get time::' + str(proxy_time.time()))
                print('Time now::: ' + str(datetime.now().time()))
                time.sleep(12)
                proxy_text = requests.get(proxy_get_url).text
            proxys_got = re.split('\r\n',proxy_text)[0:-1]
            proxy_pool = proxys_got
            proxy_time = datetime.now()
        except:
            proxy_pool = ['']
            print('Proxy fetch error:')
            print(traceback.print_exc())
    return proxy_pool , proxy_time


def get_last_counter(asin_file_path):
    if os.path.exists(asin_file_path):
        log_file = open(asin_file_path, 'r', newline='')
        last_log_info_list = int(re.split(',', log_file.readlines()[-1])[1])
        log_file.close()
        return last_log_info_list
    else:
        return 0

def make_info(production_info = None):
    info_list = production_info
    sections = int(info_list[5])
    asin = info_list[4]
    country = info_list[6].lower()
    keywords = list(filter(lambda x: x != '', info_list[8:-1]))
    if keywords:
        selected_keyword = random.sample(keywords, 1)
    else:
        selected_keyword = ['']
        print('There is no keyword in the table!!!!!!!')
    production_info = {}
    production_info['country'] = info_list[6].lower()
    production_info['department'] = info_list[1]
    production_info['keyword'] = selected_keyword[0]
    production_info['asin'] = info_list[4]
    production_info['low_price'] = info_list[2]
    production_info['high_price'] = info_list[3]
    return asin, country, sections, keywords, production_info

def thead_alive_count(task_thread_gtoup = None):
    alive_count = 0
    select_thread = 0
    for i in range(len(task_thread_gtoup)):
        if task_thread_gtoup[i].is_alive():
            alive_count += 1
        else:
            select_thread = i
    return alive_count, select_thread


def task_cycle():
    #log_file_path = './logs/'
    #view_task_number = 15
    if not os.path.exists(print_path):
        os.mkdir(print_path)
    date_path = str(time.strftime("%Y%m%d", time.localtime()))
    log_file_handler = open(print_path + date_path + '.log', 'a')
    sys.stdout = log_file_handler

    # read info from csv file
    task_file = open(source_file_path, 'r', newline='')
    file_info = list(csv.reader(task_file))
    production_header = file_info[0]
    production_infos = file_info[1:]
    task_file.close()
    day_date = datetime.now().day
    production_number = len(production_infos)
    proxy_pool = []
    proxy_time = datetime.now()
    file_lock = threading.RLock()
    production_done_number = []
    for i in range(production_number):
        asin, country, sections, keywords, production_info = make_info(production_infos[i])
        counter_number = get_last_counter(log_file_path + date_path + '/' + country + '_' + asin + '.csv')
        production_done_number.append(counter_number)
        print('Counter number for '+ asin + '  is :' + str(counter_number))

    # update price
    task_thread = threading.Thread(target=update_price, args=(production_header, production_infos, day_date,))
    task_thread.setDaemon(daemonic=True)
    task_thread.start()

    task_thread_gtoup = []
    while True:
        for i in range(production_number):
            alive_count, select_thread = thead_alive_count(task_thread_gtoup)

            if change_mac == False:
                while alive_count >= view_task_number:
                    # print('Alive thread number is : ' + str(alive_count) + ' &&&&&&&&&&&&&&&&&&&&&&')
                    time.sleep(5)
                    alive_count, select_thread = thead_alive_count(task_thread_gtoup)
            else:
                # wait all thread done to reset Mac
                if alive_count >= view_task_number:
                    while alive_count:
                        time.sleep(5)
                        alive_count, select_thread = thead_alive_count(task_thread_gtoup)
                    # change Mac address
                    os.system("sudo spoof-mac.py randomize enp0s31f6")
                    os.system("sudo service networking restart")
                    print('Mac address changed!')
                    time.sleep(5)

            asin, country, sections, keywords, production_info = make_info(production_infos[i])
            date_path = str(time.strftime("%Y%m%d", time.localtime())) + '/'
            if sections > get_last_counter(log_file_path + date_path + country + '_' + asin + '.csv'):
                proxy_pool, proxy_time = get_proxy(proxy_pool, proxy_time)
                proxy = proxy_pool.pop() if proxy_pool else ''
                #print('Proxy poll left::: ' + str(proxy_pool) + '\n Get time :: ' + str(proxy_time.time()))
                #print('task info:::::' + str(production_info['asin']) + ' ####################### ' + proxy)
                try:
                    task_thread = threading.Thread(target=submit_task,
                                                   args=(production_info, proxy, file_lock), name=asin)
                    task_thread.setDaemon(daemonic=True)
                    task_thread.start()
                    if len(task_thread_gtoup) >= view_task_number:
                        task_thread_gtoup[select_thread] = task_thread
                    else:
                        task_thread_gtoup.append(task_thread)
                except:
                    print(traceback.print_exc())

            if day_date != datetime.now().day:
                print('Today is over, sorry...')
                sys.stdout = __console__
                log_file_handler.close()
                return

        alive_count, select_thread = thead_alive_count(task_thread_gtoup)
        if alive_count == 0:
            break

    print('View task done!!!!')
    sys.stdout = __console__
    log_file_handler.close()


def check_rank():
    #rank_task_number = 2
    # read info from csv file
    task_file = open(source_file_path, 'r', newline='')
    file_info = list(csv.reader(task_file))
    production_header = file_info[0]
    production_infos = file_info[1:]
    task_file.close()
    proxy_pool = []
    proxy_time = datetime.now()
    file_lock = threading.RLock()
    if not os.path.exists(print_path):
        os.mkdir(print_path)
    date_path = str(time.strftime("%Y%m%d", time.localtime()))
    log_file_handler = open(print_path + date_path + '_rank.log' , 'a')
    sys.stdout = log_file_handler

    check_list = []
    for i in range(len(production_header[8:])):
        for j in range(len(production_infos)):
            asin, country, sections, keywords, production_info = make_info(production_infos[j])
            if len(keywords) > i:
                production_info['keyword'] = keywords[i]
                production_info['rank'] = ''
                production_info['low_price'] = '0'
                production_info['high_price'] = '0'
                check_list.append(production_info)

    task_thread_gtoup = []
    day_date = datetime.now().day
    for test in range(rank_retry_num):
        for i in range(len(check_list)):
            if not check_list[i]['rank']:
                alive_count, select_thread = thead_alive_count(task_thread_gtoup)
                while alive_count >= rank_task_number:
                    time.sleep(5)
                    alive_count, select_thread = thead_alive_count(task_thread_gtoup)
                proxy_pool, proxy_time = get_proxy(proxy_pool, proxy_time, time_out = 120)
                proxy = proxy_pool.pop() if proxy_pool else ''
                print('task info:::::' + str(check_list[i]) + ' ####################### ' + proxy)
                try:
                    task_thread = threading.Thread(target=submit_rank_task, args=(check_list[i], proxy, file_lock),
                                                   name=asin)
                    task_thread.setDaemon(daemonic=True)
                    task_thread.start()
                    if len(task_thread_gtoup) >= rank_task_number:
                        task_thread_gtoup[select_thread] = task_thread
                    else:
                        task_thread_gtoup.append(task_thread)
                except:
                    print(traceback.print_exc())

            if day_date != datetime.now().day:
                print('Today is over, sorry...')
                sys.stdout = __console__
                log_file_handler.close()
                return

    print('All rank checked!!!')
    sys.stdout = __console__
    log_file_handler.close()


def task_status(select_date = ''):
    #log_file_path = './logs/'

    # read info from csv file
    task_file = open(source_file_path, 'r', newline='')
    production_infos = list(csv.reader(task_file))[1:]
    task_file.close()
    production_number = len(production_infos)
    for i in range(production_number):
        asin, country, sections, keywords, production_info = make_info(production_infos[i])
        counter_number = get_last_counter(log_file_path + select_date + '/' + country + '_' + asin + '.csv')
        print('Counter number for '+ asin + '  is :' + str(counter_number))

def task_buy():
    task_file = open(order_file_path, 'r', newline='')
    file_info = list(csv.reader(task_file))
    order_header = file_info[0]
    order_raw_infos = file_info[1:]
    order_queue = queue.Queue()
    for order_raw_info in order_raw_infos:
        order_queue.put(make_order_info(order_raw_info))
    task_file.close()
    proxy_pool = []
    proxy_time = datetime.now()
    file_lock = threading.RLock()
    if not os.path.exists(print_path):
        os.mkdir(print_path)
    date_path = str(time.strftime("%Y%m%d", time.localtime()))
    log_file_handler = open(print_path + date_path + '_order.log', 'a')
    #sys.stdout = log_file_handler

    task_thread_gtoup = []
    alive_count = 0
    while (not order_queue.empty()) or alive_count:
        alive_count, select_thread = thead_alive_count(task_thread_gtoup)
        if change_mac == False:
            while alive_count >= order_task_number:
                time.sleep(5)
                alive_count, select_thread = thead_alive_count(task_thread_gtoup)
        else:
            # wait all thread done to reset Mac
            if alive_count >= order_task_number:
                while alive_count:
                    time.sleep(5)
                    alive_count, select_thread = thead_alive_count(task_thread_gtoup)
                # change Mac address
                os.system("sudo spoof-mac.py randomize enp0s31f6")
                os.system("sudo service networking restart")
                print('Mac address changed!')
                time.sleep(5)
        file_lock.acquire()
        if order_queue.empty():
            continue
        select_order_info = order_queue.get()
        file_lock.release()
        if select_order_info['retrynumber'] >= order_retry_num:
            continue
        proxy_pool, proxy_time = get_proxy(proxy_pool, proxy_time, time_out=120)
        proxy = proxy_pool.pop() if proxy_pool else ''
        #proxy = ''
        print('task info:::::' + str(select_order_info['trackingnumber']) + ' ####################### ' + proxy)
        try:
            task_thread = threading.Thread(target=submit_order_task,
                                           args=(select_order_info, order_queue, proxy, file_lock),
                                           name=select_order_info['asin'])
            task_thread.setDaemon(daemonic=True)
            task_thread.start()
            if len(task_thread_gtoup) >= order_task_number:
                task_thread_gtoup[select_thread] = task_thread
            else:
                task_thread_gtoup.append(task_thread)
        except:
            print(traceback.print_exc())

        alive_count, select_thread = thead_alive_count(task_thread_gtoup)


def make_order_info(order_raw_info):
    order_info = {}
    order_info['username'] = order_raw_info[23]
    order_info['password'] = order_raw_info[24]
    order_info['cookies']  =order_raw_info[25]
    order_info['fullname'] = order_raw_info[8]
    order_info['address'] = order_raw_info[9]
    order_info['city'] = order_raw_info[11]
    order_info['state'] = order_raw_info[12]
    order_info['postalcode'] = order_raw_info[10]
    order_info['phonenumber'] = order_raw_info[13]
    order_info['country'] = 'us'
    order_info['department'] = order_raw_info[2]
    order_info['keyword'] = order_raw_info[7]
    order_info['asin'] = order_raw_info[6]
    order_info['low_price'] = order_raw_info[3]
    order_info['high_price'] = order_raw_info[3]
    order_info['ccnumber'] = order_raw_info[17]
    order_info['trackingnumber'] = order_raw_info[14]
    order_info['price'] = order_raw_info[5]
    order_info['gifcard'] = order_raw_info[16]
    order_info['reviewstar'] = 5 #order_raw_info[20]
    order_info['reviewheadline'] = order_raw_info[21]
    order_info['reviewcontent'] = order_raw_info[22]
    order_info['retrynumber'] = 0
    order_info['errorcode'] = 'Begin'
    return order_info


def task_review():
    task_file = open(order_file_path, 'r', newline='')
    file_info = list(csv.reader(task_file))
    order_header = file_info[0]
    order_raw_infos = file_info[1:]
    review_queue = queue.Queue()
    for order_raw_info in order_raw_infos:
        review_queue.put(make_order_info(order_raw_info))
    task_file.close()
    proxy_pool = []
    proxy_time = datetime.now()
    file_lock = threading.RLock()
    if not os.path.exists(print_path):
        os.mkdir(print_path)
    date_path = str(time.strftime("%Y%m%d", time.localtime()))
    log_file_handler = open(print_path + date_path + '_review.log', 'a')
    #sys.stdout = log_file_handler

    task_thread_gtoup = []
    alive_count = 0
    while (not review_queue.empty()) or alive_count:
        alive_count, select_thread = thead_alive_count(task_thread_gtoup)
        if change_mac == False:
            while alive_count >= review_task_number:
                time.sleep(5)
                alive_count, select_thread = thead_alive_count(task_thread_gtoup)
        else:
            # wait all thread done to reset Mac
            if alive_count >= review_task_number:
                while alive_count:
                    time.sleep(5)
                    alive_count, select_thread = thead_alive_count(task_thread_gtoup)
                # change Mac address
                os.system("sudo spoof-mac.py randomize enp0s31f6")
                os.system("sudo service networking restart")
                print('Mac address changed!')
                time.sleep(5)
        file_lock.acquire()
        if review_queue.empty():
            continue
        select_order_info = review_queue.get()
        file_lock.release()
        if select_order_info['retrynumber'] >= review_retry_num:
            continue
        proxy_pool, proxy_time = get_proxy(proxy_pool, proxy_time, time_out=120)
        proxy = proxy_pool.pop() if proxy_pool else ''
        #proxy = ''
        print('task info:::::' + str(select_order_info['trackingnumber']) + ' ####################### ' + proxy)
        try:
            task_thread = threading.Thread(target=submit_review_task,
                                           args=(select_order_info, review_queue, proxy, file_lock),
                                           name=select_order_info['asin'])
            task_thread.setDaemon(daemonic=True)
            task_thread.start()
            if len(task_thread_gtoup) >= review_task_number:
                task_thread_gtoup[select_thread] = task_thread
            else:
                task_thread_gtoup.append(task_thread)
        except:
            print(traceback.print_exc())

        alive_count, select_thread = thead_alive_count(task_thread_gtoup)

def task_validate_account():
    pass

def EnableCodeLog(enable = True):
    if enable:
        if not os.path.exists(print_path):
            os.mkdir(print_path)
        date_path = str(time.strftime("%Y%m%d", time.localtime()))
        log_file_handler = open(print_path + date_path + '_review.log', 'a')
        sys.stdout = log_file_handler
    else:
        sys.stdout = __console__

def TaskManeger(task_number = 1, target=submit_review_task, args= '', tasksync = False):
    task_thread_gtoup = []
    alive_count = 0
    task_queue = queue.Queue()
    file_lock = threading.RLock()

    while (not task_queue.empty()) or alive_count:
        alive_count, select_thread = thead_alive_count(task_thread_gtoup)
        if tasksync:
            # execute task when task pool not full
            while alive_count >= task_number:
                time.sleep(5)
                alive_count, select_thread = thead_alive_count(task_thread_gtoup)
        else:
            # wait all thread done to reset Mac
            if alive_count >= task_number:
                while alive_count:
                    time.sleep(5)
                    alive_count, select_thread = thead_alive_count(task_thread_gtoup)
                # change Mac address
                os.system("sudo spoof-mac.py randomize enp0s31f6")
                os.system("sudo service networking restart")
                print('Mac address changed!')
                time.sleep(5)
        file_lock.acquire()
        if review_queue.empty():
            continue
        select_order_info = review_queue.get()
        file_lock.release()
        if select_order_info['retrynumber'] >= review_retry_num:
            continue
        proxy_pool, proxy_time = get_proxy(proxy_pool, proxy_time, time_out=120)
        proxy = proxy_pool.pop() if proxy_pool else ''
        # proxy = ''
        print('task info:::::' + str(select_order_info['trackingnumber']) + ' ####################### ' + proxy)
        try:
            task_thread = threading.Thread(target=target,
                                           args=(args, review_queue, proxy, file_lock),
                                           name=select_order_info['asin'])
            task_thread.setDaemon(daemonic=True)
            task_thread.start()
            if len(task_thread_gtoup) >= review_task_number:
                task_thread_gtoup[select_thread] = task_thread
            else:
                task_thread_gtoup.append(task_thread)
        except:
            print(traceback.print_exc())

        alive_count, select_thread = thead_alive_count(task_thread_gtoup)

def task_modify_account():
    proxy_pool = []
    proxy_time = datetime.now()
    file_lock = threading.RLock()
    EnableCodeLog()


def task_add_cart():
    pass

if __name__ == "__main__":
    rank_task_number = 14
    view_task_number = 24
    order_task_number = 2
    review_task_number = 2


    print('*********************************************')
    print('*          please select function           *')
    print('*   1. View production                      *')
    print('*   2. Rank production                      *')
    print('*   3. Show status                          *')
    print('*   4. Buy production                       *')
    print('*   5. Add reviewer                         *')
    print('*   6. Validate account                     *')
    print('*   7. Modify account                       *')
    print('*   8. Add cart brfore order                *')
    print('*********************************************')
    func_select = input()

    print('select contry::: ca / us / uk')
    country = input()
    if country == 'ca':
        source_file_path = './ca.csv'
        print('CA selected...')
    elif country == 'uk':
        source_file_path = './uk.csv'
        print('UK selected...')
    else:
        source_file_path = './us.csv'
        print('US selected...')

    if func_select == '1':
        while True:
            task_cycle()
            while datetime.now().hour != 0:
                print('Wait for next day!!!')
                time.sleep(60)
    elif func_select == '2':
        while True:
            check_rank()
            while datetime.now().hour != 0:
                print('Wait for next day!!!')
                time.sleep(60)
    elif func_select == '4':
        task_buy()
    elif func_select == '5':
        task_review()
    elif func_select == '6':
        task_validate_account()
    elif func_select == '7':
        task_modify_account()
    elif func_select == '8':
        task_add_cart()
    else:
        print('Date select (YYYYMMDD): ')
        select_date = input()
        if not select_date:
            select_date = str(time.strftime("%Y%m%d", time.localtime()))
        task_status(select_date)


