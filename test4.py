from difflib import SequenceMatcher

a = '1231af987666u12dasfinggysuyuiij'
b = '12dfsuyuiij'

print(SequenceMatcher(None,a,b).get_opcodes())

for item in a:
    print(item)

ff = ('erw','343')
print(ff[1])

def SMacth(StrA,StrB, Ratio = 0.8, CaseSensitive = False):
    if CaseSensitive == False:
        TestA = StrA.lower()
        TestB = StrB.lower()
    else:
        TestA = StrA
        TestB = StrB
    if len(StrA) > len(StrB):
        ShorterLenght = len(StrB)
    else:
        ShorterLenght = len(StrA)

    DiffResult = SequenceMatcher(None,TestA,TestB).get_opcodes()
    SameCounter = 0
    for diff in DiffResult:
        if diff[0] == 'equal':
            SameCounter += diff[2] - diff[1] + 1
    if SameCounter/ShorterLenght >= Ratio:
        return True
    else:
        return False

print(SMacth(a,b))
