from taskmanager import TaskManager
from amazon_function import AmazonFunction
import csv
import time
import json
import random
from random import randint
from datetime import datetime
import pandas as pd
import traceback


ReviewerFile = './amazonbuy_database/review.csv'
AccountFile     = './amazonbuy_database/AccountInfo.csv'

ReviewerFrame = pd.DataFrame(pd.read_csv(ReviewerFile,header=0, dtype=str))
ReviewerFrame.dropna(how='all', inplace=True)
ReviewerFrame.dropna(axis=1, how='any', inplace=True)
ReviewerFrame.fillna('',inplace=True)

AccountFrame = pd.DataFrame(pd.read_csv(AccountFile,header=0, dtype=str,sep=','))
AccountFrame.drop_duplicates(subset='username', inplace=True)
AccountFrame.dropna(how='all', inplace=True)
#AccountFrame.dropna(axis=1, how='all', inplace=True)
#AccountFrame.dropna(how='any', inplace=True)
AccountFrame.fillna('',inplace=True)
AccountFrame.set_index('username', inplace=True)


class Review(TaskManager):
    def __init__(self):
        TaskManager.__init__(self)
        self.ReportInfo = ['username', 'password','cookies', 'asin', 'reviewstar', 'reviewertitle', 'reviewercontent', 'Timestamp']
        self.ReportErrorInfo = ['errorcode', 'retrynumber']
        self.FatalError = ['BadPassword', 'BadEmail']
        self.TaskSync = False
        self.CodeLogEn(False)
        self.ThreadNumber = 5
        self.MaxRetry = 5
        self.LoadImage = False
        self.ProxyEnable = True
        self.ProxyTimeout = 60
        self.TaskName = 'SubmitReviewer'
        self.submitedUser = []
        self.TaskInfos = []
        for name, item in ReviewerFrame.iterrows():
            self.TaskInfos.append(item.to_dict())
        pass

    def SubTaskFinal(self, TaskInfo):
        if TaskInfo['Logout']:
            try:
                self.submitedUser.remove(TaskInfo['username'])
            except:
                print(traceback.print_exc())
                pass

    # overiding method
    def SubTask(self, driver, TaskInfo):
        driver.implicitly_wait(5)
        TaskInfo['Logout'] = True
        TaskInfo['cookies'] = AccountFrame.loc[TaskInfo['username']]['cookies']
        while TaskInfo['username'] in self.submitedUser:
            time.sleep(30)
            print('Reviewer waits for: ' + TaskInfo['username'] + ' :: ' + TaskInfo['asin'])
        print('Reviewer begins for: ' + TaskInfo['username'] + ' :: ' + TaskInfo['asin'])
        self.submitedUser.append(TaskInfo['username'])
        Task = AmazonFunction(driver, TaskInfo)
        if not Task.login():
            self.TaskLog(TaskInfo)
            return False
        if not Task.GoToReview():
            self.TaskLog(TaskInfo)
            return False
        if Task.WriteReview():
            print('Reviewer added for: ' + TaskInfo['username'] + ' :: ' + TaskInfo['asin'])
        else:
            print('Reviewer fail for: ' + TaskInfo['username'] + ' :: ' + TaskInfo['asin'])
        #TaskInfo['cookies'] = json.dumps(driver.get_cookies())



if __name__ == "__main__":
    Task = Review()
    Task.TaskManage()
