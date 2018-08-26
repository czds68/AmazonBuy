import os
import re
tt = os.system("sudo spoof-mac.py list")

def GetMacAddress():
    MacFilter = re.compile(r'[:0-9A-F]')
    output = str(os.popen('sudo spoof-mac.py list'))
    return ( MacFilter.findall(output)[0])

print(GetMacAddress())