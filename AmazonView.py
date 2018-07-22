from taskmanager import TaskManager
from amazon_function import AmazonFunction
from amazon_pages import AmazonPages
import csv
import time
import json
import random
#import parseinfo
from random import randint
from datetime import datetime
import pandas as pd
import os
import threading
import AmazonTables
import traceback


LogFilePath = './logs/'
ProductFile     = './amazonbuy_database/view.csv'

ProductFrame = pd.DataFrame(pd.read_csv(ProductFile,header=0, dtype=str))
ProductFrame.dropna(how='all', inplace=True)
#ProductFrame.dropna(axis=1, how='all', inplace=True)
#ProductFrame.dropna(how='any', inplace=True)
ProductFrame.fillna(value='',inplace=True)
ProductTable = []
for num, item in ProductFrame.iterrows():
    item.dropna(inplace=True)
    ProductInfo={}
    ProductInfo.update(ProductFrame.loc[num].to_dict())
    ProductTable.append(ProductInfo)


class ViewTask(TaskManager):
    def __init__(self):
        TaskManager.__init__(self)
        self.ReportInfo = ['Timestamp', 'department', 'asin', 'keyword', 'lowprice', 'highprice', 'buyboxprice', 'country', 'taskid']
        self.ReportErrorInfo = ['errorcode', 'retrynumber']
        self.FatalError = ['OverDay']
        self.TaskSync = False
        self.CodeLogEn(False)
        self.ThreadNumber = 15
        self.MaxRetry = 3
        self.AuthProxy = False
        self.ProxyEnable = True
        self.ProxyTimeout = 60
        self.day_date = datetime.now().day
        self.TaskName = 'ViewTask'
        self.TaskSummury = ProductTable
        self.TaskInfos = []
        for item in ProductTable:
            for i in range(int(item['sections'])):
                TaskInfo = {'taskid': i}
                TaskInfo.update(item)
                keywordSelect = ['Keywords1', 'Keywords2', 'Keywords3', 'Keywords4', 'Keywords5', 'Keywords6',
                                 'Keywords7',
                                 'Keywords8', 'Keywords9', 'Keywords10']
                keywordGoup = []
                for key in keywordSelect:
                    if key in item:
                        if item[key]:
                            keywordGoup.append(item[key])
                random.shuffle(keywordGoup)
                TaskInfo.update({'keyword': keywordGoup[0]})
                self.TaskInfos.append(TaskInfo)
        random.shuffle(self.TaskInfos)
        pass


    def updateprice(self, TaskSummury, retrycnt = 3):
        while True:
            print('Begin to update price...')
            for item in TaskSummury:
                for i in range(retrycnt):
                    try:
                        proxy = self.GetProxy()
                        driver = self.WebDriver(proxy)
                        print('Update price for ' + item['asin'])
                        production_url = AmazonTables.URLDomains(item['country']) + 'gp/product/' + item['asin']
                        TASK = AmazonFunction(driver,FunctionInfo=item)
                        price = TASK.check_price(production_url)
                        driver.delete_all_cookies()
                        driver.quit()
                    except:
                        print(traceback.print_exc())
                        time.sleep(30)
                        continue
                    if price:
                        item.update(price)
                        break
                    else:
                        print('Price update for ' + item['asin'] + ' failed!')
            time.sleep(30)
            print('Update price done...')
            time.sleep(7200)

    def UpdatePriceTask(self):
        # update price
        task_thread = threading.Thread(target=self.updateprice, args=(self.TaskSummury, 3))
        task_thread.setDaemon(daemonic=True)
        task_thread.start()

    # write log
    def TaskLog(self, TaskInfo):
        self.FileLock.acquire()
        TaskInfo['Timestamp'] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        LogInfo = []
        for item in self.ReportInfo:
            LogInfo.append(TaskInfo[item])
        if TaskInfo['status']:
            FilePath = LogFilePath + self.DatePath + self.TaskName + TaskInfo['asin'] + '.csv'
        else:
            for item in self.ReportErrorInfo:
                LogInfo.append(TaskInfo[item])
            FilePath = LogFilePath + self.DatePath + self.TaskName + TaskInfo['asin'] + '_fail.csv'
        if not os.path.exists(FilePath):
            OpenFile = open(FilePath, "a")
            WriteFile = csv.writer(OpenFile)
            if TaskInfo['status']:
                WriteFile.writerow(self.ReportInfo)
            else:
                WriteFile.writerow(self.ReportInfo + self.ReportErrorInfo + ['FatalError'])
        else:
            OpenFile = open(FilePath, "a")
            WriteFile = csv.writer(OpenFile)
        WriteFile.writerow(LogInfo)
        OpenFile.close()
        self.FileLock.release()

    # task in Main thread
    def InMianTask(self):
        if self.day_date != datetime.now().day:
            self.FileLock.acquire()
            self.TaskQueue.queue.clear()
            self.FileLock.release()
            return True

    # overiding method
    def SubTask(self, driver, TaskInfo):
        driver.implicitly_wait(10)
        for item in self.TaskSummury:
            if TaskInfo['asin'] == item['asin'] and TaskInfo['country'] == item['country']:
                TaskInfo.update(item)
        try:
            driver.get(AmazonTables.URLDomains(item['country']))
            time.sleep(20)
        except:
            TaskInfo['status'] = False
            TaskInfo['errorcode'] = 'URLDomainFail'
            return False
        Task.speed = randint(40, 80)
        SearchTask = AmazonPages(driver)
        if SearchTask.SearchAndView(TaskInfo, timer = randint(90,120)):
            print('View page done.')
            return True
        else:
            return False



if __name__ == "__main__":
    Task = ViewTask()
    Task.UpdatePriceTask()
    while True:
        Task.day_date = datetime.now().day
        Task.TaskManage()
        while Task.day_date == datetime.now().day:
            print('Wait for next day!!!')
            time.sleep(60)