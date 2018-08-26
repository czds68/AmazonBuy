from AmazonDatabaseAccess import amazon_db
from AmazonDatabaseAccess import TEST_OP
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

AccountFile = './amazonbuy_database/AccountInfo.csv'

AccountFrame = pd.DataFrame(pd.read_csv(AccountFile,header=0, dtype=str,sep=','))
AccountFrame.drop_duplicates(subset='username', inplace=True)
AccountFrame.dropna(how='all', inplace=True)
#AccountFrame.dropna(axis=1, how='all', inplace=True)
#AccountFrame.dropna(how='any', inplace=True)
AccountFrame.fillna('',inplace=True)
#AccountFrame.set_index('username', inplace=True)
AcountTable = []
for name, item in AccountFrame.iterrows():
    AcountTable.append(item.to_dict())
pass

op = TEST_OP.GET
db = amazon_db()
db.open()
rslt = db.accountinfo_get_item()

for item in AcountTable:
    print('Add new acount  ' + item['username'] + ' : '+ item['password'])
    db.accountinfo_add_item(item['username'], item['password'])

db.close()
del db