import os
import re
tt = os.system("sudo spoof-mac.py list")

def GetMacAddress():
    MacFilter = re.compile(r'[:0-9A-Fa-f]{17}')
    output = str(os.popen('sudo spoof-mac.py list').read())
    return ( MacFilter.findall(output)[0])

print(GetMacAddress())