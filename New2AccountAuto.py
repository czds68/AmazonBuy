from taskmanager import TaskManager
from amazon_function import AmazonFunction
import csv
import time
import json
import random
#import parseinfo
from random import randint
from datetime import datetime
import pandas as pd

AccountFile     = './amazonbuy_database/AccountInfo.csv'
FinanceFile     = './amazonbuy_database/Finance.csv'
AddressFile     = './amazonbuy_database/shippingaddress.csv'
OrderTaskFile   = './amazonbuy_database/ordertask.csv'
ProductFile     = './amazonbuy_database/productinfo.csv'

AccountFrame = pd.DataFrame(pd.read_csv(AccountFile,header=0, dtype=str,sep=','))
AccountFrame.drop_duplicates(subset='username', inplace=True)
AccountFrame.dropna(how='all', inplace=True)
#AccountFrame.dropna(axis=1, how='all', inplace=True)
#AccountFrame.dropna(how='any', inplace=True)
AccountFrame.fillna(value='',inplace=True)

AddressFrame = pd.DataFrame(pd.read_csv(AddressFile,header=0, dtype=str))
AddressFrame.dropna(how='all', inplace=True)
AddressFrame.dropna(axis=1, how='any', inplace=True)
AddressFrame.dropna(how='all', inplace=True)
AddressFrame.fillna(value='',inplace=True)

OrderTaskFrame = pd.DataFrame(pd.read_csv(OrderTaskFile,header=0, dtype=str))
OrderTaskFrame.dropna(how='all', inplace=True)
OrderTaskFrame.dropna(axis=1, how='all', inplace=True)
OrderTaskTable = []
for name, item in OrderTaskFrame.iterrows():
    item.dropna(inplace=True)
    item.drop(['username'], inplace=True)
    OrderTaskInfo = {'asins': list(item)}
    OrderTaskTable.append(OrderTaskInfo)

FinanceFrame = pd.DataFrame(pd.read_csv(FinanceFile,header=0, dtype=str))
FinanceFrame.drop_duplicates(inplace=True)
FinanceFrame.dropna(how='all', inplace=True)
FinanceFrame.dropna(axis=1, how='all', inplace=True)
FinanceFrame.dropna(how='any', inplace=True)
FinanceFrame.fillna(value='',inplace=True)

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
        self.ReportInfo = ['username', 'password', 'cookies','fullname','address','postalcode','city','state','phonenumber', 'Timestamp', 'ordernumber', 'asins']
        self.ReportErrorInfo = ['errorcode', 'retrynumber']
        self.FatalError = ['VerifyEmail', 'BadPassword', 'FixAddress', 'AddressNotMatch', 'GiftCardUsed', 'BadGiftCard']
        self.TaskSync = False
        self.CodeLogEn(False)
        self.ThreadNumber = 1
        self.MaxRetry = 3
        self.ProxyEnable = True
        self.ProxyTimeout = 60
        self.TaskName = 'PlaceOrder_auto'
        self.TaskInfos = OrderTaskTable
        for i in range(len(self.TaskInfos)):
            self.TaskInfos[i].update(AccountFrame.loc[i].to_dict())
            self.TaskInfos[i].update({'billingaddress':FinanceFrame.loc[i].to_dict()})
            self.TaskInfos[i].update({'shippingaddress':AddressFrame.loc[i].to_dict()})
        pass


    # overiding method
    def SubTask(self, driver, TaskInfo):
        driver.implicitly_wait(5)
        Task = AmazonFunction(driver, TaskInfo)
        TaskInfo['ordernumber'] = ''
        Task.FunctionInfo.update(TaskInfo['shippingaddress'])
        Task.speed = randint(50, 100)
        if not Task.login():
            return False
        time.sleep(5)
        Task.FunctionInfo.update(TaskInfo['billingaddress'])
        if not Task.AddCreditCard():
            print('Credit Card add fail for: ' + TaskInfo['username'])
            return False
        Task.FunctionInfo.update(TaskInfo['shippingaddress'])
        if not Task.SetAddress():
            return False
        for asin in TaskInfo['asins']:
            Task.FunctionInfo['asin'] = asin
            Task.FunctionInfo.update(ProductFrame.loc[Task.FunctionInfo['asin']].to_dict())
            Task.FunctionInfo['lowprice'] = str(round((float(Task.FunctionInfo['buyboxprice']) - 0.02), 2))
            Task.FunctionInfo['highprice'] = str(round((float(Task.FunctionInfo['buyboxprice']) + 0.01), 2))
            #Task.FunctionInfo['lowprice'] = Task.FunctionInfo['buyboxprice']
            #Task.FunctionInfo['highprice'] = Task.FunctionInfo['buyboxprice']
            if not Task.SearchProduct():
                print('Search production fail...')
                # Fatal error if not found in any page  TBD
                TaskInfo['errorcode'] = 'SearchFail'
                TaskInfo['status'] = False
                return False
            if not Task.AddCart():
                print('Add cart fail...')
                # Fatal error if not found TBD
                return False
        if not Task.PlaceOrder():
            return False
        TaskInfo['cookies'] = json.dumps(driver.get_cookies())
        return True

if __name__ == "__main__":
    Task = PlaceOrder()
    Task.TaskManage()