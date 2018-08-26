from AmazonDatabaseAccess import amazon_db
from AmazonDatabaseAccess import TEST_OP
op = TEST_OP.GET
db = amazon_db()
db.open()
rslt = db.accountinfo_get_item()

for item in rslt:
    db.accountinfo_del_item(item[1])
db.close()
del db