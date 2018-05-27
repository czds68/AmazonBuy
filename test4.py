from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import zipfile
import os
from datetime import datetime

output_capture = os.path.expanduser("~/Dropbox/amazon/counterCAPTURE")


def proxyanalysis(text):
    t = text.find(":")
    # print t
    ip = text[0:t]
    # print ip
    rest = text[t + 1:]
    # print rest
    t = rest.find(":")
    # print t
    port = rest[0:t]
    # print port
    rest = rest[t + 1:]
    # print rest
    t = rest.find(":")
    username = rest[0:t]
    password = rest[t + 1:]
    # print username, password
    return ip, port, username, password


def checkintheblacklist(proxyi):
    with open(output_capture) as f:
        content = f.read().splitlines()
        content = filter(None, content)
    today = str(datetime.now()).split(" ")[0]
    b = [x for x in content if x.split(" ")[0] == today and x.split(" ")[3] == proxyi]
    # print content
    # print b
    ## b is the list that contains the record of inputed proxyi at today
    if not b:
        # if b is empty, then the proxy is not blocked
        return (0)
    else:
        print
        "IP is blocked"
        return (1)


def main(i, proxyi):
    if checkintheblacklist(proxyi) == 0:
        ip, port, username, password = proxyanalysis(proxyi)
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
        pluginfile = 'proxy_auth_plugin' + str(i) + '.zip'
        # print pluginfile

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        co = Options()
        prefs = {"profile.managed_default_content_settings.images": 2}
        co.add_experimental_option("prefs", prefs)
        # co.add_argument("--start-maximized")
        co.add_extension(pluginfile)
        driver = webdriver.Chrome(chrome_options=co)
        print
        "thread %d : Ip: %s" % (i, ip)
        return driver


