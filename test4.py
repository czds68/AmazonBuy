import  os
tt = os.system("sudo spoof-mac.py list")

def GetMacAddress():
    output = os.popen('sudo spoof-mac.py list')
    print( output.read())
