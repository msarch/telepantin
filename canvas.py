
# -------------------- STANDARD ENGINE SECTION (rev 9) --------------------
import pyglet
from pyglet.gl import *
from collections import namedtuple
from itertools import cycle
from math import  atan, cos, hypot, pi, sin
from sys import stdout

Color = namedtuple('Color', 'r g b a') # RGB+ alpha (0 to 255)
Point = namedtuple('Point', 'id x y')  # name + 2 coordinates
Pt = Point
Edge = namedtuple('Edge', 'id start end color') # name + 2 pts + color

ORIGIN = Point('O',0,0)
OO=ORIGIN
TWOPI = 2*pi
BLACK = Color(  0,   0,   0, 255)
WHITE = Color(255, 255, 255, 255)
CLINE = Color(125, 125, 100, 100)   # construction lines color
REV_PER_SEC = 0.1                   # angular velocity 0.5= 0.5rev/s
alpha = 0.0                         # flywheel initial angle


# Pyglet Window stuff ---------------------------------------------------------
batch = pyglet.graphics.Batch()  # holds all graphics
config = Config(sample_buffers=1, samples=4, depth_size=16,
                double_buffer=True, mouse_visible=False)
window = pyglet.window.Window(fullscreen=not(WINDOWED), config=config)
SCREEN_WIDTH, SCREEN_HEIGHT = window.width, window.height

glClearColor(*BLACK)  # background color
glEnable(GL_LINE_SMOOTH)
glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
glEnable(GL_BLEND)                                  # transparency
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)   # transparency
#glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)          # wireframe view mode

@window.event
def draw():
    window.clear()
    batch.draw()

@window.event
def on_key_press(key, modifiers):
    global PAUSED
    if key == pyglet.window.key.SPACE: PAUSED = not(PAUSED)
    elif key == pyglet.window.key.A:  # = Q with AZERTY kbd
        print ''
        print '* * * * * * * * * * * * * user quit * * * * * * * * * * * * * *'
        print ''
        pyglet.app.exit()

def update(dt):
    # alpha is updated at constant speed as in an uniform circular motion
    # custom scene actions should update using alpha
    global alpha
    if PAUSED: pass
    else:
        alpha +=  dt * REV_PER_SEC * 360  # alpha is in degrees
        if alpha > 360 : alpha -= 360    # stay within [0,360°]

        if VERBOSE:
            global frame_number, duration
            frame_number +=1
            duration += dt
            print ''
            print '---------------------------------------------------------------'
            print '-'
            print '-                    updating'
            print '-                    . alpha    :', alpha
            print '-                    . duration :', duration
            print '-                    . frame #  :', frame_number
            print '-                    . FPS      :', 1/dt
            print '-'
            print '---------------------------------------------------------------'
            print ''

        scene_update(dt)

    draw()


# Sketch class ----------------------------------------------------------------
class Sketch(pyglet.graphics.Group): # subclass with position/rotation ability
    '''
    'sketches' are regular pyglet graphics.Groups whom 'set_state' and
    'unset_state' methods are used to add move and rotate functionnalities.
    '''
    def __init__(self,pos=ORIGIN, ro=0):  # pos=x,y coords, ro=rot. angle
        super(Sketch, self).__init__()
        self.pos, self.ro = pos, ro

    def set_state(self):
        glPushMatrix()
        glRotatef(self.ro, 0, 0, 1) # GL rot. in degrees; x,y,z of rot. axis
        glTranslatef(self.pos.x, self.pos.y, 0) # translate after rotation

    def unset_state(self):
        glPopMatrix()

# }}} --------------------- END OF STANDARD ENGINE SECTION --------------------


