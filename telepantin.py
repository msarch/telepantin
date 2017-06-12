#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# http://www.github.com/msarch/slide

DEBUG = True
DEBUG = False

# {{{ -------------------- STANDARD ENGINE SECTION (rev 6) --------------------
import math
import pyglet
from pyglet.gl import *
from collections import namedtuple

Point = namedtuple('Point', 'x y')  #x and y should be floats
Segment = namedtuple('Segment', 'start end')  #start and end should be Points

ORIGIN = Point(0,0)
TWOPI = 2*math.pi
BLACK = (  0,   0,   0, 255)
WHITE = (255, 255, 255, 255)
CLINE = (125, 125, 100, 100)        # construction lines color
REV_PER_SEC = 0.2                   # angular velocity 0.5= 0.5rev/s
alpha = 0.0                         # flywheel initial angle


# Pyglet Window stuff ---------------------------------------------------------
batch = pyglet.graphics.Batch()  # holds all graphics
config = Config(sample_buffers=1, samples=4,depth_size=16, double_buffer=True, mouse_visible=False)
window = pyglet.window.Window(fullscreen=not(DEBUG), config=config)
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

def update(dt):  # updates an uniform circular motion then calls custom actions
    global alpha
    da = dt * REV_PER_SEC * 360  # alpha is in degrees
    alpha += da
    if alpha > 360 : alpha -= 360    # stay within [0,360°]
    updates(dt, da)
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

# }}} --------------------- END OF STANDARD ENGINE SECTION --------------------

# {{{ -------------------- STANDARD SHAPES SECTION (rev 4) --------------------
# Vertex transform function ---------------------------------------------------
'''
take a list of x,y coordinates as Points, returns a list of Points
applies 2D rotation+translation to each couple of coords
'''
def transform(points, dx=0, dy=0, ro=0):  #'hard' vertex transformation (translation/rotation)
    cosro = math.cos(ro*TWOPI/360)
    sinro = math.sin(ro*TWOPI/360)  #a in degrees
    newpoints=[]
    for v in points:
        newpoints.append(Point(cosro*v.x-sinro*v.y+dx ,sinro*v.x+cosro*v.y+dy))
    if DEBUG:
        print
        print '    moving points :', points
        print '    to new points :', newpoints
    return(newpoints)

# flatten a list of list, can't send tuples only floats as openGL vertexes-----
flatten = lambda l: [item for sublist in l for item in sublist]


# Circle, outline only --------------------------------------------------------
# Adding a shape to a sketch(i.e. group) with batch.add returns a vertex list,
# Color and vertex positions are later accessible with .colors and .vertices
# Removing a shapes is done with vertex_list.delete(...)
def circle(radius, color, sketch,dx=0, dy=0, ro=0):
        # number of divisions per PI rads (half the circle)
    stepangle = TWOPI / (int(radius / 5) + 8)  # number of segments depends of size
    points = [Point(x=0, y=radius)]  # create list and first element
    phi = 0
    while phi < TWOPI:
        # because GL_LINES is used, we have to repeat same pt twice :
        # end of previous segment + start of next segment
        points.append(Point(radius * math.sin(phi), radius * math.cos(phi)))
        points.append(Point(radius * math.sin(phi), radius * math.cos(phi)))
        phi += stepangle
    points.append(Point(x=0, y=radius))  # add right side vertex
    print
    print '    defining ', len(points), 'points circle :', points
    c=batch.add(len(points), GL_LINES, sketch, 'v2f/static', 'c4B/static')
    c.colors = color*(len(points))
    c.vertices = flatten(transform(points, dx, dy, ro))
    return(c) # c is a vertex_list since batch.add() returns a vertex_list

# Line ------------------------------------------------------------------------
def line(point1, point2, color, sketch, dx=0, dy=0, ro=0):
    l = batch.add(2, GL_LINES, sketch, 'v2f/static', 'c4B/static')
    l.colors= color*2
    points = [point1, point2]
    print
    print '    defining line :', points
    l.vertices=flatten(transform(points, dx,dy,ro))
    return(l)

# Rectangle, filed from triangles ---------------------------------------------
def rec(w, h, color, sketch, dx=0, dy=0, ro=0):
    r = batch.add(6, pyglet.gl.GL_TRIANGLES, sketch, 'v2f/static', 'c4B/static')
    r.colors = color*6
    points = [Point(p[0],p[1]) for p in ((0,0),(0,h),(w,h),(w,h),(w,0),(0,0))]
    print
    print '    defining rec :', points
    r.vertices = flatten(transform(points, dx, dy, ro))
    return(r) # batch.add() returns a vertex_list

# }}} --------------------- END OF STANDARD SHAPES SECTION --------------------

# {{{ ----------------------------- SCENE SECTION -----------------------------
# kapla colors ----------------------------------------------------------------
k_r  = (255,  69,   0, 255)  # red kapla
k_g  = (  0,  99,   0, 255)  # green kapla
k_b  = (  0,   0, 140, 255)  # blue kapla
k_y  = (255, 214,   0, 255)  # yellow kapla

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
vertices = [Point(span, tk2), Point(tk2, tk2), Point(tk2, span),
        Point(-tk2, span), Point(-tk2, tk2), Point(-span,tk2),
        Point(-span, -tk2), Point(-tk2, -tk2), Point(-tk2,-span),
        Point(tk2, -span), Point(tk2, -tk2), Point(span,-tk2)]
edges = [Segment(vertices[i], vertices[i+1]) for i in range(len(vertices)-1)]

# projection algorithm step 1 -------------------------------------------------
def filter_by_edge_normal(edges):  # filters wrong direction facing edges
    #returns list of edges
    selected=edges
    return(selected)

# projection algorithm step 2 -------------------------------------------------
def visible_segments(edges):  # gets who is projecting, until hidden by next
    #returns 1 axis coordinates list
    sections=[]
    return(sections)


# shapes ----------------------------------------------------------------------
wheel_center=Point(SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.5)
wheel = Sketch(wheel_center)  # revolving sketch
still = Sketch(wheel_center)  # 'default' still sketch

# circles
circle(radius=rd2, color=CLINE, sketch=still)
circle(radius=rd1, color=CLINE, sketch=still)

# four rects in a cross
rec(w=kal, h=kae, color=k_r, sketch=wheel, dx=kae/2, dy=-kae/2)
rec(w=kal, h=kae, color=k_b, sketch=wheel, dx=-kal-kae/2, dy=-kae/2)
rec(w=kae, h=kal, color=k_g, sketch=wheel, dx=-kae/2, dy=kae/2)
rec(w=kae, h=kal, color=k_y, sketch=wheel, dx=-kae/2, dy=-kal-kae/2)

# half screen line
line(Point(wheel_center.x,SCREEN_HEIGHT/2), Point(wheel_center.x, -SCREEN_HEIGHT/2), color=CLINE, sketch=still)

#generate  a list of horizontal rays from each vert to end_x
end_x = SCREEN_WIDTH/2
rays = [line(point, Point(end_x, point.y), color=CLINE, sketch=still)for point in vertices]


# updates ---------------------------------------------------------------------
def updates(dt, da):
    # wheel is rotating
    wheel.ro = alpha

    # we nedd to hard transform each vert for later access to coordinates
    global vertices
    vertices=transform(vertices, ro=da)

    # lines droping from points
    global rays
    for i, v in enumerate(vertices):
        rays[i].vertices = (v.x, v.y, end_x, v.y)

    #source_segments= visible_segments(filter_by_edge_normal(edges))
    #for edge in source_segments:
        #live_lines.append(line(vertices[edge[0]], vertices[edge[1]],
                               #-SCREEN_WIDTH, vertices[edge[1]],
                               #color=WHITE, sketch=still))


# }}} ------------------------ END OF SCENE SECTION ---------------------------


#---------------------------------- MAIN --------------------------------------
if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1.0/120)
    pyglet.app.run()

# vim: set foldmarker={{{,}}} foldlevel=0 foldmethod=marker :


