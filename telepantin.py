#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# http://www.github.com/msarch/slide

DEBUG = True

# {{{ -------------------- STANDARD ENGINE SECTION (rev 5) --------------------
import math
import pyglet
from pyglet.gl import *
from collections import namedtuple

Point = namedtuple('Point', 'x y')
ORIGIN = Point(0,0)
TWOPI = 2*math.pi
OMEGA = 0.5 * 360.00                # angular velocity 0.5= 0.5rev/s
alpha = 0.0                         # flywheel initial angle
vis = 1                             # visibility switch
black = (  0,   0,   0, 255)
white = (255, 255, 255, 255)

# Pyglet Window stuff ---------------------------------------------------------
batch = pyglet.graphics.Batch()  # holds all graphics
config = Config(sample_buffers=1, samples=4,depth_size=16, double_buffer=True, mouse_visible=False)
window = pyglet.window.Window(fullscreen=not(DEBUG), config=config)
SCREEN_WIDTH, SCREEN_HEIGHT = window.width, window.height

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
    '''
    def __init__(self,pos=ORIGIN, ro=0):  # pos.x,pos.y=coords, pos.a=rotation angle
        super(Sketch, self).__init__()
        self.pos,self.ro = pos, ro

    def set_state(self):
        glPushMatrix()
        glTranslatef(self.pos.x, self.pos.y, 0)
        glRotatef(self.ro, 0, 0, 1) # GL rot. in degrees; x,y,z of rot. axis

    def unset_state(self):
        glPopMatrix()


# Vertex afine transform function ---------------------------------------------
'''
take a list of x,y coordinates as Points OR tuples,
applies 2D rotation+translation to each couple of coords
returns a list of Points
'''
def transform(vtx, dx=0, dy=0, ro=0):  #'hard' vertex transformation (translation/rotation)
    cosro, sinro = math.cos(TWOPI*ro/360), math.sin(TWOPI*ro/360)  #a in degrees
    return([Point(cosro*v[0]-sinro*v[1]+dx,sinro*v[0]+cosro*v[1]+dy) for v in vtx])

flatten = lambda l: [item for sublist in l for item in sublist]

# }}} --------------------- END OF STANDARD ENGINE SECTION --------------------



# {{{ -------------------- STANDARD SHAPES SECTION (rev 3) --------------------
# Adding a shape to a sketch(i.e. group) with batch.add returns a vertex list,
# Color and vertex positions are later accessible with .colors and .vertices
# Removing a shapes is done with vertex_list.delete(...)
# Circle, outline only --------------------------------------------------------
def circle(radius, color, sketch,dx=0, dy=0, ro=0):
        # number of divisions per PI rads (half the circle)
    stepangle = TWOPI / (int(radius / 5) + 8)  # number of segments depends of size
    vtx = [Point(0, radius)]  # create list and first element
    phi = 0
    while phi < TWOPI:
        # because GL_LINES is used, we have to repeat same pt twice :
        # end of previous segment + start of next segment
        vtx.append(Point(radius * math.sin(phi),radius * math.cos(phi)))
        vtx.append(Point(radius * math.sin(phi),radius * math.cos(phi)))
        phi += stepangle
    vtx.append(Point(0, radius))  # add right side vertex
    c=batch.add(len(vtx), GL_LINES, sketch, 'v2f/static', 'c4B/static')
    c.colors = color*(len(vtx))
    c.vertices = flatten(transform(vtx, dx, dy, ro))
    return(c) # c is a vertex_list since batch.add() returns a vertex_list

# Line ------------------------------------------------------------------------
def line(pt1, pt2, color, sketch, dx=0, dy=0, ro=0):
    l = batch.add(2, GL_LINES, sketch, 'v2f/static', 'c4B/static')
    l.colors= color*2
    l.vertices=flatten(transform((pt1, pt2, dx,dy,ro)))
    return(l)

# Rectangle, filed from triangles ---------------------------------------------
def rec(w, h, color, sketch, dx=0, dy=0, ro=0):
    r = batch.add(6, pyglet.gl.GL_TRIANGLES, sketch, 'v2f/static', 'c4B/static')
    r.colors = color*6
    r.vertices = flatten(transform(((0,0),(0,h),(w,h),(w,h),(w,0),(0,0)), dx, dy, ro))
    return(r) # batch.add() returns a vertex_list

# }}} --------------------- END OF STANDARD SHAPES SECTION --------------------



# {{{ ----------------------------- SCENE SECTION -----------------------------
wheel_center=Point(SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.66)
wheel = Sketch(wheel_center)  # revolving sketch
still = Sketch(wheel_center)  # 'default' still sketch

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
tk2 = gu*kae/2
span = gu*tk2+kal

# kapla list of verts coords from a to l, by pairs: x1,y1,x2,y2, ...
all_verts = [(span, tk2),(tk2, tk2),(tk2, span),(-tk2, span),
            (-tk2, tk2),(-span,tk2),(-span, -tk2),(-tk2, -tk2),
            (-tk2,-span), (tk2, -span), (tk2, -tk2), (span,-tk2)]
all_edges = tuple((i,i+1) for i in range (11))


# kapla colors ----------------------------------------------------------------
k_r  = (255,  69,   0, 255)  # red kapla
k_g  = (  0,  99,   0, 255)  # green kapla
k_b  = (  0,   0, 140, 255)  # blue kapla
k_y  = (255, 214,   0, 255)  # yellow kapla


def filter_by_edge_normal(edges):  # filters wrong direction facing edges
    #returns list of edges
    less=edges
    return(less)

def visible_segments(edges):  # gets who is projecting, until hidden by next
    #returns 1 axis coordinates list
    cut=edges
    return(cut)


# shapes ----------------------------------------------------------------------
# circles
circle(radius=rd2, color=white, sketch=still)
circle(radius=rd1, color=white, sketch=still)

# four rects in a cross
rec(w=kal, h=kae, color=k_r, sketch=wheel, dx=kae/2, dy=-kae/2)
rec(w=kal, h=kae, color=k_b, sketch=wheel, dx=-kal-kae/2, dy=-kae/2)
rec(w=kae, h=kal, color=k_g, sketch=wheel, dx=-kae/2, dy=kae/2)
rec(w=kae, h=kal, color=k_y, sketch=wheel, dx=-kae/2, dy=-kal-kae/2)

#generate empty list of rays on each vert
#rays=[None for i in xrange(len(all_verts)/2)]  empty list of rays
#for edge in all_edges:
    #ray[i]=line(all_verts[edge[0]],
                #all_verts[edge[1]],
                #-SCREEN_WIDTH,
                #all_verts[edge[1]],
                #color=white, sketch=still)



# updates ---------------------------------------------------------------------
def updates(dt):
    # wheel is rotating
    wheel.ro = alpha

    # only hard transform of each vert can give access to coordinates
    global all_verts
    all_verts=transform(all_verts, ro=alpha)

    source_segments= visible_segments(filter_by_edge_normal(all_edges))
    # lines droping from points
    #live_lines=[]  #list of dynamically displayed elts recreated

    #for edge in source_segments:
        #live_lines.append(line(all_verts[edge[0]], all_verts[edge[1]],
                               #-SCREEN_WIDTH, all_verts[edge[1]],
                               #color=white, sketch=still))


# }}} --------------------- END OF STANDARD SHAPES SECTION --------------------


#---------------------------------- MAIN --------------------------------------
if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1.0/120)
    pyglet.app.run()

# vim: set foldmarker={{{,}}} foldlevel=0 foldmethod=marker :


