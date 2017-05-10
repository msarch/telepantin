#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# simple pyglet animation
# http://www.github.com/msarch/slide

# {{{ -------------------- STANDARD ENGINE SECTION (rev 1.0.0) ----------------
import math
import pyglet
from pyglet.gl import *

PI = math.pi
DEG2RAD = 2 * PI / 360
OMEGA = 360.0 * 0.1                           # angular velocity (360 = 1rev/s)
SCREEN_WIDTH, SCREEN_HEIGHT = 1280,800
ORIGIN = [SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 0] # screen center, rotation = 0
alpha = 0.0                                   # initial angle
vis = 1                                       # visibility switch
# Sketch class ----------------------------------------------------------------
class Sketch(pyglet.graphics.Group): # subclass with position/rotation ability
    '''
    'sketches' are regular pyglet graphics.Groups whom 'set_state' and
    'unset_state' methods are used to add move and rotate functionnalities.
    Adding a shape to a group (batch.add) returns the matching vertex list,
    color and vertex position are accessible through .colors and .vertices
    '''
    def __init__(self,pos=ORIGIN):
        super(Sketch, self).__init__()
        self.pos=pos

    def set_state(self):
        glPushMatrix()
        glTranslatef(self.pos[0], self.pos[1], 0)
        glRotatef(self.pos[2], 0, 0, 1) # rot. in degrees; x,y,z of rot. axis

    def unset_state(self):
        glPopMatrix()

# vertex_list modifier function -----------------------------------------------
def translate(vtx,pos): # modifying a list of vertices at once to new pos
    return(reduce(tuple.__add__, zip([x+pos[0] for x in vtx[0::2]],
    [y+pos[1] for y in vtx[1::2]])))

# Pyglet Window stuff ---------------------------------------------------------
batch = pyglet.graphics.Batch()  # holds all graphics
canvas = pyglet.window.Window(fullscreen=True)
canvas.set_mouse_visible(False)

glEnable(GL_LINE_SMOOTH)
glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
glEnable(GL_BLEND)                                  # transparency
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)   # transparency
black   =(  0,   0,   0, 255)
glClearColor(*black)  # background color

@canvas.event
def on_key_press(symbol, modifiers):
    global vis
    if symbol == pyglet.window.key.I:
        vis=not(vis)  # visibility switch
        toggle(vis)
    else: pyglet.app.exit()

@canvas.event
def draw():
    canvas.clear()
    batch.draw()

def update(dt):  # updates an uniform circular motion then calls custom actions
    global alpha
    alpha+= dt * OMEGA % 360 # stay within [0,360°]
    updates(dt)
    draw()

def toggle(vis):
    pass

# }}} --------------------- END OF STANDARD ENGINE SECTION --------------------


#--------------------------------- SCENE SECTION ------------------------------


# sketches --------------------------------------------------------------------
still  = Sketch()  # 'default' still sketch
wheel  = Sketch(pos=(SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.66, 0))  # revolving

# geometry --------------------------------------------------------------------
# circle function
def circle(pos=(0,0), radius=100, color=(255,255,255,255), sk=still):
    '''
    Returns a Circle, outline only
    '''
    # number of divisions per ∏ rads (half the circle)
    stepangle = math.pi / (int(radius / 5) + 12)
    # with vertices numbered like a clock,  GL_TRIANGLE_STRIP order is:
    # 11, 12, 10, 1, 9, 2, 8, 3, 7, 4, 6, 5
    vtx = [0, radius]  # create list and first element
    phi = 0
    numvtx=2 # number of vtx that will be passed to batch.add
    while phi < 2.0 * math.pi:
        # end of previous segment
        vtx.append(radius * math.sin(phi))
        vtx.append(radius * math.cos(phi))
        numvtx += 1
        # same pt start of next segment if GL_LINES is used
        vtx.append(radius * math.sin(phi))
        vtx.append(radius * math.cos(phi))
        phi += stepangle
        numvtx += 1
    vtx.extend([0, radius])  # add right side vertex
    circle=batch.add(numvtx, GL_LINES, sk, 'v2f/static', 'c4B/static')
    #circle=batch.add(numvtx, GL_LINE_STRIP, sk, 'v2f/static', 'c4B/static')
    circle.colors = color*numvtx
    circle.vertices = translate(vtx, pos)
    return(circle) # is a vertex_list since batch.add() returns a vertex_list

# rectangle function
def rec(w=100, h=100, color=(255,255,255,255), pos=ORIGIN, sk=still):
    '''
    Returns a rectangle, filed
    '''
    rec=batch.add(6, pyglet.gl.GL_TRIANGLES, sk, 'v2f/static', 'c4B/static')
    rec.colors = color*6
    rec.vertices = translate((0,0,0,h,w,h,w,h,w,0,0,0), pos)
    print rec.vertices[0]
    return(rec) # batch.add() returns a vertex_list

# geometry sizes relative to screen
gu = int(SCREEN_HEIGHT/110)  # overall drawing V size is 85 gu and just fits into screen
hgt, wth, thk = 33 * gu, 11 * gu, 6 * gu  # proportions of the kapla block
rad1=0.5*math.hypot(thk,thk)
rad2=math.hypot(0.5*thk,0.5*thk+hgt)
alf= math.atan(thk*0.5/hgt)  # length set to 1 for faster calculations
# list of verts
#      *  *           d c            d c
#   *        *     '  | |  '      '       '
#  *          *   f---e b---a    f    ,__--a +alf
#  *          *   g---h k---l    g       --l -alf
#   *        *     ,  | |  ,      ,       ,
#      *  *           i j            i j
polar_coords=(alf, rad2, PI/2-alf, rad2, PI/2+alf, rad2, -alf+PI, rad2,
            alf+PI , rad2, -alf-PI/2, rad2, alf-PI/2, rad2, -alf, rad2)
# verts generator
def get_verts():
    for n in polar_coords: yield (n)
gv=get_verts()

# kapla_colors
redk =(255, 69,   0,   255)  # red kapla
bluk =(  0,  0, 140,   255)  # blue kapla
grnk =(  0, 99,   0,   255)  # green kapla
yelk =(255, 214,  0,   255)  # yellow kapla
white = (255, 255, 255, 255)

# four rects in a cross
r1 = rec(w=hgt, h=thk, color=redk, sk=wheel, pos=(thk/2, -thk/2))
r2 = rec(w=hgt, h=thk, color=bluk, sk=wheel, pos=(-hgt - thk/2, -thk/2))
r3 = rec(w=thk, h=hgt, color=grnk, sk=wheel, pos=(-thk/2, thk/2))
r4 = rec(w=thk, h=hgt, color=yelk, sk=wheel, pos=(-thk/2, -hgt - thk/2))
# circles
c=circle(radius=rad1, sk=wheel)
c=circle(radius=rad2, sk=wheel)
for a,l in zip(gv,gv):
    print a, l
    circle(sk=wheel, radius=10, pos=(l*math.cos(a),l*math.sin(a)))



# updates ---------------------------------------------------------------------
def updates(dt):
    # wheel is rotating
    wheel.pos = [wheel.pos[0],wheel.pos[1], alpha]
    gv=get_verts()
    for a in gv:
        print a

#---------------------------------- MAIN --------------------------------------


if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1.0/24)
    pyglet.app.run()

# vim: set foldmarker={{{,}}} foldlevel=0 foldmethod=marker :
