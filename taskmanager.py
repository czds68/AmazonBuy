import os
import sys
import time
import queue
import threading
from threading import current_thread
import traceback
from datetime import datetime
import requests
import re
import csv
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import zipfile


LogFilePath = './logs/'
PrintPath = './code_log/'
MacName = 'enp0s31f6'
# set maximum recursion depth
sys.setrecursionlimit(10000)

class TaskManager():
    def __init__(self):
        # initial
        self.FileLock = threading.RLock()
        self.ReportInfo = ['retrynumber'] # Infos report when Thread done
        self.ReportErrorInfo = ['errorcode']  # infos report when Thread fail
        self.FatalError = []  # Stop retry if fatal error

        # initial Task Info
        self.TaskInfos = []
        self.TaskQueue = queue.Queue()

        # Webdriver setting
        self.LoadImage = False
        self.FakeAgent = True

        # Proxy Setting
        #self.ProxyUrl = 'http://webapi.http.zhimacangku.com/getip?num=5&type=1&pro=&city=0&yys=0&port=11&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        self.ProxyUrl = 'http://webapi.http.zhimacangku.com/getip?num=5&type=1&pro=&city=0&yys=0&port=11&time=2&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        #self.ProxyUrl = 'http://api.xdaili.cn/xdaili-api//privateProxy/applyStaticProxy?spiderId=c0e4dc4f348e4dc9b791f96880ca912e&returnType=1&count=5'
        self.ProxyPool = []
        self.ProxyTime = datetime.now()
        self.ProxyTimeout = 120
        self.ProxyEnable = True
        self.AuthProxy = False
        if not os.path.exists('./ProxyPluginFiles/'):
            os.mkdir('./ProxyPluginFiles/')

        # Thread setting
        self.MaxRetry = 0 # Max retry number if failed
        self.TaskSync = False
        self.ThreadNumber = 1
        self.ThreadGroup = []
        self.ThreadSelect = 0
        self.ThreadAliveNum = 0

        # initial the output path
        self.TaskName = 'task' # name log file
        self.TaskLogEn = True
        self.TaskRetryEn = True
        self.DatePath = str(time.strftime("%Y%m%d", time.localtime())) + '/'
        if not os.path.exists(LogFilePath):
            os.mkdir(LogFilePath)
        if not os.path.exists(LogFilePath + self.DatePath):
            os.mkdir(LogFilePath + self.DatePath)

        # Log the print info
        self.__console__ = sys.stdout

    def CodeLogEn(self, enable = True):
        if enable:
            if not os.path.exists(PrintPath):
                os.mkdir(PrintPath)
            log_file_handler = open(PrintPath + self.DatePath + '.log', 'a')
            sys.stdout = log_file_handler
        else:
            sys.stdout = self.__console__

    def FillInfo(self):
        for TaskInfo in self.TaskInfos:
            TaskInfo['retrynumber'] = 0
            TaskInfo['status'] = False
            TaskInfo['errorcode'] = 'Start'
            TaskInfo['Timestamp'] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.TaskQueue.put(TaskInfo)

    # A dummy subtask
    def SubTask(self, driver, TaskInfo):
        time.sleep(5)
        TaskInfo['status'] = True
        TaskInfo['errorcode'] = 'Finished'
        print('Thread executed!')

    # finally work when threads synchronously done
    def SubSyncFunc(self):
        # change Mac address
        os.system("sudo spoof-mac.py randomize " + MacName)
        os.system("sudo service networking restart")
        print('Mac address changed!')
        time.sleep(5)

    # start a driver
    def WebDriver(self, proxy):
        # use chrome
        # 去除 提醒标示栏
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')
        options.add_argument('--log-level=3')
        # useragent
        if self.FakeAgent:
            useragent = '--user-agent=' + str(UserAgent().random)
            options.add_argument(useragent)
        # add plug-in
        #options.add_extension("./EditThisCookie_v1.4.3.crx")
        # set proxy
        if proxy:
            if self.AuthProxy:
                options.add_extension(self.MakeAuthProxy(proxy))
            else:
                options.add_argument('--proxy-server=http://' + proxy)
        # 不加载图片
        if not self.LoadImage:
            options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        # 加载策略
        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "none"
        try:
            driver = webdriver.Chrome('./chromedriver', chrome_options=options, desired_capabilities=caps)
            driver.set_page_load_timeout(10)
            driver.set_script_timeout(10)
            driver.implicitly_wait(10)
            driver.maximize_window()
        except:
            print('Set full screen fail!')
            print(traceback.print_exc())
        return driver

    # generate and manage the threads
    def SubmitTask(self, TaskInfo, proxy):
        if self.AuthProxy:
            proxy = TaskInfo['proxy']
        try:
            driver = self.WebDriver(proxy)
            self.SubTask(driver, TaskInfo)
            if self.TaskRetryEn:
                self.PushRetryQueue(TaskInfo)
            if self.TaskLogEn:
                self.TaskLog(TaskInfo)
        except:
            TaskInfo['errorcode'] = 'TaskSubmitFail'
            TaskInfo['status'] = False
            print('Submitting thread fail!!!')
            print(traceback.print_exc())
            self.PushRetryQueue(TaskInfo)
            self.TaskLog(TaskInfo)
        finally:
            try:
                driver.delete_all_cookies()
                driver.quit()
            except:
                pass
            self.SubTaskFinal(TaskInfo)

    def SubTaskFinal(self,TaskInfo):
        pass

    def PushRetryQueue(self, TaskInfo):
        self.FileLock.acquire()
        if (TaskInfo['errorcode'] not in self.FatalError) and (not TaskInfo['status']):
            TaskInfo['retrynumber'] += 1
            self.TaskQueue.put(TaskInfo)
        self.FileLock.release()

    # write log
    def TaskLog(self, TaskInfo):
        self.FileLock.acquire()
        TaskInfo['Timestamp'] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        LogInfo = []
        for item in self.ReportInfo:
            LogInfo.append(TaskInfo[item])
        if TaskInfo['status']:
            FilePath = LogFilePath + self.DatePath + self.TaskName + '.csv'
        else:
            for item in self.ReportErrorInfo:
                LogInfo.append(TaskInfo[item])
            FilePath = LogFilePath + self.DatePath + self.TaskName + '_fail.csv'
            if TaskInfo['errorcode'] in self.FatalError:
                LogInfo.append('FatalError')
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

    def GetProxy(self):
        if self.ProxyEnable and not self.AuthProxy:
            if self.ProxyPool == [] or (int((datetime.now() - self.ProxyTime).seconds) > self.ProxyTimeout):
                try:
                    ProxyText = requests.get(self.ProxyUrl).text
                    ErrorInfo = re.compile('[a-zA-Z]')
                    while ErrorInfo.findall(ProxyText):
                        print('Retry for proxy...  Last get time::' + str(self.ProxyTime.time()))
                        print('Time now::: ' + str(datetime.now().time()))
                        time.sleep(10)
                        ProxyText = requests.get(self.ProxyUrl).text
                    ProxyGot = re.split('\r\n', ProxyText)[0:-1]
                    self.ProxyPool = ProxyGot
                    self.ProxyTime = datetime.now()
                except:
                    self.ProxyPool == []
                    print('Proxy fetch error...')
                    print(traceback.print_exc())
            return self.ProxyPool.pop() if self.ProxyPool else ''
        else:
            return ''

    def MakeAuthProxy(self,proxy):
        ProxySplit = proxy.split(':')
        ip = ProxySplit[0]
        port = ProxySplit[1]
        username = ProxySplit[2]
        password = ProxySplit[3]
        manifest_json = """
                {
                    "version": "1.0.0",
                    "manifest_version": 2,
                    "name": "Chrome Proxy",
                    "permissions": [
                        "proxy",
                        "tabs",
                        "unlimitedStorage",
                        "storage",
                        "<all_urls>",
                        "webRequest",
                        "webRequestBlocking"
                    ],
                    "background": {
                        "scripts": ["background.js"]
                    },
                    "minimum_chrome_version":"22.0.0"
                }
                """

        background_js = '''
                var config = {
                        mode: "fixed_servers",
                        rules: {
                          singleProxy: {
                            scheme: "http",
                            host: "''' + ip + '''",
                            port: parseInt(''' + port + ''')
                          },
                          bypassList: ["foobar.com"]
                        }
                      };

                chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

                function callbackFn(details) {
                    return {
                        authCredentials: {
                            username: "''' + username + '''",
                            password: "''' + password + '''"
                        }
                    };
                }

                chrome.webRequest.onAuthRequired.addListener(
                            callbackFn,
                            {urls: ["<all_urls>"]},
                            ['blocking']
                );
                '''
        TreadTask = current_thread()
        pluginfile = './ProxyPluginFiles/' + 'proxy_auth_plugin_' + TreadTask.getName() + '.zip'
        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        return pluginfile

    def CountThread(self):
        self.ThreadAliveNum = 0
        self.ThreadSelect = len(self.ThreadGroup)
        for i in range(len(self.ThreadGroup)):
            if self.ThreadGroup[i].is_alive():
                self.ThreadAliveNum += 1
            else:
                self.ThreadSelect = i

    def TaskManage(self):
        # fill Queue
        self.FillInfo()

        # Manage thread
        while (not self.TaskQueue.empty()) or self.ThreadAliveNum:
            self.CountThread()
            if self.TaskSync == False:
                # wait thread pool available
                while self.ThreadAliveNum >= self.ThreadNumber:
                    time.sleep(5)
                    self.CountThread()
            else:
                # wait all thread done to reset Mac
                if self.ThreadAliveNum >= self.ThreadNumber:
                    while self.ThreadAliveNum:
                        time.sleep(5)
                        self.CountThread()
                    self.SubSyncFunc()

            # get task info from queue
            if self.TaskQueue.empty():
                self.CountThread()
                continue
            self.FileLock.acquire()
            TaskInfo = self.TaskQueue.get()
            self.FileLock.release()

            # skip if retry more than expected
            if TaskInfo['retrynumber'] > self.MaxRetry:
                continue

            # get proxy
            proxy = self.GetProxy()

            # Start a thread
            try:
                print('Start Task::::: thread_' + str(self.ThreadSelect) + ' :::: ' + proxy)
                task_thread = threading.Thread(target=self.SubmitTask, args=(TaskInfo, proxy),name=self.TaskName+str(self.ThreadSelect))
                task_thread.setDaemon(daemonic=True)
                task_thread.start()
                if len(self.ThreadGroup) >= self.ThreadNumber:
                    self.ThreadGroup[self.ThreadSelect] = task_thread
                else:
                    self.ThreadGroup.append(task_thread)
            except:
                print(traceback.print_exc())

            self.CountThread()
        # final task when all thread done
        self.FinalWork()

    def FinalWork(self):
        pass
