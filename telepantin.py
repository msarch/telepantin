#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# http://www.github.com/msarch/slide

# {{{ -------------------- STANDARD ENGINE SECTION (rev 2) --------------------
import math
import pyglet
from pyglet.gl import *

SCREEN_WIDTH, SCREEN_HEIGHT = 1280,800
TWOPI = 2*math.pi
OMEGA = 0.5 * 360.00                # angular velocity 0.5= 0.5rev/s
alpha = 0.0                         # flywheel initial angle
vis = 1                             # visibility switch
black = (  0,   0,   0, 255)
white = (255, 255, 255, 255)


# Pyglet Window stuff ---------------------------------------------------------
batch = pyglet.graphics.Batch()  # holds all graphics
config = Config(sample_buffers=1, samples=4,depth_size=16, double_buffer=True, mouse_visible=False)
window = pyglet.window.Window(fullscreen=True, config=config)

glClearColor(*black)  # background color
glEnable(GL_LINE_SMOOTH)
glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
glEnable(GL_BLEND)                                  # transparency
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)   # transparency
#glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)          # wireframe view mode

@window.event
def draw():
    window.clear()
    batch.draw()

def update(dt):  # updates an uniform circular motion then calls custom actions
    global alpha
    alpha += dt * OMEGA
    if alpha > 360 : alpha -= 360  # stay within [0,360°]
    updates(dt)
    draw()


# Sketch class ----------------------------------------------------------------
class Sketch(pyglet.graphics.Group): # subclass with position/rotation ability
    '''
    'sketches' are regular pyglet graphics.Groups whom 'set_state' and
    'unset_state' methods are used to add move and rotate functionnalities.
    Adding a shape to a group (batch.add) returns the matching vertex list,
    color and vertex position are accessible through .colors and .vertices
    '''
    def __init__(self,x,y,a):
        super(Sketch, self).__init__()
        self.x, self.y, self.a = x, y, a  # x,y coords, rotation angle

    def set_state(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.a, 0, 0, 1) # GL rot. in degrees; x,y,z of rot. axis

    def unset_state(self):
        glPopMatrix()


# Vertex transform functions --------------------------------------------------
def transform(vtx, dx=0, dy=0, a=0):  #'hard' vertex transformation (translation/rotation)
    cosa, sina = math.cos(TWOPI*a/360), math.sin(TWOPI*a/360)  #a given in deg
    it = iter(vtx)
    newverts = []
    for i in xrange(len(vtx)/2):
        x = it.next()
        y = it.next()
        newverts.append(cosa*x - sina*y + dx)
        newverts.append(sina*x + cosa*y + dy)
    return (newverts)


# }}} --------------------- END OF STANDARD ENGINE SECTION --------------------

# {{{ -------------------- STANDARD SHAPES SECTION (rev 1) --------------------
# Circle, outline only --------------------------------------------------------
def circle(radius, color, sketch, dx=0, dy=0, a=0):
        # number of divisions per ∏ rads (half the circle)
    stepangle = TWOPI / (int(radius / 5) + 8)
    vtx = [0, radius]  # create list and first element
    phi = 0
    while phi < TWOPI:
        # because GL_LINES is used, we have to repeat same pt twice :
        # end of previous segment + start of next segment
        vtx.extend([radius * math.sin(phi),radius * math.cos(phi),
                 radius * math.sin(phi),radius * math.cos(phi)])
        phi += stepangle
    vtx.extend([0, radius])  # add right side vertex
    c=batch.add(len(vtx)/2, GL_LINES, sketch, 'v2f/static', 'c4B/static')
    #circle=batch.add(numvtx, GL_LINE_STRIP, sk, 'v2f/static', 'c4B/static')
    c.colors = color*(len(vtx)/2)
    c.vertices = transform(vtx, dx=dx, dy=dy, a=a)
    return(c) # c is a vertex_list since batch.add() returns a vertex_list

# Line ------------------------------------------------------------------------
def line(x1, y1, x2, y2, color, pos, sketch, dx=0, dy=0, a=0):
    l = batch.add(2, GL_LINES, still, 'v2f/static', 'c4B/static')
    l.color = color*2
    l.vertices=transform((x1, y1, x2, y2), dx=dx, dy=dy, a=a)
    return(l)

# Rectangle, filed from triangles ---------------------------------------------
def rec(w, h, color, sketch, dx=0, dy=0, a=0):
    r = batch.add(6, pyglet.gl.GL_TRIANGLES, sketch, 'v2f/static', 'c4B/static')
    r.colors = color*6
    r.vertices = transform((0,0,0,h,w,h,w,h,w,0,0,0), dx=dx, dy=dy, a=a)
    return(r) # batch.add() returns a vertex_list

# }}} --------------------- END OF STANDARD SHAPES SECTION --------------------

# {{{ ----------------------------- SCENE SECTION -----------------------------

still = Sketch(SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.66, 0)  # 'default' still sketch
wheel = Sketch(SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.66, 0)  # revolving

# data and helper functions ---------------------------------------------------
#      d--c
#      |  |
#  f---e  b---a ... +alf
#  |    .     | ... 0°
#  g---h  k---l ... -alf
#      |  |
#      i--j
gu   = int(SCREEN_HEIGHT/110)  # overall drawing V size is 85*gu to fit screen
kal, kaw, kae = 33 * gu, 11 * gu, 6 * gu  # use proportions of real kapla block
rd1 = math.hypot(0.5 * kae, 0.5 * kae + kal)  # rad of outer verts (acdfgijl)
rd2 = 0.5 * math.hypot(kae,kae)  # rad for inner verts (behk)
alf  = math.atan(kae * 0.5 / kal)  # angle from center to a
tk2 = kae/2
span = tk2+kal
# kapla list of verts coords from a to l, by pairs: x1,y1,x2,y2, ...
all_verts = [span, tk2,   tk2, tk2,    tk2, span,    -tk2, span,
            -tk2, tk2,    -span,tk2,   -span, -tk2,  -tk2, -tk2,
            -tk2,-span,   tk2, -span,  tk2, -tk2,    span,-tk2]
all_edges = tuple((i,i+1) for i in range (11))

# kapla colors ----------------------------------------------------------------
k_r  = (255,  69,   0, 255)  # red kapla
k_g  = (  0,  99,   0, 255)  # green kapla
k_b  = (  0,   0, 140, 255)  # blue kapla
k_y  = (255, 214,   0, 255)  # yellow kapla


def filter_by_edge_normal(edges):  # filters wrong direction facing edges
    #returns list of edges
    pass

def get_visible(edges):  # gets who is projecting, until hidden by next
    #returns 1 axis coordinates list
    pass



# shapes ----------------------------------------------------------------------
# circles
c = circle(radius=rd2, color=white, sketch=still)
c = circle(radius=rd1, color=white, sketch=still)

# four rects in a cross
r1 = rec(w=kal, h=kae, color=k_r, sketch=wheel, dx=kae/2, dy=-kae/2)
r2 = rec(w=kal, h=kae, color=k_b, sketch=wheel, dx=-kal-kae/2, dy= -kae/2)
r3 = rec(w=kae, h=kal, color=k_g, sketch=wheel, dx=-kae/2, dy=kae/2)
r4 = rec(w=kae, h=kal, color=k_y, sketch=wheel, dx=-kae/2, dy=-kal-kae/2)

# generate a list of circles on ech vert, part of still sketch
c=[i for i in xrange(len(all_verts)/2)]
v = iter(all_verts)
for i in xrange(len(all_verts)/2):
    c[i]=circle(radius=10, color=white, sketch=still, dx=v.next(), dy=v.next())


# updates ---------------------------------------------------------------------
def updates(dt):
    # wheel is rotating
    wheel.a = alpha

    # only hard transform of each vert can give access to coordinates
    transform(all_verts, a=alpha)

    # redraw new circle on each vert
    v = iter(all_verts)
    for i in xrange(len(all_verts)/2):
        c[i].delete()
        c[i]=circle(radius=15, color=white, sketch=still, dx=v.next(),dy=v.next())

    filter_by_edge_normal(all_edges)
    get_visible(all_edges)

    # lines droping from points

# }}} --------------------- END OF STANDARD SHAPES SECTION --------------------


#---------------------------------- MAIN --------------------------------------
if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1.0/120)
    pyglet.app.run()

# vim: set foldmarker={{{,}}} foldlevel=0 foldmethod=marker :


