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
from AmazonDatabaseAccess import amazon_db
from AmazonTables import GetMacAddress



MACAddress = GetMacAddress()
#MACAddress = 'F4:0F:24:05:D2:6A'
db = amazon_db()
db.open()
rslt = db.accountinfo_get_item()

AccountTable = []
for item in rslt:
    print(item)
    acountinfo = {}
    acountinfo.update({'username': item[1],
                       'password':item[2],
                       'cookies': item[3],
                       'createdate':item[4],
                       'logindate':item[5],
                       'lastbuy':item[6],
                       'in_use':item[7],
                       'alive':item[8],
                       'MAC': MACAddress})
    AccountTable.append(acountinfo)
db.close()
del db

'''
def accountinfo_update_item(
        self,
        username,
        password,
        cookies,
        createdate,
        logindate,
        lastbuy,
        in_use,
        alive,
        MAC,
):
'''

class AccountView(TaskManager):
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
        TaskInfo['logindate'] = datetime()
        db = amazon_db()
        db.open()
        db.accountinfo_update_item(
            TaskInfo['username'],
            TaskInfo['password'],
            TaskInfo['cookies'],
            TaskInfo['createdate'],
            TaskInfo['logindate'],
            TaskInfo['lastbuy'],
            TaskInfo['in_use'],
            TaskInfo['alive'],
            TaskInfo['MAC'],)
        db.close()
        del db
        return True

if __name__ == "__main__":
    while True:
        SelectTime = randint(5, 23)
        while datetime.now().hour != SelectTime:
            print('Wait for the time!!!')
            time.sleep(60)
        Task = AccountView()
        Task.TaskManage()
        while datetime.now().hour != 0:
            print('Wait for next day!!!')
            time.sleep(60)
