#/usr/bin/python
# -*- coding: iso-8859-1 -*-


# -------------------- STANDARD PYGLET CANVAS ENGINE (rev X) ------------------
import pyglet
from pyglet.gl import *
from pyglet.graphics import Batch
from colors import BLACK


# Pyglet Window ---------------------------------------------------------------
CANVAS = pyglet.window.Window(fullscreen=True)      # The Pyglet Window
CANVAS_WIDTH, CANVAS_HEIGHT = CANVAS.width, CANVAS.height
CANVAS_CENTER = (CANVAS_WIDTH/2, CANVAS_HEIGHT/2)
CANVAS_PAUSED = False                               # canvas initial state

# OpenGL stuff
glClearColor(*BLACK)                     # background color
glEnable(GL_LINE_SMOOTH)
glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
glEnable(GL_BLEND)                                  # transparency
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)   # transparency
#glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)          # wireframe only mode

@CANVAS.event
def redraw():
    CANVAS.clear()
    BATCH.draw()

@CANVAS.event
def on_key_press(key, modifiers):
    '''
    # PAUSE and QUIT actions
    '''
    if key == pyglet.window.key.SPACE:
        global CANVAS_PAUSED
        CANVAS_PAUSED = not CANVAS_PAUSED
        print '+ key pressed :  ___'
    elif key == pyglet.window.key.ESCAPE:  # = Q with AZERTY kbd
        print '+ key pressed :  ESC'
        print ''
        print '           *    b y e    *'
        print ''
        pyglet.app.exit()

def run():
    pyglet.app.run()


# Sketch class ----------------------------------------------------------------
class Sketch(pyglet.graphics.Group): # subclass with position/rotation ability
    '''
    'sketches' are regular pyglet graphics.Groups
    'set_state' and 'unset_state' methods are used for animation purpose.
    Sketches can be translated and rotated every redraw
    self.pos and self.heading
    '''
    def __init__(self,pos=CANVAS_CENTER, heading=0):  # pos=x,y coords, heading=rot. angle
        super(Sketch, self).__init__()
        self.pos = pos
        self.heading = heading

    def set_state(self):
        glPushMatrix()
        glRotatef(self.heading, 0, 0, 1) # GL rot. in degrees; x,y,z of rot. axis
        glTranslatef(self.pos[0], self.pos[1], 0) # translate after rotation

    def unset_state(self):
        glPopMatrix()


BACKGROUND = Sketch()            # default sketch
BATCH = Batch()                  # holds all vertex lists
print '+ canvas.py loaded'


#-------------------------- MAIN for SELF-TESTING -----------------------------
if __name__ == "__main__":
    redraw()
    run()

