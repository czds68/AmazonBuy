from taskmanager import TaskManager
from amazon_function import AmazonFunction
import csv
import time
import json
import random
import parseinfo
from random import randint
from datetime import datetime
from amazon_pages import AmazonPages

def make_order_info_0(RawInfo):
    order_info = {}
    order_info['ordernumber'] = ''
    return order_info

def make_order_info_1(RawInfo):
    order_info = {}
    order_info['newemail'] = ''
    return order_info


AccountFile = './order.csv'

class VerifyAccount(TaskManager):
    def __init__(self):
        TaskManager.__init__(self)
        self.ReportInfo = ['username', 'password', 'cookies','errorcode']
        self.ReportErrorInfo = ['retrynumber']
        self.FatalError = ['BadPassword', 'BadEmail']
        self.TaskSync = False
        self.CodeLogEn(False)
        self.ThreadNumber = 3
        self.MaxRetry = 3
        self.ProxyEnable = True
        self.TaskName = 'VerifyAccount'
        self.WalkaroundEn = True
        self.TaskInfos = parseinfo.AccountTable

    # overiding method
    def SubTask(self, driver, TaskInfo):
        Task = AmazonFunction(driver, TaskInfo)
        Task.VerifyEnhance = True
        if Task.login():
            try:
                driver.get("https://www.amazon.com/")
                time.sleep(5)
            except:
                pass
            if self.WalkaroundEn:
                Task.Walkaround()
            TaskInfo['cookies'] = json.dumps(driver.get_cookies())
        else:
            TaskInfo['cookies'] = ''
        pass


class ModifyAcount(TaskManager):
    def __init__(self):
        TaskManager.__init__(self)
        self.ReportInfo = ['newemail', 'newpassword', 'newcookies', 'Timestamp', 'username']
        self.ReportErrorInfo = ['errorcode', 'retrynumber']
        self.FatalError = ['BadPassword', 'BadEmail', 'VerifyEmail']
        self.TaskSync = False
        self.CodeLogEn(False)
        self.ThreadNumber = 1
        self.MaxRetry = 3
        self.ProxyEnable = False
        self.TaskName = 'ModifyAcount'
        self.TaskInfos = parseinfo.AccountTable

    # overiding method
    def SubTask(self, driver, TaskInfo):
        TaskInfo['newcookies'] = ''
        TaskInfo['newemail'] = ''
        TaskInfo['newepassword'] = ''
        Task = AmazonFunction(driver, TaskInfo)
        if not Task.login():
            print('Login fail...')
            return False
        if not Task.SecurityPage():
            return False
        EmailDomain = '@foxairmail.com'
        if not Task.ChangeEmail(EmailDomain):
            return False
        if not Task.ChangePassword():
            return False
        #TaskInfo['newemail'] = TaskInfo['username']
        TaskInfo['newcookies'] = json.dumps(driver.get_cookies())

class PrepareOrder(TaskManager):
    def __init__(self):
        TaskManager.__init__(self)
        self.ReportInfo = ['Timestamp', 'username', 'asins']
        self.ReportErrorInfo = ['errorcode', 'retrynumber']
        self.FatalError = ['VerifyEmail', 'FixAddress', 'AddressNotMatch', 'GiftCardUsed', 'BadGiftCard']
        self.TaskSync = False
        self.CodeLogEn(False)
        self.ThreadNumber = 5
        self.MaxRetry = 5
        self.ProxyEnable = True
        self.TaskName = 'PrepareOrder'
        self.TaskInfos = parseinfo.OrderTaskTable
        for item in self.TaskInfos:
            item.update(parseinfo.AccountFrame.loc[item['username']].to_dict())
            item.update(parseinfo.AddressFrame.loc[item['username']].to_dict())

    # overiding method
    def SubTask(self, driver, TaskInfo):
        Task = AmazonFunction(driver, TaskInfo)
        Task.speed = randint(100, 160)
        if not Task.login():
            return False
        time.sleep(5)
        if not Task.CleanCart():
            return False
        if not Task.SetAddress():
            return False

        for asin in TaskInfo['asins']:
            Task.FunctionInfo['asin'] = asin
            Task.FunctionInfo.update(parseinfo.ProductFrame.loc[Task.FunctionInfo['asin']].to_dict())
            Task.FunctionInfo['lowprice'] = str(round((float(Task.FunctionInfo['buyboxprice']) - 0.01), 2))
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
        return True

class PlaceOrder(TaskManager):
    def __init__(self):
        TaskManager.__init__(self)
        self.ReportInfo = [ 'Timestamp', 'username', 'ordernumber', 'asins']
        self.ReportErrorInfo = ['errorcode', 'retrynumber']
        self.FatalError = ['VerifyEmail', 'AddressShallUpdate', 'AddressNoShipped']
        self.TaskSync = False
        self.CodeLogEn(False)
        self.ThreadNumber = 3
        self.MaxRetry = 5
        self.ProxyEnable = True
        self.TaskName = 'PlaceOrder'
        self.TaskInfos = parseinfo.OrderTaskTable
        for item in self.TaskInfos:
            item.update(parseinfo.AccountFrame.loc[item['username']].to_dict())
            #item.update(parseinfo.GiftCardFrame.loc[item['username']].to_dict())
            item.update(parseinfo.AddressFrame.loc[item['username']].to_dict())

    # overiding method
    def SubTask(self, driver, TaskInfo):
        Task = AmazonFunction(driver, TaskInfo)
        TaskInfo['ordernumber'] = ''
        if not Task.login():
            return False
        Task.PlaceOrder()

class TestSearch(TaskManager):
    def __init__(self):
        TaskManager.__init__(self)
        self.ReportInfo = [ 'asin', 'department', 'buyboxprice', 'orderprice', 'keyword', 'brand', 'Timestamp']
        self.ReportErrorInfo = ['errorcode', 'retrynumber']
        self.FatalError = ['']
        self.TaskSync = False
        self.CodeLogEn(False)
        self.ThreadNumber = 5
        self.MaxRetry = 3
        self.ProxyEnable = False
        self.TaskName = 'TestSearch'
        self.TaskInfos = []
        parseinfo.ProductFrame.reset_index(inplace=True)
        for i in range(parseinfo.ProductFrame.shape[0]):
            ProductInfo = parseinfo.ProductFrame.loc[i]
            ProductInfo.dropna(inplace=True)
            self.TaskInfos.append(ProductInfo.to_dict())

    # overiding method
    def SubTask(self, driver, TaskInfo):
        driver.get("https://www.amazon.com/")
        time.sleep(10)
        Task = AmazonFunction(driver, TaskInfo)
        Task.speed = randint(120, 160)
        Task.FunctionInfo['lowprice'] = str(round((float(Task.FunctionInfo['buyboxprice']) - 0.01), 2))
        Task.FunctionInfo['highprice'] = str(round((float(Task.FunctionInfo['buyboxprice']) + 0.01), 2))
        SearchTask = AmazonPages(driver)
        #if not Task.SearchProduct():
        if not SearchTask.SearchAndView(TaskInfo):
            print('Search production fail...')
            # Fatal error if not found in any page  TBD
            TaskInfo['errorcode'] = 'SearchFail'
            TaskInfo['status'] = False
            return False
        if not Task.AddCart():
            print('Add cart fail...')
            return False
        return True

class Review(TaskManager):
    def __init__(self):
        TaskManager.__init__(self)
        self.ReportInfo = ['reviewerid', 'asin', 'reviewstar', 'reviewertitle', 'reviewercontent', 'reviewerusername', 'Timestamp']
        self.ReportErrorInfo = ['errorcode', 'retrynumber']
        self.FatalError = ['BadPassword', 'BadEmail', 'VerifyEmail']
        self.TaskSync = False
        self.CodeLogEn(False)
        self.ThreadNumber = 5
        self.MaxRetry = 3
        self.ProxyEnable = True
        self.TaskName = 'SubmitReview'
        self.LoadImage = False
        self.TaskLogEn = False
        self.TaskRetryEn = False
        self.TaskInfos = parseinfo.OrderTaskTable
        for item in self.TaskInfos:
            item.update(parseinfo.AccountFrame.loc[item['username']].to_dict())
        self.ReviewList = []
        for name, item in parseinfo.ReviewerFrame.iterrows():
            self.ReviewList.append(item.to_dict())
        pass

    def PopReviewer(self, asin):
        SelectReviewer = {'reviewerid':'',
                          'orderasin':'',
                          'reviewstar':'',
                          'reviewertitle':'',
                          'reviewercontent':'',
                          'reviewstatus':'',
                          'reviewerusername':''}
        for item in self.ReviewList:
            if item['orderasin'] == asin and item['reviewstatus'] != 'used':
                item['reviewstatus'] = 'used'
                SelectReviewer = item
                self.ReviewList.remove(item)
                break
        return SelectReviewer

    def PushReviewer(self, SelectReviewer):
        SelectReviewer['reviewstatus'] = ''
        self.ReviewList.append(SelectReviewer)

    def DumpReviewer(self):
        self.ReportInfo = ['reviewerid', 'orderasin', 'reviewstar', 'reviewertitle', 'reviewercontent', 'reviewstatus']
        self.TaskName = 'DumpReviewer'
        for item in self.ReviewList:
            if item['reviewstatus'] != 'used':
                item['status'] = True
                item['errorcode'] = ''
                self.TaskLog(item)

    def DumpLeftTask(self):
        self.ReportInfo = ['username', 'asins']
        self.TaskName = 'DumpLeftTask'
        for item in self.TaskInfos:
            if item['asins']:
                item['status'] = True
                item['errorcode'] = ''
                self.TaskLog(item)

    # overiding method
    def FinalWork(self):
        self.DumpReviewer()
        self.DumpLeftTask()

    # overiding method
    def SubTask(self, driver, TaskInfo):
        TaskInfo['asin'] = ''
        TaskInfo['reviewerid'] = ''
        TaskInfo['reviewstar'] = ''
        TaskInfo['reviewertitle'] = ''
        TaskInfo['reviewercontent'] = ''
        TaskInfo['reviewerusername'] = TaskInfo['username']
        Task = AmazonFunction(driver, TaskInfo)
        if not Task.login():
            self.PushRetryQueue(TaskInfo)
            self.TaskLog(TaskInfo)
            return False
        if not Task.GoToReview():
            self.PushRetryQueue(TaskInfo)
            self.TaskLog(TaskInfo)
            return False
        TaskInfoCopy = TaskInfo['asins'].copy()
        for asin in TaskInfoCopy:
            TaskInfo.update({'asin': asin})
            SelectReviewer = self.PopReviewer(asin)
            TaskInfo.update(SelectReviewer)
            if SelectReviewer['reviewercontent']:
                if Task.WriteReview():
                    print('Reviewer added for: ' + TaskInfo['username'] + ' :: ' + asin)
                    TaskInfo['asins'].remove(asin)
                else:
                    self.PushReviewer(SelectReviewer)
                    print('Reviewer fail for: ' + TaskInfo['username'] + ' :: ' + asin)
            else:
                TaskInfo['status'] = False
                TaskInfo['errorcode'] = 'InsufficientReviewer'
                print('Reviewer is insufficient for: ' + TaskInfo['username'] + ' :: ' + asin)
                TaskInfo['asins'].remove(asin)
            self.TaskLog(TaskInfo)
        # not all ASIN done
        if TaskInfo['asins']:
            self.PushRetryQueue(TaskInfo)
        pass


class CreatNewAcount(TaskManager):
    def __init__(self):
        TaskManager.__init__(self)
        self.ReportInfo = ['username', 'password', 'cookies', 'Timestamp']
        self.ReportErrorInfo = ['errorcode', 'retrynumber']
        self.FatalError = ['']
        self.TaskSync = False
        self.CodeLogEn(False)
        self.ThreadNumber = 4
        self.MaxRetry = 3
        self.ProxyEnable = True
        self.speed = 20
        self.LoadImage = False
        self.TaskName = 'CreatAcount'
        self.AcountNumber = 12
        self.TaskInfos = []
        for i in range(self.AcountNumber):
            self.TaskInfos.append({'AounctID': str(i)})

    # overiding method
    def SubTask(self, driver, TaskInfo):
        TaskInfo['username'] = ''
        TaskInfo['password'] = ''
        TaskInfo['cookies'] = ''
        Task = AmazonFunction(driver, TaskInfo)
        EmailDomain = '@foxairmail.com'
        if not Task.CreatAcount(EmailDomain):
            return False
        Task.driver.get("https://www.amazon.com/")
        try: Task.driver.find_element_by_id('nav-logo').click()
        except: pass
        try:
            Task.ViewAllPage()
            Task.Walkaround()
        except:
            pass
        Task.FunctionInfo['cookies'] = json.dumps(driver.get_cookies())
        #Task.FunctionInfo['cookies'] = ''
        return True

class ViewTask(TaskManager):
    def __init__(self):
        TaskManager.__init__(self)
        self.ReportInfo = ['asin', 'keyword', 'retrynumber', 'Timestamp']
        self.ReportErrorInfo = ['errorcode', 'retrynumber']
        self.FatalError = ['']
        self.TaskSync = False
        self.CodeLogEn(False)
        self.ThreadNumber = 1
        self.MaxRetry = 2000
        self.ProxyEnable = False
        self.speed = 12
        self.TaskName = 'CreatAcount'
        self.TaskLogEn = False
        self.TaskRetryEn = False
        self.TaskInfos = parseinfo.ViewTaskTable

    # overiding method
    def SubTask(self, driver, TaskInfo):
        TaskInfo['lowprice'] = '0'
        TaskInfo['highprice'] = '0'
        self.TaskName = TaskInfo['asin']
        self.start_time = datetime.now()
        TaskInfo['keyword'] = random.sample(TaskInfo['keywords'], 1)[0]
        print('start info:::' + TaskInfo['asin'] + ' keyword: ' + TaskInfo['keyword'])
        Task = AmazonFunction(driver, TaskInfo)

        try: Task.driver.get('https://www.amazon.com/')
        except: pass
        try: Task.driver.maximize_window()
        except: print('Set full screen fail!')

        ProductionUrl = Task.SearchProduct()
        if not ProductionUrl:
            return False
        if not Task.ViewAllPage():
            return False
        if not Task.view_reviewer():
            return False
        if not Task.add_to_cart():
            return False
        Task.back_to_page(ProductionUrl)

        while Task.stay_time() < Task.min_view_time:
            Task.speed = randint(20, 60)
            if not Task.view_all():
                return False
            Task.back_to_page(ProductionUrl)

        self.TaskLog(TaskInfo)
        if int(TaskInfo['sections']) != '0':
            self.PushRetryQueue(TaskInfo)
            TaskInfo['sections'] = str(int(TaskInfo['sections']) - 1)


class FillCreditCard(TaskManager):
    def __init__(self):
        TaskManager.__init__(self)
        self.ReportInfo = ['username', 'password', 'cookies', 'nameoncard','ccnumber','ccmonth','ccyear','checkaccount']
        self.ReportErrorInfo = ['errorcode', 'retrynumber']
        self.FatalError = ['BadPassword', 'BadEmail', 'InsufficientCard']
        self.TaskSync = False
        self.CodeLogEn(False)
        self.ThreadNumber = 5
        self.MaxRetry = 3
        self.ProxyEnable = True
        self.TaskName = 'FillCreditCard'
        self.TaskInfos = parseinfo.AccountTable
        self.CreditCardList = []
        for name, item in parseinfo.FinanceFrame.iterrows():
            self.CreditCardList.append(item.to_dict())
        pass

    def PopCard(self):
        SelectCard = {}
        for item in self.CreditCardList:
            if item['cardstatus'] != 'used':
                item['cardstatus'] = 'used'
                SelectCard = item
                self.CreditCardList.remove(item)
                break
        return SelectCard

    def PushCard(self, SelectCard):
        SelectCard['cardstatus'] = ''
        self.CreditCardList.append(SelectCard)

    def DumpCard(self):
        self.ReportInfo = ['username','nameoncard','ccnumber','ccmonth','ccyear','cardstatus','checkaccount']
        self.TaskName = 'DumpCard'
        for item in self.CreditCardList:
            if item['cardstatus'] != 'used':
                item['status'] = True
                item['errorcode'] = ''
                self.TaskLog(item)

    def DumpLeftUser(self):
        self.ReportInfo = ['username']
        self.TaskName = 'DumpLeftUser'
        for item in self.TaskInfos:
            if not item['status']:
                self.TaskLog(item)

    # overiding method
    def FinalWork(self):
        self.DumpCard()
        self.DumpLeftUser()

    # overiding method
    def SubTask(self, driver, TaskInfo):
        SelectCard = self.PopCard()
        if SelectCard:
            TaskInfo.update(SelectCard)
            Task = AmazonFunction(driver, TaskInfo)
            if not Task.login():
                self.PushCard(SelectCard)
                print('Login fail...')
                return False
            if Task.AddCreditCard():
                print('Credit Card added for: ' + TaskInfo['username'])
            else:
                self.PushCard(SelectCard)
                print('Credit Card add fail for: ' + TaskInfo['username'])
        else:
            TaskInfo.update({'nameoncard': '',
                             'ccnumber': '',
                             'ccmonth': '',
                             'ccyear': '',
                             'cardstatus': '',
                             'checkaccount': ''})
            TaskInfo['status'] = False
            TaskInfo['errorcode'] = 'InsufficientCard'
            print('Credit Card is insufficient for: ' + TaskInfo['username'])
        time.sleep(5)
        Task.FunctionInfo['cookies'] = json.dumps(driver.get_cookies())

class FillAddress(TaskManager):
    def __init__(self):
        TaskManager.__init__(self)
        self.ReportInfo = ['username', 'password', 'cookies','fullname','address','postalcode','city','state','phonenumber']
        self.ReportErrorInfo = ['errorcode', 'retrynumber']
        self.FatalError = ['BadPassword', 'BadEmail', 'InsufficientAddress']
        self.TaskSync = False
        self.CodeLogEn(False)
        self.ThreadNumber = 5
        self.MaxRetry = 3
        self.ProxyEnable = True
        self.TaskName = 'FillShippingAddress'
        self.TaskInfos = parseinfo.AccountTable
        self.AddressList = []
        for name, item in parseinfo.AddressFrame.iterrows():
            self.AddressList.append(item.to_dict())
        pass

    def PopAddress(self):
        SelectAddress = {}
        for item in self.AddressList:
            if item['addressstatus'] != 'used':
                item['addressstatus'] = 'used'
                SelectAddress = item
                self.AddressList.remove(item)
                break
        return SelectAddress

    def PushAddress(self, SelectAddress):
        SelectAddress['addressstatus'] = ''
        self.AddressList.append(SelectAddress)

    def DumpAddress(self):
        self.ReportInfo = ['username','fullname','address','postalcode','city','state','phonenumber','addressstatus']
        self.TaskName = 'DumpCard'
        for item in self.AddressList:
            if item['addressstatus'] != 'used':
                item['status'] = True
                item['errorcode'] = ''
                self.TaskLog(item)

    def DumpLeftUser(self):
        self.ReportInfo = ['username']
        self.TaskName = 'DumpLeftUser'
        for item in self.TaskInfos:
            if not item['status']:
                self.TaskLog(item)

    # overiding method
    def FinalWork(self):
        self.DumpAddress()
        self.DumpLeftUser()

    # overiding method
    def SubTask(self, driver, TaskInfo):
        SelectAddress = self.PopAddress()
        if SelectAddress:
            TaskInfo.update(SelectAddress)
            Task = AmazonFunction(driver, TaskInfo)
            if not Task.login():
                self.PushAddress(SelectAddress)
                print('Login fail...')
                return False
            if Task.SetAddress():
                print('Shipping address added for: ' + TaskInfo['username'])
            else:
                self.PushAddress(SelectAddress)
                print('Shipping address add fail for: ' + TaskInfo['username'])
        else:
            TaskInfo.update({'fullname': '',
                             'address': '',
                             'postalcode': '',
                             'city': '',
                             'state': '',
                             'phonenumber': '',
                             'addressstatus': ''})
            TaskInfo['status'] = False
            TaskInfo['errorcode'] = 'InsufficientAddress'
            print('Address is insufficient for: ' + TaskInfo['username'])
        time.sleep(5)


if __name__ == "__main__":
    print('*********************************************')
    print('*          please select function           *')
    print('*   1. Validate account                     *')
    print('*   2. Modify account                       *')
    print('*   3. Prepare Order                        *')
    print('*   4. Place Order                          *')
    print('*   5. Test Search                          *')
    print('*   6. Submit reviewer                      *')
    print('*   7. Creat new Account                    *')
    print('*   8. View product                         *')
    print('*   9. Fill credit Card                     *')
    print('*   a. Fill Shipping Address                *')
    print('*********************************************')
    TaskSelect = input()
    if TaskSelect == '1':
        Task = VerifyAccount()
        Task.TaskManage()
    elif TaskSelect == '2':
        Task = ModifyAcount()
        Task.TaskManage()
    elif TaskSelect == '3':
        Task = PrepareOrder()
        Task.TaskManage()
    elif TaskSelect == '4':
        Task = PlaceOrder()
        Task.TaskManage()
    elif TaskSelect == '5':
        Task = TestSearch()
        Task.TaskManage()
    elif TaskSelect == '6':
        Task = Review()
        Task.TaskManage()
    elif TaskSelect == '7':
        Task = CreatNewAcount()
        Task.TaskManage()
    elif TaskSelect == '8':
        Task = ViewTask()
        Task.TaskManage()
    elif TaskSelect == '9':
        Task = FillCreditCard()
        Task.TaskManage()
    elif TaskSelect == 'a':
        Task = FillAddress()
        Task.TaskManage()
    else:
        print('No task selected.')