#/usr/bin/python
# -*- coding: iso-8859-1 -*-


# ------------------------- STANDARD COLORS (rev 1) ---------------------------
from collections import namedtuple

Color = namedtuple('Color', 'r g b a') # RGB+ alpha (0 to 255)

BLACK = Color(  0,   0,   0, 255)
WHITE = Color(255, 255, 255, 255)
CLINE = Color(125, 125, 100, 100)   # construction lines color
BACKGROUND_COLOR = Color(0, 0, 0, 255)

print '+ colors.py loaded'

'''
class for printing terminal text in colors,
To use code like this, you can do something like

    print tt.blue
    print 'test'
    print tt.RESET

'''

class tt:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'

    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    black='\033[30m'
    red='\033[31m'
    green='\033[32m'
    orange='\033[33m'
    blue='\033[34m'
    purple='\033[35m'
    cyan='\033[36m'
    lightgrey='\033[37m'
    darkgrey='\033[90m'
    lightred='\033[91m'
    lightgreen='\033[92m'
    lightblue='\033[94m'
    pink='\033[95m'
    lightcyan='\033[96m'



#-------------------------- MAIN for SELF-TESTING -----------------------------
if __name__ == "__main__":

    print tt.blue
    print 'test'
    print tt.RESET

