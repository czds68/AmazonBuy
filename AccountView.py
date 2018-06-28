from taskmanager import TaskManager
from amazon_function import AmazonFunction
from amazon_pages import AmazonPages
import csv
import time
import json
import random
#import parseinfo
import traceback
from random import randint
from datetime import datetime
import pandas as pd

FinanceFile     = './amazonbuy_database/Finance.csv'
AddressFile     = './amazonbuy_database/shippingaddress.csv'
ProductFile     = './amazonbuy_database/productinfo.csv'
AccountFile = './amazonbuy_database/AccountInfo.csv'

AccountFrame = pd.DataFrame(pd.read_csv(AccountFile,header=0, dtype=str,sep=','))
AccountFrame.drop_duplicates(subset='username', inplace=True)
AccountFrame.dropna(how='all', inplace=True)
#AccountFrame.dropna(axis=1, how='all', inplace=True)
#AccountFrame.dropna(how='any', inplace=True)
AccountFrame.fillna('',inplace=True)
AccountTable = []
for num, item in AccountFrame.iterrows():
    AccountTable.append(item.to_dict())

AddressFrame = pd.DataFrame(pd.read_csv(AddressFile,header=0, dtype=str))
AddressFrame.dropna(how='all', inplace=True)
AddressFrame.dropna(axis=1, how='any', inplace=True)
AddressFrame.dropna(how='all', inplace=True)
AddressFrame.fillna(value='',inplace=True)
AddressFrame.set_index('username', inplace=True)

FinanceFrame = pd.DataFrame(pd.read_csv(FinanceFile,header=0, dtype=str))
FinanceFrame.drop_duplicates(inplace=True)
FinanceFrame.dropna(how='all', inplace=True)
FinanceFrame.dropna(axis=1, how='all', inplace=True)
#FinanceFrame.dropna(how='any', inplace=True)
FinanceFrame.fillna(value='',inplace=True)
FinanceFrame.set_index('username', inplace=True)

ProductFrame = pd.DataFrame(pd.read_csv(ProductFile,header=0, dtype=str))
ProductFrame.drop_duplicates(subset='asin', inplace=True)
ProductFrame.dropna(how='all', inplace=True)
ProductFrame.dropna(axis=1, how='all', inplace=True)
#ProductFrame.dropna(how='any', inplace=True)
ProductFrame.fillna(value='',inplace=True)
ProductFrame.set_index('asin', inplace=True)

# check whether already placed order

class PlaceOrder(TaskManager):
    def __init__(self):
        TaskManager.__init__(self)
        self.ReportInfo = ['username', 'password', 'cookies', 'proxy', 'Timestamp']
        self.ReportErrorInfo = ['errorcode', 'retrynumber']
        self.FatalError = ['VerifyEmail', 'BadPassword']
        self.TaskSync = False
        self.CodeLogEn(False)
        self.ThreadNumber = 1
        self.MaxRetry = 3
        self.ProxyEnable = True
        self.AuthProxy = True
        self.ProxyTimeout = 60
        self.SubMaxRetry = 2
        self.TaskName = 'Account View'
        self.TaskInfos = AccountTable
        for item in self.TaskInfos:
            item.update({'cookies': ''})
            item.update(AccountFrame.loc[item['username']].to_dict())
            item.update({'billingaddress':FinanceFrame.loc[item['username']].to_dict()})
            item.update({'shippingaddress':AddressFrame.loc[item['username']].to_dict()})
        pass

    # overiding method
    def SubTask(self, driver, TaskInfo):
        driver.implicitly_wait(5)
        Task = AmazonFunction(driver, TaskInfo)
        TaskInfo['ordernumber'] = ''
        Task.FunctionInfo.update(TaskInfo['shippingaddress'])
        Task.NewRandomAccount = False
        Task.speed = randint(50, 100)
        EmailDomain = '@foxairmail.com'
        if not Task.login():
            return False
        time.sleep(5)
        Task.FunctionInfo.update(TaskInfo['billingaddress'])
        Viewpages = AmazonPages(driver)
        for i in range(randint(2,6)):
            Viewpages.RandomClick()
            Viewpages.WalkAround(ScrollSpeed=[5,20])
            time.sleep(randint(5,15))
        TaskInfo['cookies'] = json.dumps(driver.get_cookies())
        return True

if __name__ == "__main__":
    while True:
        SelectTime = randint(5, 23)
        while datetime.now().hour != SelectTime:
            print('Wait for the time!!!')
            time.sleep(60)
        Task = PlaceOrder()
        Task.TaskManage()
        while datetime.now().hour != 0:
            print('Wait for next day!!!')
            time.sleep(60)
