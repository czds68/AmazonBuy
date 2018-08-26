from datetime import date, datetime, timedelta
import mysql.connector
from mysql.connector import errorcode
import logging
from enum import IntEnum


remote_config = {
    "user": "root",
    "password": "Max123",
    "host": "czds68.yicp.io",
    "port": "4406",
    "database": "amazon",
}

local_config = {
    "user": "root",
    "password": "Max123",
    "host": "czds68.yicp.io",
    "port": "4406",
    "database": "amazon",
}

mac_config = {
    "user": "root",
    "password": "lee",
    "host": "192.168.0.3",
    "port": "3306",
    "database": "amazon",
}
config = remote_config


class DB(IntEnum):
    ACCOUNTINFO = 0
    SHIPADDRESS = 1
    FINANCE = 2
    ACCOUNTQUOTA = 3
    PRODUCTINFO = 4
    ORDERTASK = 5


class amazon_db(object):
    db_names = [
        "accountinfo",
        "shipaddress",
        "finance",
        "accountquota",
        "productinfo",
        "ordertask",
    ]

    accountinfo_fields = [
        "userid",
        "username",
        "password",
        "cookies",
        "createdate",
        "logindate",
        "lastbuy",
        "in_use",
        "alive",
        "MAC",
    ]
    shipaddress_fields = [
        "addrid",
        "username",
        "fullname",
        "address",
        "postalcode",
        "city",
        "state",
        "phonenumber",
    ]
    finance_fields = [
        "cardid",
        "username",
        "nameoncard",
        "ccnumber",
        "ccmonth",
        "ccyear",
        "checkaccount",
        "fullname",
        "address",
        "postalcode",
        "city",
        "state",
        "phonenumber",
    ]
    accountquota_fields = ["accountid", "checkaccount", "wquota", "mquota", "yquota"]
    productinfo_fields = [
        "productid",
        "asin",
        "department",
        "busybox_price",
        "order_price",
        "keyword",
        "brand",
    ]
    order_task_fields = ["ordertaskid", "username", "asin", "num", "order_date"]

    # args in tuple form
    sql_add_accountinfo_tuple = (
        "INSERT INTO accountinfo"
        "(username, password, cookies, createdate, logindate, lastbuy, in_use, alive, MAC)"
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
    )
    sql_update_accountinfo_tuple = "UPDATE accountinfo SET password=%s, cookies=%s, createdate=%s, logindate=%s, lastbuy=%s, in_use=%s, alive=%s, MAC=%s WHERE username=%s;"

    # args in dict form
    sql_add_accountinfo_dict = (
        "INSERT INTO accountinfo"
        "(username, password, cookies, createdate, logindate, lastbuy, alive, MAC)"
        "VALUES (%(username)s, %(password)s, %(cookies)s, %(createdate)s, %(logindate)s, %(lastbuy)s, %(alive)s, %(MAC)s);"
    )
    sql_update_accountinfo_dict = "UPDATE accountinfo SET password=%(password)s, cookies=%(cookies)s, createdate=%(createdate)s, logindate=%(logindate)s, lastbuy=%(lastbuy)s, in_use=%(in_use)s, alive=%(alive)s, MAC=%(MAC)s WHERE username=%(username)s;"

    sql_get_accountinfo_all = "SELECT * FROM accountinfo;"
    sql_get_accountinfo_by_lastbuy_tuple = (
        "SELECT * FROM accountinfo WHERE lastbuy < %s AND in_use=0;"
    )
    sql_get_accountinfo_by_lastbuy_dict = (
        "SELECT * FROM accountinfo WHERE lastbuy < %(lastbuy)s AND in_use=0;"
    )
    sql_del_accountinfo_tuple = "DELETE FROM accountinfo WHERE username=%s;"
    sql_del_accountinfo_dict = "DELETE FROM accountinfo WHERE username=%(username)s;"
    # args in tuple form
    sql_add_shipaddress_tuple = (
        "INSERT INTO shipaddress "
        "(username, fullname, address, postalcode, city, state, phonenumber)"
        "VALUES (%s,%s,%s,%s,%s,%s,%s)"
    )
    sql_update_shipaddress_tuple = "UPDATE shipaddress SET fullname=%s, address=%s, postalcode=%s, city=%s, state=%s, phonenumber=%s WHERE username=%s;"
    # args in dict form
    sql_add_shipaddress_dict = (
        "INSERT INTO shipaddress "
        "(username, fullname, address, postalcode, city, state, phonenumber)"
        "VALUES (%(username)s,%(fullname)s,%(address)s,%(postalcode)s,%(city)s,%(state)s,%(phonenumber)s)"
    )
    sql_update_shipaddress_dict = "UPDATE shipaddress SET fullname=%(fullname)s, address=%(address)s, postalcode=%(postalcode)s, city=%(city)s, state=%(state)s, phonenumber=%(phonenumber)s WHERE username=%(username)s;"
    sql_get_shipaddress_all = "SELECT * FROM shipaddress;"
    sql_get_shipaddress_by_username_tuple = (
        "SELECT * FROM shipaddress WHERE username=%s;"
    )
    sql_get_shipaddress_by_username_dict = (
        "SELECT * FROM shipaddress WHERE username=%(username)s;"
    )
    sql_del_shipaddress_tuple = "DELETE FROM shipaddress WHERE username=%s;"
    sql_del_shipaddress_dict = "DELETE FROM shipaddress WHERE username=%(username)s;"

    # args in tuple form
    sql_add_finance_tuple = (
        "INSERT INTO finance "
        "(username,nameoncard,ccnumber,ccmonth,ccyear,checkaccount,fullname,address, postalcode,city,state,phonenumber) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    )
    sql_update_finance_tuple = "UPDATE finance SET nameoncard=%s,ccnumber=%s,ccmonth=%s,ccyear=%s,checkaccount=%s,fullname=%s,address=%s, postalcode=%s,city=%s,state=%s,phonenumber=%s WHERE username=%s;"

    # args in dict form
    sql_add_finance_dict = (
        "INSERT INTO finance "
        "(username,nameoncard,ccnumber,ccmonth,ccyear,checkaccount,fullname,address, postalcode,city,state,phonenumber) "
        "VALUES (%(username)s,%(nameoncard)s,%(ccnumber)s,%(ccmonth)s,%(ccyear)s,%(checkaccount)s,%(fullname)s,%(address)s,%(postalcode)s,%(city)s,%(state)s,%(phonenumber)s)"
    )
    sql_update_finance_dict = "UPDATE finance SET nameoncard=%(nameoncard)s,ccnumber=%(ccnumber)s,ccmonth=%(ccmonth)s,ccyear=%(ccyear)s,checkaccount=%(checkaccount)s,fullname=%(fullname)s,address=%(address)s, postalcode=%(postalcode)s,city=%(city)s,state=%(state)s,phonenumber=%(phonenumber)s WHERE username=%(username)s;"

    sql_get_finance_all = "SELECT * FROM finance;"
    sql_get_finance_by_username_tuple = "SELECT * FROM finance WHERE username=%s;"
    sql_get_finance_by_username_dict = (
        "SELECT * FROM finance WHERE username=%(username)s;"
    )
    sql_del_finance_tuple = "DELETE FROM finance WHERE username=%s;"
    sql_del_finance_dict = "DELETE FROM finance WHERE username=%(username)s;"

    # args in tuple form
    sql_add_accountquota_tuple = (
        "INSERT INTO accountquota"
        "(checkaccount,wquota,mquota,yquota)"
        "VALUES (%s,%s,%s,%s)"
    )
    sql_update_accountquota_tuple = (
        "UPDATE accountquota SET wquota=%s,mquota=%s,yquota=%s WHERE checkaccount=%s;"
    )

    # args in dict form
    sql_add_accountquota_dict = (
        "INSERT INTO accountquota"
        "(checkaccount,wquota,mquota,yquota)"
        "VALUES (%(checkaccount)s,%(wquota)s,%(mquota)s,%(yquota)s)"
    )
    sql_update_accountquota_dict = "UPDATE accountquota SET wquota=%(wquota)s,mquota=%(mquota)s,yquota=%(yquota)s WHERE checkaccount=%(checkaccount)s;"
    sql_get_accountquota_all = "SELECT * FROM accountquota;"
    sql_get_accountquota_by_account_tuple = (
        "SELECT * FROM accountquota WHERE checkaccount=%s;"
    )
    sql_get_accountquota_by_account_dict = (
        "SELECT * FROM accountquota WHERE checkaccount=%(checkaccount)s;"
    )
    sql_del_accountquota_tuple = "DELETE FROM accountquota WHERE checkaccount=%s;"
    sql_del_accountquota_dict = (
        "DELETE FROM accountquota WHERE checkaccount=%(checkaccount)s;"
    )

    # args in tuple form
    sql_add_productinfo_tuple = (
        "INSERT INTO productinfo"
        "(asin, department, busybox_price, order_price, keyword, brand)"
        "VALUES (%s,%s,%s,%s,%s,%s)"
    )
    sql_update_productinfo_tuple = "UPDATE productinfo SET department=%s, busybox_price=%s, order_price=%s, keyword=%s, brand=%s WHERE asin=%s;"
    # args in dict form
    sql_add_productinfo_dict = (
        "INSERT INTO productinfo"
        "(asin, department, busybox_price, order_price, keyword, brand)"
        "VALUES (%(asin)s,%(department)s,%(busybox_price)s,%(order_price)s,%(keyword)s,%(brand)s)"
    )
    sql_update_productinfo_dict = "UPDATE productinfo SET department=%(department)s, busybox_price=%(busybox_price)s, order_price=%(order_price)s, keyword=%(keyword)s, brand=%(brand)s WHERE asin=%(asin)s;"
    sql_get_productinfo_all = "SELECT * FROM productinfo;"
    sql_get_productinfo_by_asin_tuple = "SELECT * FROM productinfo WHERE asin=%s;"
    sql_get_productinfo_by_asin_dict = "SELECT * FROM productinfo WHERE asin=%(asin)s;"
    sql_del_productinfo_tuple = "DELETE FROM productinfo WHERE asin=%s;"
    sql_del_productinfo_dict = "DELETE FROM productinfo WHERE asin=%(asin)s;"

    # args in tuple form
    sql_add_ordertask_tuple = (
        "INSERT INTO ordertask"
        "(username, asin, num, order_date)"
        "VALUES (%s,%s,%s,%s)"
    )
    sql_update_ordertask_tuple = (
        "UPDATE ordertask SET asin=%s, num=%s, order_date=%s WHERE username=%s;"
    )

    # args in dict form
    sql_add_ordertask_dict = (
        "INSERT INTO ordertask"
        "(username, asin, num, order_date)"
        "VALUES (%(username)s,%(asin)s,%(num)s, %(order_date)s)"
    )
    sql_update_ordertask_dict = "UPDATE ordertask SET asin=%(asin)s, num=%(num)s, order_date=%(order_date)s WHERE username=%(username)s;"
    sql_get_ordertask_all = "SELECT * FROM ordertask;"
    # sql_del_ordertask_tuple = ("DELETE FROM ordertask WHERE username=%s;")
    # sql_del_ordertask_dict = ("DELETE FROM ordertask WHERE username=%(username)s;")

    def __init__(self):
        # for rd lock table
        self.sql_rd_lock = []
        self.sql_rd_lock_all = "LOCK TABLES "
        for item in list(enumerate(amazon_db.db_names)):
            # print(item)
            lock_statement = "LOCK TABLE %s READ;" % item[1]
            if item[0] == 0:
                self.sql_rd_lock_all += "%s READ" % item[1]
            else:
                self.sql_rd_lock_all += ",%s READ" % item[1]
            self.sql_rd_lock.append(lock_statement)
        self.sql_rd_lock_all += ";"

        # for wr lock table
        self.sql_wr_lock = []
        self.sql_wr_lock_all = "LOCK TABLES "
        for item in list(enumerate(amazon_db.db_names)):
            # print(item)
            lock_statement = "LOCK TABLE %s WRITE;" % item[1]
            if item[0] == 0:
                self.sql_wr_lock_all += "%s WRITE" % item[1]
            else:
                self.sql_wr_lock_all += ",%s WRITE" % item[1]
            self.sql_wr_lock.append(lock_statement)
        self.sql_wr_lock_all += ";"

        # for unlock all table
        self.sql_unlock_all = "UNLOCK TABLES;"

        self.sql_fields = {}
        self.sql_fields[
            amazon_db.db_names[DB.ACCOUNTINFO]
        ] = amazon_db.accountinfo_fields
        self.sql_fields[
            amazon_db.db_names[DB.SHIPADDRESS]
        ] = amazon_db.shipaddress_fields
        self.sql_fields[amazon_db.db_names[DB.FINANCE]] = amazon_db.finance_fields
        self.sql_fields[
            amazon_db.db_names[DB.ACCOUNTQUOTA]
        ] = amazon_db.accountquota_fields
        self.sql_fields[
            amazon_db.db_names[DB.PRODUCTINFO]
        ] = amazon_db.productinfo_fields
        self.sql_fields[amazon_db.db_names[DB.ORDERTASK]] = amazon_db.order_task_fields
        # for key, val in self.sql_fields.items():
        #    print(key, val)
        # print(self.sql_fields[amazon_db.db_names[DB.ACCOUNTINFO]])
        return

    def open(self):
        try:
            self.cnx = mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            print("connect err:", err)
        return

    def accountinfo_add_item(
        self,
        username,
        password,
        cookies=None,
        createdate=datetime.now(),
        logindate=datetime.now(),
        lastbuy=datetime(1997, 1, 1),
        in_use=0,
        alive=1,
        MAC="00-00-00-00-00-00",
    ):
        add_dll = {}
        add_dll["username"] = username
        add_dll["password"] = password
        add_dll["cookies"] = cookies
        add_dll["createdate"] = createdate
        add_dll["logindate"] = logindate
        add_dll["lastbuy"] = lastbuy
        add_dll["in_use"] = in_use
        add_dll["alive"] = alive
        add_dll["MAC"] = MAC
        print(add_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.ACCOUNTINFO])
        self.cursor.execute(amazon_db.sql_add_accountinfo_dict, add_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()
        return

    def accountinfo_get_item(self):
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_rd_lock[DB.ACCOUNTINFO])
        self.cursor.execute(amazon_db.sql_get_accountinfo_all)
        result = self.cursor.fetchall()
        # print(result)
        self.cursor.execute(self.sql_unlock_all)
        self.cursor.close()
        return result

    def accountinfo_get_item_by_lastbuy(self, interval):
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_rd_lock[DB.ACCOUNTINFO])
        tdiff = timedelta(hours=interval)
        self.cursor.execute(
            amazon_db.sql_get_accountinfo_by_lastbuy_tuple, (datetime.now() + tdiff,)
        )
        result = self.cursor.fetchall()
        # print(result)
        candidate_users = []
        for row in result:
            # print(row)
            item = dict(zip(amazon_db.accountinfo_fields, row))
            # print(item)
            candidate_users.append(item)
        # print(candidate_users)
        self.cursor.execute(self.sql_unlock_all)
        self.cursor.close()
        return candidate_users

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
        update_dll = {}
        update_dll["username"] = username
        update_dll["password"] = password
        update_dll["createdate"] = createdate
        update_dll["logindate"] = logindate
        update_dll["lastbuy"] = lastbuy
        update_dll["in_use"] = in_use
        update_dll["alive"] = alive
        update_dll["cookies"] = cookies
        update_dll["MAC"] = MAC
        # print(update_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.ACCOUNTINFO])
        self.cursor.execute(amazon_db.sql_update_accountinfo_dict, update_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()

    def accountinfo_del_item(self, username):
        update_dll = {}
        update_dll["username"] = username
        # print(update_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.ACCOUNTINFO])
        self.cursor.execute(amazon_db.sql_del_accountinfo_dict, update_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()

    def shipaddress_add_item(
        self,
        username,
        fullname,
        address=None,
        postalcode=None,
        city=None,
        state=None,
        phonenumber=None,
    ):
        add_dll = {}
        add_dll["username"] = username
        add_dll["fullname"] = fullname
        add_dll["address"] = address
        add_dll["postalcode"] = postalcode
        add_dll["city"] = city
        add_dll["state"] = state
        add_dll["phonenumber"] = phonenumber
        print(add_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.SHIPADDRESS])
        self.cursor.execute(amazon_db.sql_add_shipaddress_dict, add_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()
        return

    def shipaddress_get_item(self):
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_rd_lock[DB.SHIPADDRESS])
        self.cursor.execute(amazon_db.sql_get_shipaddress_all)
        result = self.cursor.fetchall()
        # print(result)
        self.cursor.execute(self.sql_unlock_all)
        self.cursor.close()
        return result

    def shipaddress_get_item_by_username(self, username):
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_rd_lock[DB.SHIPADDRESS])
        query = {}
        query["username"] = username

        self.cursor.execute(amazon_db.sql_get_shipaddress_by_username_dict, query)
        result = self.cursor.fetchone()
        # print(result)
        # for row in result:
        if result:
            result = dict(zip(amazon_db.shipaddress_fields, result))

        self.cursor.execute(self.sql_unlock_all)
        self.cursor.close()
        return result

    def shipaddress_update_item(
        self, username, fullname, address, postalcode, city, state, phonenumber
    ):
        update_dll = {}
        update_dll["username"] = username
        update_dll["fullname"] = fullname
        update_dll["address"] = address
        update_dll["postalcode"] = postalcode
        update_dll["city"] = city
        update_dll["state"] = state
        update_dll["phonenumber"] = phonenumber
        # print(update_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.SHIPADDRESS])
        self.cursor.execute(amazon_db.sql_update_shipaddress_dict, update_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()

    def shipaddress_del_item(self, username):
        update_dll = {}
        update_dll["username"] = username
        # print(update_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.SHIPADDRESS])
        self.cursor.execute(amazon_db.sql_del_shipaddress_dict, update_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()

    def finance_add_item(
        self,
        username,
        nameoncard,
        ccnumber,
        ccmonth,
        ccyear,
        checkaccount,
        fullname,
        address,
        postalcode,
        city,
        state,
        phonenumber,
    ):
        add_dll = {}
        add_dll["username"] = username
        add_dll["nameoncard"] = nameoncard
        add_dll["ccnumber"] = ccnumber
        add_dll["ccmonth"] = ccmonth
        add_dll["ccyear"] = ccyear
        add_dll["checkaccount"] = checkaccount
        add_dll["fullname"] = fullname
        add_dll["address"] = address
        add_dll["postalcode"] = postalcode
        add_dll["city"] = city
        add_dll["state"] = state
        add_dll["phonenumber"] = phonenumber
        print(add_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.FINANCE])
        self.cursor.execute(amazon_db.sql_add_finance_dict, add_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()
        return

    def finance_get_item(self):
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_rd_lock[DB.FINANCE])
        self.cursor.execute(amazon_db.sql_get_finance_all)
        result = self.cursor.fetchall()
        # print(result)
        self.cursor.execute(self.sql_unlock_all)
        self.cursor.close()
        return result

    def finance_get_item_by_username(self, username):
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_rd_lock[DB.FINANCE])
        self.cursor.execute(amazon_db.sql_get_finance_by_username_tuple, (username,))
        # result = self.cursor.fetchall()
        # #print(result)
        # candidate_finance = []
        # for row in result:
        #     item = dict(zip(amazon_db.finance_fields, row))
        #     candidate_finance.append(item)
        result = self.cursor.fetchone()
        if result:
            result = dict(zip(amazon_db.finance_fields, result))
        self.cursor.execute(self.sql_unlock_all)
        self.cursor.close()
        return result

    def finance_update_item(
        self,
        username,
        nameoncard,
        ccnumber,
        ccmonth,
        ccyear,
        checkaccount,
        fullname,
        address,
        postalcode,
        city,
        state,
        phonenumber,
    ):
        update_dll = {}
        update_dll["username"] = username
        update_dll["nameoncard"] = nameoncard
        update_dll["ccnumber"] = ccnumber
        update_dll["ccmonth"] = ccmonth
        update_dll["ccyear"] = ccyear
        update_dll["checkaccount"] = checkaccount
        update_dll["fullname"] = fullname
        update_dll["address"] = address
        update_dll["postalcode"] = postalcode
        update_dll["city"] = city
        update_dll["state"] = state
        update_dll["phonenumber"] = phonenumber
        # print(update_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.FINANCE])
        self.cursor.execute(amazon_db.sql_update_finance_dict, update_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()

    def finance_del_item(self, username):
        update_dll = {}
        update_dll["username"] = username
        # print(update_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.FINANCE])
        self.cursor.execute(amazon_db.sql_del_finance_dict, update_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()

    def accountquota_add_item(self, checkaccount, wquota, mquota, yquota):
        add_dll = {}
        add_dll["checkaccount"] = checkaccount
        add_dll["wquota"] = wquota
        add_dll["mquota"] = mquota
        add_dll["yquota"] = yquota
        # print(add_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.ACCOUNTQUOTA])
        self.cursor.execute(amazon_db.sql_add_accountquota_dict, add_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()
        return

    # get all accounts' quota
    def accountquota_get_item(self):
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_rd_lock[DB.ACCOUNTQUOTA])
        self.cursor.execute(amazon_db.sql_get_accountquota_all)
        result = self.cursor.fetchall()
        # print(result)
        self.cursor.execute(self.sql_unlock_all)
        self.cursor.close()
        return result

    # input specific user
    # output all related info
    def accountquota_get_one_item(self, checkaccount):
        query = {}
        query["checkaccount"] = checkaccount
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_rd_lock[DB.ACCOUNTQUOTA])
        self.cursor.execute(amazon_db.sql_get_accountquota_by_account_dict, query)
        # result = self.cursor.fetchall()
        # quota_rslt = []
        # for row in result:
        #     item = dict(zip(amazon_db.accountquota_fields, row))
        #     quota_rslt.append(item)
        result = self.cursor.fetchone()
        if result:
            result = dict(zip(amazon_db.accountquota_fields, result))
        # print(result)
        self.cursor.execute(self.sql_unlock_all)
        self.cursor.close()
        return result

    def accountquota_update_item(self, checkaccount, wquota, mquota, yquota):
        update_dll = {}
        update_dll["checkaccount"] = checkaccount
        update_dll["wquota"] = wquota
        update_dll["mquota"] = mquota
        update_dll["yquota"] = yquota
        # print(update_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.ACCOUNTQUOTA])
        self.cursor.execute(amazon_db.sql_update_accountquota_dict, update_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()

    def accountquota_del_item(self, checkaccount):
        update_dll = {}
        update_dll["checkaccount"] = checkaccount
        # print(update_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.ACCOUNTQUOTA])
        self.cursor.execute(amazon_db.sql_del_accountquota_dict, update_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()

    def productinfo_add_item(
        self, asin, department, busybox_price, order_price, keyword, brand
    ):
        add_dll = {}
        add_dll["asin"] = asin
        add_dll["department"] = department
        add_dll["busybox_price"] = busybox_price
        add_dll["order_price"] = order_price
        add_dll["keyword"] = keyword
        add_dll["brand"] = brand
        # print(add_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.PRODUCTINFO])
        self.cursor.execute(amazon_db.sql_add_productinfo_dict, add_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()
        return

    def productinfo_get_item(self):
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_rd_lock[DB.PRODUCTINFO])
        self.cursor.execute(amazon_db.sql_get_productinfo_all)
        result = self.cursor.fetchall()
        # print(result)
        self.cursor.execute(self.sql_unlock_all)
        self.cursor.close()
        return result

    def productinfo_get_one_item(self, asin):
        query = {}
        query["asin"] = asin
        # print('query', query)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_rd_lock[DB.PRODUCTINFO])
        self.cursor.execute(amazon_db.sql_get_productinfo_by_asin_dict, query)

        result = self.cursor.fetchone()
        if result:
            result = dict(zip(amazon_db.productinfo_fields, result))
        # print(product_rslt)
        self.cursor.execute(self.sql_unlock_all)
        self.cursor.close()
        return result

    def productinfo_update_item(
        self, asin, department, busybox_price, order_price, keyword, brand
    ):
        update_dll = {}
        update_dll["asin"] = asin
        update_dll["department"] = department
        update_dll["busybox_price"] = busybox_price
        update_dll["order_price"] = order_price
        update_dll["keyword"] = keyword
        update_dll["brand"] = brand
        print(update_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.PRODUCTINFO])
        self.cursor.execute(amazon_db.sql_update_productinfo_dict, update_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()

    def productinfo_del_item(self, asin):
        update_dll = {}
        update_dll["asin"] = asin
        # print(update_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.PRODUCTINFO])
        self.cursor.execute(amazon_db.sql_del_productinfo_dict, update_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()

    def ordertask_add_item(self, username, asin, num, order_date=datetime.now()):
        add_dll = {}
        add_dll["username"] = username
        add_dll["asin"] = asin
        add_dll["num"] = num
        add_dll["order_date"] = order_date
        # print(add_dll)
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_wr_lock[DB.ORDERTASK])
        self.cursor.execute(amazon_db.sql_add_ordertask_dict, add_dll)
        self.cursor.execute(self.sql_unlock_all)
        self.cnx.commit()
        self.cursor.close()
        return

    def ordertask_get_item(self):
        self.cursor = self.cnx.cursor()
        self.cursor.execute(self.sql_rd_lock[DB.ORDERTASK])
        self.cursor.execute(amazon_db.sql_get_ordertask_all)
        result = self.cursor.fetchall()
        # print(result)
        self.cursor.execute(self.sql_unlock_all)
        self.cursor.close()
        return result

    def close(self):
        self.cnx.close()


class TEST_OP(IntEnum):
    ADD = 0
    UPDATE = 1
    DEL = 2
    GET = 3


def dbg_accountinfo():
    op = TEST_OP.GET
    db = amazon_db()
    db.open()
    rslt = db.accountinfo_get_item()
    for row in rslt:
        print(row)

    if op == TEST_OP.ADD:
        # db.accountinfo_add_item('MarvinDickerson987@foxairmail.com', 'MarvinDickerson987')
        # db.accountinfo_add_item('AdamBright@foxairmail.com', '6564kkngbb')
        # db.accountinfo_add_item('DamaoWang@foxairmail.com', 'jyenbk85')
        # db.accountinfo_add_item('shawnelee88@gmail.com', 'leo88')
        db.accountinfo_add_item("shawnelee881@gmail.com", "leo88")
        db.accountinfo_add_item("shawnelee882@gmail.com", "leo88")
    elif op == TEST_OP.UPDATE:
        rslt = db.accountinfo_get_item()
        for row in rslt:
            print(row)

        db.accountinfo_update_item(
            "shawnelee882@gmail.com",
            "9999999",
            None,
            datetime.now(),
            datetime.now(),
            datetime.now(),
            1,
            1,
            None,
        )
        rslt = db.accountinfo_get_item()
        for row in rslt:
            print(row)
    elif op == TEST_OP.GET:
        rslt = db.accountinfo_get_item()
        for row in rslt:
            print(row)
    elif op == TEST_OP.DEL:
        db.accountinfo_del_item("shawnelee882@gmail.com")
        rslt = db.accountinfo_get_item()
        for row in rslt:
            print(row)
    db.close()
    del db


def dbg_shipaddr():
    op = TEST_OP.GET
    db = amazon_db()
    db.open()
    rslt = db.shipaddress_get_item()
    for row in rslt:
        print(row)

    if op == TEST_OP.ADD:
        # db.shipaddress_add_item('MarvinDickerson987@foxairmail.com', 'Jack Chan',  '1776 Bicentennial way, apt i-5','02911','North Providence','RI','6232295326')
        # db.shipaddress_add_item('AdamBright@foxairmail.com', 'Bing Tan', '3308 Trappers Cove Trail, Apt 3B', '48910', 'Lansing', 'MI', '6508890052')
        # db.shipaddress_add_item('DamaoWang@foxairmail.com', 'Zhiyuan Lan', '4 bud way, ste 16-201', '03063', 'nashua ', 'NH', '6035241562')
        db.shipaddress_add_item(
            "shawnelee88@gmail.com",
            "Zhiyuan Lan",
            "4 bud way, ste 16-201",
            "03063",
            "nashua ",
            "NH",
            "6035241562",
        )
        db.shipaddress_add_item(
            "shawnelee881@gmail.com",
            "shawnelee881",
            "4 bud way, ste 16-201",
            "03063",
            "nashua ",
            "NH",
            "6035241562",
        )
        db.shipaddress_add_item(
            "shawnelee882@gmail.com",
            "shawnelee882",
            "4 bud way, ste 16-201",
            "03063",
            "nashua ",
            "NH",
            "6035241562",
        )
    elif op == TEST_OP.UPDATE:
        rslt = db.shipaddress_get_item()
        for row in rslt:
            print(row)

        db.shipaddress_update_item(
            "shawnelee882@gmail.com",
            "shawnelee882222",
            "4 bud way, ste 16-202",
            "310000",
            "hangzhou ",
            "ZJ",
            "6035241562",
        )
        rslt = db.shipaddress_get_item()
        for row in rslt:
            print(row)
    elif op == TEST_OP.GET:
        rslt = db.shipaddress_get_item()
        for row in rslt:
            print(row)
    elif op == TEST_OP.DEL:
        db.shipaddress_del_item("shawnelee882@gmail.com")
        rslt = db.shipaddress_get_item()
        for row in rslt:
            print(row)

    db.close()
    del db


def dbg_finance():
    op = TEST_OP.GET
    db = amazon_db()
    db.open()
    rslt = db.finance_get_item()
    for row in rslt:
        print(row)

    if op == TEST_OP.ADD:
        # db.finance_add_item('MarvinDickerson987@foxairmail.com', 'Marvin Dickerson','4859106480044568',
        #                     '04','2022','TDLan-549','Marvin Dickerson','6 redglobe ct','29681-3615',
        #                     'simpsonville','SC','8645612655')
        # db.finance_add_item('AdamBright@foxairmail.com','Adam Bright','4859105152861630',
        #                     '04','2022','BOALI-848','Adam Bright','6614 Aden Ln, Apt 1','78739',
        #                     'Austin','TX','5756026422')
        db.finance_add_item(
            "shawnelee88@gmail.com",
            "Annie Lee",
            "4859109471703325",
            "04",
            "2022",
            "TDLan-549",
            "Annie Lee",
            "193 central st. ste W102",
            "03051",
            "nashua",
            "NH",
            "3054146488",
        )
        db.finance_add_item(
            "shawnelee881@gmail.com",
            "Bing Tan",
            "4859101936347160",
            "04",
            "2022",
            "TDLan-549",
            "Bing Tan",
            "3308 Trappers Cove Trail, Apt 3D",
            "48910",
            "Lansing",
            "MI",
            "6508890052",
        )
        db.finance_add_item(
            "shawnelee882@gmail.com",
            "Mineral Dick",
            "4859107167920401",
            "04",
            "2022",
            "TDLan-549",
            "Mineral Dick",
            "193 central st. Apt W253",
            "03051",
            "nashua",
            "NH",
            "4242237285",
        )
        rslt = db.finance_get_item()
        for row in rslt:
            print(row)
    elif op == TEST_OP.UPDATE:
        db.finance_update_item(
            "shawnelee882@gmail.com",
            "Mineral Dick111",
            "4859107167920401",
            "04",
            "2022",
            "TDLan-549",
            "Mineral Dick111",
            "193 central st. Apt W253",
            "03051",
            "hangzhou",
            "ZJ",
            "4242237285",
        )
        rslt = db.finance_get_item()
        for row in rslt:
            print(row)
    elif op == TEST_OP.GET:
        rslt = db.finance_get_item()
        for row in rslt:
            print(row)
    elif op == TEST_OP.DEL:
        db.finance_del_item("shawnelee882@gmail.com")
        rslt = db.finance_get_item()
        for row in rslt:
            print(row)
    db.close()
    del db


def dbg_accountquota():
    op = TEST_OP.GET
    db = amazon_db()
    db.open()
    rslt = db.accountquota_get_item()
    for row in rslt:
        print(row)

    if op == TEST_OP.ADD:
        db.accountquota_add_item("TDLan-549", 200, 800, 10000)
        db.accountquota_add_item("BOALI-848", 200, 800, 10000)
    elif op == TEST_OP.UPDATE:
        db.accountquota_update_item("TDLan-549", 200, 900, 10000)
        rslt = db.accountquota_get_item()
        for row in rslt:
            print(row)
    elif op == TEST_OP.GET:
        rslt = db.accountquota_get_item()
        for row in rslt:
            print(row)
    elif op == TEST_OP.DEL:
        db.accountquota_del_item("TDLan-548")
        rslt = db.accountquota_get_item()
        for row in rslt:
            print(row)
    db.close()
    del db


def dbg_productinfo():
    op = TEST_OP.GET
    db = amazon_db()
    db.open()
    rslt = db.productinfo_get_item()
    for row in rslt:
        print(row)
    if op == TEST_OP.ADD:
        db.productinfo_add_item(
            "B077RYNF82",
            "Electronics",
            "89.99",
            "89.99",
            "wireless bluetooth earbud",
            "STERIO",
        )
        db.productinfo_add_item(
            "B07439HNFT", "Electronics", "94.99", "94.99", "dash cam 4k", "STERIO"
        )
    elif op == TEST_OP.UPDATE:
        rslt = db.productinfo_get_item()
        for row in rslt:
            print(row)
        db.productinfo_update_item(
            "B07439HNFT", "Computer", "77.68", "88.67", "HD cam", "xiaomi"
        )
        for row in rslt:
            print(row)
    elif op == TEST_OP.GET:
        rslt = db.productinfo_get_item()
        for row in rslt:
            print(row)
    elif op == TEST_OP.DEL:
        db.productinfo_del_item("B07439HNad")
        rslt = db.productinfo_get_item()
        for row in rslt:
            print(row)
    db.close()
    del db


def dbg_ordertask():
    op = TEST_OP.GET
    db = amazon_db()
    db.open()
    rslt = db.ordertask_get_item()
    for row in rslt:
        print(row)
    if op == TEST_OP.ADD:
        db.ordertask_add_item("lee", "B077RYNF82", 10)
        db.ordertask_add_item("lee", "B07439HNFT", 20)
        db.ordertask_add_item("AnnieLee@foxairmail.com", "B07439HNFT", 30)
        db.ordertask_add_item("BingTan89@foxairmail.com", "B07439HNFT", 40)
        db.ordertask_add_item("MineralDick@foxairmail.com", "B077RYNF82", 50)
        rslt = db.ordertask_get_item()
        for row in rslt:
            print(row)
    elif op == TEST_OP.UPDATE:
        pass
    elif op == TEST_OP.GET:
        rslt = db.ordertask_get_item()
        for row in rslt:
            print(row)
    elif op == TEST_OP.DEL:
        pass
    db.close()
    del db


# select candidates which meets some requirements
# min_val:each buyer should spend minimum money
# buyer_interval:lastbuy time should be more than this, in hrs
def get_available_user(min_val, buyer_interval, asin_task):
    # get available users according to buyer_interval, should not use users which have purchased recently
    db = amazon_db()
    db.open()
    all_candidates = []

    asin_list = []
    asin_qnty_list = []
    asin_price_list = []

    for key, val in asin_task.items():
        product = db.productinfo_get_one_item(key)
        asin_list.append(key)
        asin_qnty_list.append(val)
        asin_price_list.append(product["order_price"])
        print(product)

    for i in range(len(asin_list)):
        print(asin_list[i], asin_price_list[i], asin_qnty_list[i])

    accountinfo_rslt = db.accountinfo_get_item_by_lastbuy(buyer_interval)
    print("**********get users according to buyer_interval**********")
    for row in accountinfo_rslt:
        # print(row)
        candidate = {}
        candidate["accountinfo"] = row
        # get users' shipaddress
        shipaddr_result = db.shipaddress_get_item_by_username(row["username"])
        # print(shipaddr_result)
        if shipaddr_result == None:
            print("No Shipaddress Found:", row["username"])
            candidate["shipaddress"] = None
        else:
            candidate["shipaddress"] = shipaddr_result

        # get bank-account those users are using, check if quota enough
        # print('\n**********get finance according to user candidate**********')
        finance_rslt = db.finance_get_item_by_username(row["username"])
        candidate["finance"] = finance_rslt
        if finance_rslt == None:
            print("No Finance Found:", row["username"])
            candidate["accountquota"] = None
        else:
            quota_rslt = db.accountquota_get_one_item(finance_rslt["checkaccount"])
            candidate["accountquota"] = quota_rslt
            if quota_rslt["mquota"] < min_val:
                continue
            val_per_user = 0
            asin_per_user = []
            for i in range(len(asin_list)):
                if asin_qnty_list[i]:
                    val_per_user += asin_price_list[i]
                    asin_per_user.append(asin_list[i])
                    asin_qnty_list[i] -= 1
                    if val_per_user >= min_val and val_per_user < quota_rslt["mquota"]:
                        break

            print(asin_per_user)
            candidate["asinlist"] = asin_per_user
            all_candidates.append(candidate)

        left_asin_count = 0
        for i in range(len(asin_list)):
            if asin_qnty_list[i]:
                left_asin_count = 1
        if left_asin_count == 0:
            break

    for candidate in all_candidates:
        for tbl, info in candidate.items():
            print("tbl:", tbl, ",info:", info)

    db.close()
    del db


dbg_accountinfo()
# dbg_shipaddr()
# dbg_finance()
# dbg_accountquota()
# dbg_productinfo()
# dbg_ordertask()
#get_available_user(150, 24, {'B077RYNF82':2, 'B07439HNFT':1})

if __name__ == "__main__":
    pass
