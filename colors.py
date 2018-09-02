#/usr/bin/python
# -*- coding: iso-8859-1 -*-


# ------------------------- STANDARD COLORS (rev 1) ---------------------------
from collections import namedtuple

Color = namedtuple('Color', 'r g b a') # RGB+ alpha (0 to 255)

BLACK = Color(  0,   0,   0, 255)
WHITE = Color(255, 255, 255, 255)
DULL  = Color(125, 125, 100, 100)   # construction lines color
TRANS = Color( 50,  50,  50, 100)

print '+ colors.py loaded'


'''
class for printing terminal text in colors,
To use code like this, you can do something like

    print tt.blue
    print 'test'
    print tt.RESET

'''

class Term:

    RED='\033[31m'
    lightred='\033[91m'
    pink='\033[95m'
    GREEN = '\033[92m'
    green='\033[32m'
    lightgreen='\033[92m'
    BLUE = '\033[94m'
    blue='\033[34m'
    lightblue='\033[94m'
    cyan='\033[36m'
    lightcyan='\033[96m'
    purple='\033[35m'
    YELLOW = '\033[93m'
    orange='\033[33m'
    BLACK='\033[30m'
    darkgrey='\033[90m'
    lightgrey='\033[37m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    RESET = '\033[0m'


#-------------------------- MAIN for SELF-TESTING -----------------------------
if __name__ == "__main__":

    print term.blue
    print 'test'
    print term.RESET

