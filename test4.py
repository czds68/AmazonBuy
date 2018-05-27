import re
ttt = 'Phone:1432432'.lower()
ff = re.compile("[ .-]")
print(ff.sub(repl='',string=ttt))