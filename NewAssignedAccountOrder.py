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
OrderTaskFile   = './amazonbuy_database/ordertask.csv'
ProductFile     = './amazonbuy_database/productinfo.csv'
AccountFile = './amazonbuy_database/AccountInfo.csv'

AccountFrame = pd.DataFrame(pd.read_csv(AccountFile,header=0, dtype=str,sep=','))
AccountFrame.drop_duplicates(subset='username', inplace=True)
AccountFrame.dropna(how='all', inplace=True)
#AccountFrame.dropna(axis=1, how='all', inplace=True)
#AccountFrame.dropna(how='any', inplace=True)
AccountFrame.fillna('',inplace=True)
AccountFrame.set_index('username', inplace=True)

AddressFrame = pd.DataFrame(pd.read_csv(AddressFile,header=0, dtype=str))
AddressFrame.dropna(how='all', inplace=True)
AddressFrame.dropna(axis=1, how='any', inplace=True)
AddressFrame.dropna(how='all', inplace=True)
AddressFrame.fillna(value='',inplace=True)
AddressFrame.set_index('username', inplace=True)

OrderTaskFrame = pd.DataFrame(pd.read_csv(OrderTaskFile,header=0, dtype=str))
OrderTaskFrame.dropna(how='all', inplace=True)
OrderTaskFrame.dropna(axis=1, how='all', inplace=True)
OrderTaskFrame.set_index('username', inplace=True)
OrderTaskTable = []
for name, item in OrderTaskFrame.iterrows():
    OrderTaskInfo = {}
    OrderTaskInfo['username'] = name
    item.dropna(inplace=True)
    OrderTaskInfo['asins'] =  list(item)
    OrderTaskTable.append(OrderTaskInfo)

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
        self.ReportInfo = ['username', 'password', 'cookies', 'proxy','billingaddress','shippingaddress', 'Timestamp', 'ordernumber', 'asins']
        self.ReportErrorInfo = ['errorcode', 'retrynumber']
        self.FatalError = ['VerifyEmail', 'BadPassword', 'FixAddress', 'AddressNotMatch', 'GiftCardUsed', 'BadGiftCard']
        self.TaskSync = False
        self.CodeLogEn(False)
        self.ThreadNumber = 1
        self.MaxRetry = 3
        self.ProxyEnable = True
        self.AuthProxy = True
        self.ProxyTimeout = 60
        self.SubMaxRetry = 2
        self.TaskName = 'PlaceOrder_auto'
        self.TaskInfos = OrderTaskTable
        tt = AccountFrame
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
        if not Task.CreatAcount(EmailDomain):
            return False
        time.sleep(5)
        Task.FunctionInfo.update(TaskInfo['billingaddress'])
        SubRetry = 0
        while not Task.AddCreditCard():
            SubRetry += 1
            if SubRetry > self.SubMaxRetry:
                print('Credit Card add fail for: ' + TaskInfo['username'])
                return False
        Task.FunctionInfo.update(TaskInfo['shippingaddress'])
        SubRetry = 0
        while not Task.SetAddress():
            SubRetry += 1
            if SubRetry > self.SubMaxRetry:
                print(traceback.print_exc())
                return False
        SearchTask = AmazonPages(driver)
        for asin in TaskInfo['asins']:
            Task.FunctionInfo['asin'] = asin
            Task.FunctionInfo.update(ProductFrame.loc[Task.FunctionInfo['asin']].to_dict())
            Task.FunctionInfo['lowprice'] = str(round((float(Task.FunctionInfo['buyboxprice']) - 0.03), 2))
            Task.FunctionInfo['highprice'] = str(round((float(Task.FunctionInfo['buyboxprice']) + 0.02), 2))
            #Task.FunctionInfo['lowprice'] = Task.FunctionInfo['buyboxprice']
            #Task.FunctionInfo['highprice'] = Task.FunctionInfo['buyboxprice']
            SubRetry = 0
            while not SearchTask.SearchAndView(TaskInfo):
                SubRetry += 1
                if SubRetry > self.SubMaxRetry:
                    print('Search production fail...')
                    # Fatal error if not found in any page  TBD
                    TaskInfo['errorcode'] = 'SearchFail'
                    TaskInfo['status'] = False
                    return False
            SubRetry = 0
            while not Task.AddCart():
                SubRetry += 1
                if SubRetry > self.SubMaxRetry:
                    print('Add cart fail...')
                    # Fatal error if not found TBD
                    return False
        SubRetry = 0
        while not Task.PlaceOrder():
            SubRetry += 1
            if SubRetry > self.SubMaxRetry:
                return False
        TaskInfo['cookies'] = json.dumps(driver.get_cookies())
        return True

if __name__ == "__main__":
    Task = PlaceOrder()
    Task.TaskManage()