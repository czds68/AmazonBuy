import imaplib
import email
import re
import traceback


IMPA4_server = 'imap.sina.com'
IMPA4_mail = 'hellonihao7845@sina.com'
IMPA4_pwd = 'hellonihao7845'
usefakemail = False

def getverifycode(username, password, RetryNum = 10):
    if not usefakemail:
        IMPA4_mail = username
        IMPA4_pwd = password
    else:
        IMPA4_mail = 'hellonihao7845@sina.com'
        IMPA4_pwd = 'hellonihao7845'
    try:
        mail = imaplib.IMAP4_SSL(IMPA4_server)
        mail.login(IMPA4_mail, IMPA4_pwd)
        mail.select('INBOX')
        type, data = mail.search(None, 'ALL')
        maillist = data[0].split()
        Retry = 0
        while Retry < RetryNum:
            Retry += 1
            type, data = mail.fetch(maillist[-Retry], '(RFC822)')
            msg = email.message_from_string(data[0][1].decode('utf-8'))
            if (username in msg.get('to')) and ('Your Amazon verification code' in msg.get('subject')
                                                or 'Amazon sign-in code' in msg.get('subject')
                                                or 'One-time Password for Amazon account' in msg.get('subject')):
                print('Verification code got!')
                return re.compile('[0-9]+').findall(
                    re.compile('<p class.+[0-9]+</p>').findall(data[0][1].decode('utf-8'))[0])[0]
    except:
        print(traceback.print_exc())
        pass
    finally:
        mail.close()
        mail.logout()
    print('Fail to find verify code!')
    return False
if __name__ == "__main__":
    username = 'MarvinDickerson74@foxairmail.com'
    RetryNum = 20
    getverifycode(username, RetryNum)




