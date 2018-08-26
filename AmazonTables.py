from difflib import SequenceMatcher
import re
import os

def GetMacAddress():
    MacFilter = re.compile(r'[:0-9A-Fa-f]{17}')
    output = str(os.popen('sudo spoof-mac.py list').read())
    return ( MacFilter.findall(output)[0])

def SMatch(StrA,StrB, Ratio = 0.50, CaseSensitive = False, SubSymbol = True,MatchLengthRate = 1.8):
    if not StrA or not StrB:
        return False
    if CaseSensitive == False:
        TestA = StrA.lower()
        TestB = StrB.lower()
    else:
        TestA = StrA
        TestB = StrB
    if SubSymbol:
        Replace = re.compile("[ \!\@\#\$\%\^\&\*\(\)_+\{\}|:\"<>\?\-=\[\]\\;',./\']")
        TestA = Replace.sub(repl='', string=TestA)
        TestB = Replace.sub(repl='', string=TestB)
    if len(TestA) > len(TestB):
        ShorterLenght = len(TestB)
        LongerLength = len(TestA)
        ShortString = TestB
        LongerString = TestA
    else:
        ShorterLenght = len(TestA)
        LongerLength = len(TestB)
        ShortString = TestA
        LongerString = TestB
    StartOffset = 0
    while True:
        EnfOffset = StartOffset + int(float(ShorterLenght * MatchLengthRate))
        DiffA = ShortString
        DiffB = LongerString[StartOffset:EnfOffset]
        DiffResult = SequenceMatcher(None, DiffA, DiffB).get_opcodes()
        SameCounter = 0
        SplitCounter = 0
        for diff in DiffResult:
            if diff[0] == 'equal':
                SplitCounter += 1
                SameCounter += diff[2] - diff[1]
        if (SameCounter / ShorterLenght >= Ratio) and (SplitCounter <= 3):
            return True
        if EnfOffset > LongerLength:
            break
        StartOffset += 1
    return False


chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'


def URLDomains(Country = 'us'):
    URLTables = {'us': 'https://www.amazon.com/',
                'ca': 'https://www.amazon.ca/',
                'uk': 'https://www.amazon.co.uk/',
                'au':'https://www.amazon.com.au/'}
    if URLTables[Country]:
        return URLTables[Country]
    else:
        return URLTables['us']

DepartmentTable = {'Magazine Subscriptions': 'search-alias=magazines',
                   'Appliances': 'search-alias=appliances',
                   'Credit and Payment Cards': 'search-alias=financial',
                   'Amazon Warehouse Deals': 'search-alias=warehouse-deals',
                   'Amazon Devices': 'search-alias=amazon-devices',
                   'Alexa Skills': 'search-alias=alexa-skills',
                   'All Departments': 'search-alias=aps',
                   'Beauty & Personal Care': 'search-alias=beauty',
                   'Sports & Outdoors': 'search-alias=sporting',
                   'Software': 'search-alias=software',
                   'Industrial & Scientific': 'search-alias=industrial',
                   'Movies & TV': 'search-alias=movies-tv',
                   'Vehicles': 'search-alias=vehicles',
                   'Collectibles & Fine Art': 'search-alias=collectibles',
                   'Kindle Store': 'search-alias=digital-text',
                   'Cell Phones & Accessories': 'search-alias=mobile',
                   'Pet Supplies': 'search-alias=pets',
                   'Health, Household & Baby Care': 'search-alias=hpc',
                   'Prime Video': 'search-alias=instant-video',
                   'Electronics': 'search-alias=electronics',
                   'Computers': 'search-alias=computers',
                   'Arts, Crafts & Sewing': 'search-alias=arts-crafts',
                   'Courses': 'search-alias=courses',
                   'Luggage & Travel Gear': 'search-alias=fashion-luggage',
                   'CDs & Vinyl': 'search-alias=popular',
                   'Toys & Games': 'search-alias=toys-and-games',
                   'Digital Music': 'search-alias=digital-music',
                   'Video Games': 'search-alias=videogames',
                   'Grocery & Gourmet Food': 'search-alias=grocery',
                   'Clothing, Shoes & Jewelry': 'search-alias=fashion',
                   'Tools & Home Improvement': 'search-alias=tools',
                   'Office Products': 'search-alias=office-products',
                   'Apps & Games': 'search-alias=mobile-apps',
                   '-Women': 'search-alias=fashion-womens',
                   'Prime Exclusive Savings': 'search-alias=prime-exclusive',
                   'Handmade': 'search-alias=handmade',
                   'Musical Instruments': 'search-alias=mi',
                   'Gift Cards': 'search-alias=gift-cards',
                   '-Men': 'search-alias=fashion-mens',
                   'Prime Pantry': 'search-alias=pantry',
                   'Baby': 'search-alias=baby-products',
                   '-Baby': 'search-alias=fashion-baby',
                   'Home & Kitchen': 'search-alias=garden',
                   'Garden & Outdoor': 'search-alias=lawngarden',
                   'Home & Business Services': 'search-alias=local-services',
                   '-Girls': 'search-alias=fashion-girls',
                   '-Boys': 'search-alias=fashion-boys',
                   'Luxury Beauty': 'search-alias=luxury-beauty',
                   'Automotive Parts & Accessories': 'search-alias=automotive',
                   'Books': 'search-alias=stripbooks'}
