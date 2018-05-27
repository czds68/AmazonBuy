import pandas as pd
AccountFile     = './amazonbuy_database/AccountInfo.csv'
FinanceFile     = './amazonbuy_database/Finance.csv'
AddressFile     = './amazonbuy_database/shippingaddress.csv'
ProductFile     = './amazonbuy_database/productinfo.csv'
GiftCardFile    = './amazonbuy_database/Giftcard.csv'
OrderRecordFile = './amazonbuy_database/orderrecored.csv'
ReviewerFile = './amazonbuy_database/reviewer.csv'
OrderTaskFile   = './amazonbuy_database/ordertask.csv'
SmallGiftCardFile   = './amazonbuy_database/smallgiftcard.csv'
ViewTaskFile   = './amazonbuy_database/Viewtask.csv'

AccountFrame = pd.DataFrame(pd.read_csv(AccountFile,header=0, dtype=str,sep=','))
AccountFrame.drop_duplicates(subset='username', inplace=True)
AccountFrame.dropna(how='all', inplace=True)
#AccountFrame.dropna(axis=1, how='all', inplace=True)
#AccountFrame.dropna(how='any', inplace=True)
AccountTable = []
for name, item in AccountFrame.iterrows():
    item.fillna(value='',inplace=True)
    AccountInfo={'username': name}
    AccountInfo.update(item.to_dict())
    AccountTable.append(AccountInfo)
AccountFrame.set_index('username', inplace=True)

FinanceFrame = pd.DataFrame(pd.read_csv(FinanceFile,header=0, dtype=str))
FinanceFrame.drop_duplicates(inplace=True)
FinanceFrame.dropna(how='all', inplace=True)
#FinanceFrame.dropna(axis=1, how='all', inplace=True)
#FinanceFrame.dropna(how='any', inplace=True)
FinanceFrame.fillna(value='',inplace=True)
FinanceFrame.set_index('username', inplace=True)

AddressFrame = pd.DataFrame(pd.read_csv(AddressFile,header=0, dtype=str))
#AddressFrame.drop_duplicates(subset='username', inplace=True)
AddressFrame.dropna(how='all', inplace=True)
#AddressFrame.dropna(axis=1, how='all', inplace=True)
#AddressFrame.dropna(how='any', inplace=True)
AddressFrame.set_index('username', inplace=True)

ProductFrame = pd.DataFrame(pd.read_csv(ProductFile,header=0, dtype=str))
ProductFrame.drop_duplicates(subset='asin', inplace=True)
ProductFrame.dropna(how='all', inplace=True)
ProductFrame.dropna(axis=1, how='all', inplace=True)
#ProductFrame.dropna(how='any', inplace=True)
ProductFrame.fillna(value='',inplace=True)
ProductFrame.set_index('asin', inplace=True)
'''
GiftCardFrame = pd.DataFrame(pd.read_csv(GiftCardFile,header=0, dtype=str))
GiftCardFrame.drop_duplicates(subset='username', inplace=True)
GiftCardFrame.dropna(how='all', inplace=True)
GiftCardFrame.dropna(axis=1, how='all', inplace=True)
GiftCardFrame.fillna(value='',inplace=True)
for name, item in GiftCardFrame.iterrows():
    if not (item['username'] and item['giftcardnumber'] and item['giftcardvalue']):
        GiftCardFrame.drop(index=name,inplace=True)
GiftCardFrame.set_index('username', inplace=True)
'''

OrderRecordFrame = pd.DataFrame(pd.read_csv(OrderRecordFile,header=0, dtype=str))
OrderRecordFrame.dropna(how='all', inplace=True)
OrderRecordFrame.fillna(value='',inplace=True)
OrderRecordFrame.set_index('username', inplace=True)

ReviewerFrame = pd.DataFrame(pd.read_csv(ReviewerFile,header=0, dtype=str))
ReviewerFrame.dropna(how='all', inplace=True)
#ReviewerFrame.dropna(axis=1, how='all', inplace=True)
ReviewerFrame.fillna('',inplace=True)
for name, item in ReviewerFrame.iterrows():
    if not (item['orderasin'] and item['reviewstar'] and item['reviewertitle'] and item['reviewercontent'] and item['reviewerid']):
        ReviewerFrame.drop(index=name,inplace=True)

OrderTaskFrame = pd.DataFrame(pd.read_csv(OrderTaskFile,header=0, dtype=str))
OrderTaskFrame.drop_duplicates(subset='username', inplace=True)
OrderTaskFrame.dropna(how='all', inplace=True)
OrderTaskFrame.dropna(axis=1, how='all', inplace=True)
for name, item in OrderTaskFrame.iterrows():
    if not (item['username']):
        OrderTaskFrame.drop(index=name,inplace=True)
OrderTaskFrame.set_index('username', inplace=True)
OrderTaskFrame.dropna(how='all', inplace=True)
OrderTaskTable = []
for name, item in OrderTaskFrame.iterrows():
    item.dropna(inplace=True)
    OrderTaskInfo={'username': name}
    OrderTaskInfo.update({'asins': list(item)})
    OrderTaskTable.append(OrderTaskInfo)

SmallGiftCardFrame = pd.DataFrame(pd.read_csv(SmallGiftCardFile,header=0, dtype=str))
SmallGiftCardFrame.drop_duplicates(inplace=True)
SmallGiftCardFrame.dropna(how='all', inplace=True)
SmallGiftCardFrame.fillna('',inplace=True)
for name, item in SmallGiftCardFrame.iterrows():
    if not (item['smallgiftcardnumber'] and item['smallgiftcardvalue']):
        SmallGiftCardFrame.drop(index=name,inplace=True)
'''
ViewTaskFrame = pd.DataFrame(pd.read_csv(ViewTaskFile,header=0, dtype=str))
ViewTaskFrame.drop_duplicates(inplace=True)
ViewTaskFrame.drop(columns=['Timestamp','noname'], inplace=True)
ViewTaskFrame.dropna(how='all', inplace=True)
OrderTaskFrame.dropna(axis=1, how='all', inplace=True)
ViewTaskTable = []
for name, item in ViewTaskFrame.iterrows():
    item.dropna(inplace=True)
    OrderTaskInfo = {}
    OrderTaskInfo.update(item.to_dict())
    item.drop(['department','asin','sections','countary'], inplace=True)
    OrderTaskInfo.update({'keywords': list(item)})
    ViewTaskTable.append(OrderTaskInfo)
pass
'''