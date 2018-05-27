from datetime import date, datetime
import mysql.connector

config = {
  'user': 'root',
  'password': 'Max123',
  'host': 'czds68.yicp.io',
  'port':'4406',
  'database': 'amazon'
}
lock_accountinfo_read = ("LOCK TABLE accountinfo READ;")
lock_shipaddress_read = ("LOCK TABLE shipaddress READ;")
lock_finance_read = ("LOCK TABLE finance READ;")
lock_accountquota_read = ("LOCK TABLE accountquota READ;")
lock_accountinfo_write = ("LOCK TABLE accountinfo WRITE;")
lock_shipaddress_write = ("LOCK TABLE shipaddress WRITE;")
lock_finance_write = ("LOCK TABLE finance WRITE;")
lock_accountquota_write = ("LOCK TABLE accountquota WRITE;")
lock_rd_ops = {'accountinfo':lock_accountinfo_read,
            'shipaddress':lock_shipaddress_read, 
            'finance':lock_finance_read, 
            'accountquota':lock_accountquota_read}
lock_wr_ops = {'accountinfo':lock_accountinfo_write,
            'shipaddress':lock_shipaddress_write,
            'finance':lock_finance_write,
            'accountquota':lock_accountquota_write}
unlock_all = ("UNLOCK TABLES;")

add_accountinfo = ("INSERT INTO accountinfo"
                    "(username, password, cookies, createdate, logindate, alive, MAC)"
                    "VALUES (%s, %s, %s, %s, %s, %s, %s);")
add_shipaddr = ("INSERT INTO shipaddress "
                "(username, fullname, address, postalcode, city, state, phonenumber)"
                "VALUES (%s,%s,%s,%s,%s,%s,%s)")
add_finance = ("INSERT INTO finance "
                "(username,nameoncard,ccnumber,ccmonth,ccyear,checkaccount,fullname,address, postalcode,city,state,phonenumber) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
add_quota = ("INSERT INTO accountquota"
                "(checkaccount,wquota,mquota,yquota)"
                "VALUES (%s,%s,%s,%s)")
get_accountinfo = ("SELECT * FROM accountinfo;")
get_shipaddr = ("SELECT * FROM shipaddress;")
get_finance = ("SELECT * FROM finance;")
get_quota = ("SELECT * FROM accountquota;")

#select xxx from xxx where xxx lock in share mode;
#select xxx from xxx where xxx for udpate;

#update_accountinfo_username = ("UPDATE accountinfo SET username=%s WHERE username=%s;")
update_accountinfo_pw = ("UPDATE accountinfo SET password=%s WHERE username=%s;")
update_accountinfo_cookie = ("UPDATE accountinfo SET cookies=%s WHERE username=%s;")
update_accountinfo_createdate = ("UPDATE accountinfo SET createdate=%s WHERE username=%s;")
update_accountinfo_logindate = ("UPDATE accountinfo SET logindate=%s WHERE username=%s;")
update_accountinfo_alive = ("UPDATE accountinfo SET alive=%s WHERE username=%s;")
update_accountinfo_MAC = ("UPDATE accountinfo SET MAC=%s WHERE username=%s;")
update_accountinfo_ops = {
              'password':update_accountinfo_pw,
              'cookies':update_accountinfo_cookie,
              'createdate':update_accountinfo_createdate,
              'logindate':update_accountinfo_logindate,
              'alive':update_accountinfo_alive,
              'MAC':update_accountinfo_MAC}
update_shipaddress_fullname = ("UPDATE shipaddress SET fullname=%s WHERE username=%s;")
update_shipaddress_address = ("UPDATE shipaddress SET address=%s WHERE username=%s;")
update_shipaddress_postalcode = ("UPDATE shipaddress SET postalcode=%s WHERE username=%s;")
update_shipaddress_city = ("UPDATE shipaddress SET city=%s WHERE username=%s;")
update_shipaddress_state = ("UPDATE shipaddress SET state=%s WHERE username=%s;")
update_shipaddress_phonenumber = ("UPDATE shipaddress SET phonenumber=%s WHERE username=%s;")
update_shipaddress_ops = {
              'fullname':update_shipaddress_fullname,
              'address':update_shipaddress_address,
              'postalcode':update_shipaddress_postalcode,
              'city':update_shipaddress_city,
              'state':update_shipaddress_state,
              'phonenumber':update_shipaddress_phonenumber}
update_finance_nameoncard = ("UPDATE finance SET nameoncard=%s WHERE username=%s;")
update_finance_ccnumber = ("UPDATE finance SET ccnumber=%s WHERE username=%s;")
update_finance_ccmonth = ("UPDATE finance SET ccmonth=%s WHERE username=%s;")
update_finance_ccyear = ("UPDATE finance SET ccyear=%s WHERE username=%s;")
update_finance_checkaccount = ("UPDATE finance SET checkaccount=%s WHERE username=%s;")
update_finance_fullname = ("UPDATE finance SET fullname=%s WHERE username=%s;")
update_finance_address = ("UPDATE finance SET address=%s WHERE username=%s;")
update_finance_postalcode = ("UPDATE finance SET postalcode=%s WHERE username=%s;")
update_finance_city = ("UPDATE finance SET city=%s WHERE username=%s;")
update_finance_state = ("UPDATE finance SET state=%s WHERE username=%s;")
update_finance_phonenumber = ("UPDATE finance SET phonenumber=%s WHERE username=%s;")
update_finance_ops = {
            'nameoncard':update_finance_nameoncard,
            'ccnumber':update_finance_ccnumber,
            'ccmonth':update_finance_ccmonth,
            'ccyear':update_finance_ccyear,
            'checkaccount':update_finance_checkaccount,
            'fullname':update_finance_fullname,
            'address': update_finance_address,
            'postalcode': update_finance_postalcode,
            'city':update_finance_city,
            'state':update_finance_state,
            'phonenumber':update_finance_phonenumber}

update_accountquota_wquota = ("UPDATE accountquota SET wquota=%s WHERE checkaccount=%s;")
update_accountquota_mquota = ("UPDATE accountquota SET mquota=%s WHERE checkaccount=%s;")
update_accountquota_yquota = ("UPDATE accountquota SET yquota=%s WHERE checkaccount=%s;")
update_finance_ops = {
            'wquota':update_accountquota_wquota,
            'mquota':update_accountquota_mquota,
            'yquota':update_accountquota_yquota}
#{'accountinfo':{username=xx, password=xx,cookies=None,createdata=datetime.now(),logindate=datetime.now(),alive=1,MAC=None}}
accountinfo_fields = ('username', 'password', 'cookies', 'createdate', 'logindate', 'alive', 'MAC')
shipaddress_fields = ('username', 'fullname', 'address', 'postalcode', 'city', 'state', 'phonenumber')
finance_fields = ('username','nameoncard','ccnumber','ccmonth','ccyear','checkaccount','fullname','address', 'postalcode','city','state','phonenumber')
quota_fields = ('checkaccount','wquota','mquota','yquota')
userinfo_op = {'accountinfo':{'add_method':add_accountinfo, 'fields':accountinfo_fields, 'get_method':get_accountinfo},
                'shipaddress':{'add_method':add_shipaddr, 'fields':shipaddress_fields, 'get_method':get_shipaddr},
                'finance':{'add_method':add_finance, 'fields':finance_fields, 'get_method':get_finance},
                'accountquota':{'add_method':add_quota, 'fields':quota_fields, 'get_method':get_quota}}

#one table at a time
def add_userinfo(**kw):
    for i in userinfo_op.keys():
        if i in kw:
            print('adding item (%s,%s)' % (i,lock_wr_ops[i]))
            cursor.execute(lock_wr_ops[i])
            execute_dll_list = []
            for j in userinfo_op[i]['fields']:
                execute_dll_list.append(kw[i][j])
            execute_dll_tuple = tuple(execute_dll_list)
            print(execute_dll_tuple)
            cursor.execute(userinfo_op[i]['add_method'], execute_dll_tuple)
            cursor.execute(unlock_all)
            cnx.commit()
    return

#can get all table at once
def get_userinfo(*args):
    rslt = {}
    for tbl in args:
        print(tbl)
        cursor.execute(lock_rd_ops[tbl])
        if tbl in userinfo_op.keys():
            cursor.execute(userinfo_op[tbl]['get_method'])
            tmp_rslt = {}
            return_rslt = cursor.fetchall()
            for row in return_rslt:
                for i in range(len(row)):
                    #print(row[i])
                    if i >= 1:
                        tmp_rslt[userinfo_op[tbl]['fields'][i-1]] = row[i]
            rslt[tbl] = tmp_rslt
        cursor.execute(unlock_all)
        #cnx.commit()
    #print(rslt)
    return rslt

#one table at a time
#{table:{field1:value, field2:value}}
def set_userinfo(**kw):
    for table in userinfo_op.keys():
        cursor.execute(lock_wr_ops[table])
        if table in kw:
            print('set item:', kw)
            for k,v in kw[table].items():
                if k != 'username':
                    insert_val = [v, kw[table]['username']]
                    cursor.execute(update_accountinfo_ops[k], tuple(insert_val))
        cursor.execute(unlock_all)
        cnx.commit()
    return

test_accountinfo = {'accountinfo':{
                        'username':'MarvinDickerson987@foxairmail.com',
                        'password':'MarvinDickerson987',
                        'cookies':None,
                        'createdate':datetime.now(),
                        'logindate':datetime.now(),
                        'alive':1,
                        'MAC':None}}
test_shipaddress = { 'shipaddress':{
                    'username':'MarvinDickerson987@foxairmail.com',
                    'fullname':'Jack Chan',
                    'address':'1776 Bicentennial way, apt i-5',
                    'postalcode':'02911',
                    'city':'North Providence',
                    'state':'RI',
                    'phonenumber':'6232295326'}}

test_finance = {'finance':{
                'username':'MarvinDickerson987@foxairmail.com',
                'nameoncard':'Marvin Dickerson',
                'ccnumber':'4859106480044568',
                'ccmonth':'04',
                'ccyear':'2022',
                'checkaccount':'TDLan-549',
                'fullname':'Marvin Dickerson',
                'address':'6 redglobe ct',
                'postalcode':'29681-3615',
                'city':'simpsonville',
                'state':'SC',
                'phonenumber':'8645612655'}}
test_quota = {'accountquota':{
                'checkaccount':'TDLan-549',
                'wquota':200,
                'mquota':800,
                'yquota': 10000}}

test_update_accountinfo_mac = {'accountinfo':{
                                'username':'MarvinDickerson987@foxairmail.com',
                                'MAC': '00-00-00-00-00-00',
                                'password':'0987654321'}}
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
add_userinfo(**test_accountinfo)
#add_userinfo(**test_shipaddress)
#add_userinfo(**test_finance)
#add_userinfo(**test_quota)
#set_userinfo(**test_update_accountinfo_mac)
#get_userinfo('accountinfo')
#get_userinfo('shipaddress')
#get_userinfo('finance')
get_userinfo('accountquota')
cursor.close()
cnx.close()