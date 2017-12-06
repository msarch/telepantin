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

