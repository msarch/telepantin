#/usr/bin/python
# -*- coding: iso-8859-1 -*-


# -------------------- STANDARD PYGLET CANVAS ENGINE (rev X) ------------------
import pyglet
from pyglet.gl import *
from collections import namedtuple
from colors import BACKGROUND_COLOR

# Point is used all over to store x,y coords
Point = namedtuple('Pt', 'x y')  # name, x coord, y coord
Pt = Point

# Canvas yelds a regular rotation angle value
REV_PER_SEC = 0.1                   # angular velocity 0.5= 0.5rev/s
alpha = 0.0                         # flywheel initial angle

# initial state
CANVAS_PAUSED = True

# Pyglet Window stuff
CANVAS = pyglet.window.Window(fullscreen=True)
CANVAS_WIDTH, CANVAS_HEIGHT = CANVAS.width, CANVAS.height
CANVAS_CENTER = Point(CANVAS_WIDTH/2, CANVAS_HEIGHT/2)
CANVAS_BOTTOM_LEFT = Point(0,0)

# OpenGL stuff
glClearColor(*BACKGROUND_COLOR)               # background color
glEnable(GL_LINE_SMOOTH)
glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
glEnable(GL_BLEND)                                  # transparency
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)   # transparency
#glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)          # wireframe only mode

@CANVAS.event
def redraw(dt):
    CANVAS.clear()
    BATCH.draw()

@CANVAS.event
def on_key_press(key, modifiers):
    global CANVAS_PAUSED
    if key == pyglet.window.key.SPACE: CANVAS_PAUSED = not(CANVAS_PAUSED)
    elif key == pyglet.window.key.ESCAPE:  # = Q with AZERTY kbd
        print ''
        print '       *    b y e    *'
        print ''
        pyglet.app.exit()

BATCH = pyglet.graphics.Batch()  # holds all vertex lists

def run():
    pyglet.clock.schedule_interval(redraw, 1.0/120)
    pyglet.app.run()

# Sketch class ----------------------------------------------------------------
class Sketch(pyglet.graphics.Group): # subclass with position/rotation ability
    '''
    'sketches' are regular pyglet graphics.Groups
    'set_state' and 'unset_state' methods are used for animation purpose.
    Sketches are translated and rotated every redraw
    self.pos and self.heading
    '''
    def __init__(self,pos=CANVAS_CENTER, heading=0):  # pos=x,y coords, heading=rot. angle
        super(Sketch, self).__init__()
        self.pos, self.heading = pos, heading

    def set_state(self):
        glPushMatrix()
        glRotatef(self.heading, 0, 0, 1) # GL rot. in degrees; x,y,z of rot. axis
        glTranslatef(self.pos.x, self.pos.y, 0) # translate after rotation

    def unset_state(self):
        glPopMatrix()

BACKGROUND = Sketch()  # default sketch
ORIGIN = Point(0,0)

print '+ canvas.py loaded'


#---------------------------------- MAIN --------------------------------------
if __name__ == "__main__":
    run()

