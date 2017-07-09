#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# http://www.github.com/msarch/slide

# debug flags
WINDOWED = False
WINDOWED = True
VERBOSE = False
VERBOSE = True
if VERBOSE : frame_number, duration = 0,0

# initial state
PAUSED = False
PAUSED = True


# {{{ -------------------- STANDARD ENGINE SECTION (rev 8) --------------------
import pyglet
from pyglet.gl import *
from collections import namedtuple
from itertools import cycle
from math import  atan, cos, hypot, pi, sin
from sys import stdout

Color = namedtuple('Color', 'r g b a')
Point = namedtuple('Point', 'x y')  # 2 coordinates
Pt = Point
Segment = namedtuple('Segment', 'n start end color')
St = Segment

ORIGIN = Point(0,0)
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

# {{{ -------------------- STANDARD SHAPES SECTION (rev 4) --------------------
# Geometry helpers functions --------------------------------------------------
# non-GL vertex rotation/translation of a list of points
def transform(pts, dx=0, dy=0, ro=0):
    cosro, sinro = cos(ro*TWOPI/360), sin(ro*TWOPI/360)  #in radians
    return([Pt(cosro*pt.x-sinro*pt.y+dx,
               sinro*pt.x+cosro*pt.y+dy) for pt in pts])

# flatten a list of list : OpenGL vertexes are flat lists of floats
def flatten(l):
    return([item for sublist in l for item in sublist])

# Circle, outline only --------------------------------------------------------
# Adding a shape to a sketch(i.e. group) with batch.add returns a vertex list,
# Color and vertex positions are later accessible with .colors and .vertices
# Removing a shapes is done with vertex_list.delete(...)
def circle(radius, color, sketch,dx=0, dy=0, ro=0):
    # number of divisions, or segments size decrease w. rad.
    stepangle = TWOPI / (int(radius / 5) + 8)
    points = [Pt(x=0, y=radius)]  # create list and first element
    phi = 0
    while phi < TWOPI:
        # with GL_LINES we have to repeat same pt twice :
        # end of previous segment + start of next segment
        points.append(Pt(radius * sin(phi), radius * cos(phi)))
        points.append(Pt(radius * sin(phi), radius * cos(phi)))
        phi += stepangle
    points.append(Pt(x=0, y=radius))  # add right side vertex

    if VERBOSE:
        print '+', len(points), 'points circle'
        print '    . center :', dx, dy
        print '    . radius :', radius
        print '    . color :  ', color
        print ''

        c=batch.add(len(points), GL_LINES, sketch, 'v2f/static', 'c4B/static')
    c.colors = color*(len(points))
    c.vertices = flatten(transform(points, dx, dy, ro))
    return(c) # c is a vertex_list since batch.add() returns a vertex_list

# Line ------------------------------------------------------------------------
def line(point1, point2, color, sketch, dx=0, dy=0, ro=0):
    l = batch.add(2, GL_LINES, sketch, 'v2f/static', 'c4B/static')
    l.colors= color*2
    points = (point1, point2)
    l.vertices = flatten(transform(points, dx, dy, ro))

    if VERBOSE:
        print '+ line :'
        print '    .', point1
        print '    .', point2
        print '    .', color
        print ''

    return(l)

# Quadri from 4 points, filed with triangles ----------------------------------
def quadri(a, b, c, d , color, sketch, dx=0, dy=0, ro=0):
    r = batch.add(6, pyglet.gl.GL_TRIANGLES, sketch, 'v2f/static', 'c4B/static')
    r.colors = color*6
    points = (a, b, c, c, d, a)
    r.vertices = flatten(transform(points, dx, dy, ro))

    if VERBOSE:
        print '+ quad '
        print '    .', a
        print '    .', b
        print '    .', c
        print '    .', d
        print '    .', color
        print ''

    return(r) # batch.add() returns a vertex_list

# Rectangle, from width and height filed with triangles -----------------------
def rec(w, h, color, sketch, dx=0, dy=0, ro=0):
    r = batch.add(6, pyglet.gl.GL_TRIANGLES, sketch, 'v2f/static', 'c4B/static')
    r.colors = color*6
    points = [Pt(p[0],p[1]) for p in ((0,0),(0,h),(w,h),(w,h),(w,0),(0,0))]
    r.vertices = flatten(transform(points, dx, dy, ro))
    if VERBOSE:
        print '    + defining rec :', points
    return(r) # batch.add() returns a vertex_list

# }}} --------------------- END OF STANDARD SHAPES SECTION --------------------

# {{{ ---------------------------- SCENE INIT ---------------------------------
# kapla colors ----------------------------------------------------------------
kr  = Color(255,  69,   0, 255)  # red kapla
kg  = Color(  0,  99,   0, 255)  # green kapla
kb  = Color(  0,   0, 140, 255)  # blue kapla
ky  = Color(255, 214,   0, 255)  # yellow kapla
'''
-------------------------------------------------------------------------------
geometric data

        f--4---e
        |      |
        5  g   3
        |      |
 h--6---g      d---2---c
 |                     |
 7   b      .     r    1
 |                     |
 i--8---j      a---0---b
        |      |
        9  y   11
        |      |
        k--10--l

-------------------------------------------------------------------------------
'''
gu  = int(SCREEN_HEIGHT/110)              # global unit to fit screen
kal, kaw, kae = 33 * gu, 11 * gu, 6 * gu  # proportions of KAPLA wood blocks
rd1 = hypot(0.5 * kae, 0.5 * kae + kal)   # outer radius of blocks (acdfgijl)
rd2 = 0.5 * hypot(kae,kae)                # inner radius (behk)
tk2 = kae * 0.5
span = tk2+kal

# points data
a, b, c, d = Pt(tk2, -tk2),   Pt(span,-tk2),  Pt(span, tk2),  Pt(tk2, tk2),
e, f, g, h = Pt(tk2, span),   Pt(-tk2, span), Pt(-tk2, tk2),  Pt(-span,tk2),
i, j, k, l = Pt(-span, -tk2), Pt(-tk2, -tk2), Pt(-tk2,-span), Pt(tk2, -span),

# list of pts counterclockwise from 'a' to 'l' and to 'a' again
scene_points = (a,b,c,d,e,f,g,h,i,j,k,l,a)

def get_edges(pts, colors):
    for i in xrange(len(pts)-1):
         yield (i, pts[i], pts[i+1], colors[i])

def get_quads(pts, colors):  # yields number, coords and color
    for i in range(0,len(pts)-1, 3):
        yield (((i+3)/4, pts[i], pts[i+1], pts[i+2], pts[i+3], colors[(i+3)/4]))

# edges
edges_colors = (kr, kr, kr, kg, kg, kg, kb, kb, kb, ky, ky, ky)
scene_edges = get_edges(scene_points, edges_colors)

# quads
quads_colors = (kr, kg, kb, ky)
scene_quads = get_quads(scene_points, quads_colors)


if VERBOSE:
    print '---------------------------------------------------------------'
    print '-'
    print '-                        scene init'
    print '-'
    print '---------------------------------------------------------------'

    print '+ scene_points :'
    for _ in scene_points : print '    .', _
    print ''
    print '+ edges_colors :'
    print ''
    for _ in edges_colors : print '    .', _
    print ''
    print '+ scene_edges  :'
    print''
    for e in scene_edges:
        for _ in e : print '    .', _
        print ''
    print '+ quads_colors :'
    print ''
    for _ in quads_colors : print '    .', _
    print ''
    print '+ scene_quads  :'
    print ''
    for q in scene_quads :
        for _ in q : print '    .', _
        print ''


'''
this list should be the result of visible vertexes @ different angle
        0       : (e,c,b,l)
    1 -->  45   : (e,c,b,a,l,k)
       45       : (c,b,a,l,k)
   46 -->  89   : (c,b,a,l,k,i)
       90       : (b,l,k,i))
   91 --> 134   : (b,l,k,j,i,h)
      135       : (l,k,j,i,h)
  136 --> 179   : (l,k,j,i,h,f)
      180       : (k,i,h,f)
  181 --> 234   : (k,i,h,g,f,e)
      225       : (i,h,g,f,e)
  226 --> 269   : (i,h,g,f,e,c)
      270       : (h,f,e,c)
  271 --> 314   : (h,f,e,d,c,b)
      315       : (f,e,d,c,b)
  316 --> 359   : (f,e,d,c,b,l)

'''

# sketches --------------------------------------------------------------------
wheel_center=Pt(SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.5)
wheel = Sketch(wheel_center)  # revolving sketch
still = Sketch(wheel_center)  # 'default' still sketch

# scene shapes ----------------------------------------------------------------
# half screen line
line(Pt(wheel_center.x,SCREEN_HEIGHT/2),
     Pt(wheel_center.x, -SCREEN_HEIGHT/2),
     color=CLINE, sketch=still)

# circles
circle(radius=rd2, color=CLINE, sketch=still)
circle(radius=rd1, color=CLINE, sketch=still)


# scene shapes ----------------------------------------------------------------

# four rects in a cross, rotation will be applied to every point @ every dt
kaplas=[quadri(a, b, c, d, color=clr, sketch=still)
        for num, a, b, c, d, clr in get_quads(scene_points, quads_colors)]

# optional labels
if VERBOSE:
    labels=[]
    for i,pt in enumerate(scene_points[0: -1]):
        labels.append(pyglet.text.Label(chr(97+i),
            group=still, batch=batch,
            font_name=['Courier'], font_size=10,color=(255, 255, 255, 255),
            anchor_x='center', anchor_y='center',
            x=pt.x, y=pt.y))

# }}} ---------------------------- END OF SCENE INIT --------------------------

# {{{ --------------------------- SCENE UPDATE SECTION ------------------------

def filter_edges(edges):
    '''
    returns edge shortlist of edges with normal pointing right
    (i.e. : eliminates those invisible from the right side)
    normal vector is : (end.y-start.y, -(end.x-start.x))
    we just check : normal.x > 0 which is equivalent to: end.y > start.y
    (equality would mean horizontal edge : discarded as not visible)
    '''
    return ([(n, end, start, clr) for n, start, end, clr in edges if end.y > start.y])

def verticalize_edges(edges):
    '''
    replace all edges with artificially verticalized lines @ centroid
    '''
    return ([(n, Point((end.x+start.x)/2, max(start.y,end.y)),
                 Point((end.x+start.x)/2, min(start.y,end.y)),clr)
                 for n,start,end,clr in edges])


def edges_x_sorting(edges):
    '''
    get
    '''
    pass

def scene_update(dt):

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

    # wheel sketch is always rotating
    wheel.ro = alpha

    # move all points
    # hard (non GL) transform all points to have access to coordinates
    live_points = transform(scene_points, dx=0, dy=0, ro=alpha)

    # update kaplas vertices from live points
    for i, a,b,c,d,clr in get_quads(live_points, quads_colors):
        kaplas[i].vertices = (a.x, a.y, b.x, b.y, c.x, c.y,
                              c.x, c.y, d.x, d.y, a.x, a.y)

        if VERBOSE:
            print '= updated quad', i, 'coords'
            print '    .', a
            print '    .', b
            print '    .', c
            print '    .', d
            print '    .', clr

    if VERBOSE:
        # update vertices labels x and y
        for i,pt in enumerate(live_points[0: -1]):
            labels[i].x=int(pt.x)  # int() is MANDATORY to avoid weird results
            labels[i].y=int(pt.y)
        print '= updated labels positions'

    # update current list of front facing edges
    facing_edges = filter_edges(get_edges(live_points, edges_colors))

    if VERBOSE:
        print '= well oriented edges:'
        for e in facing_edges:
           for _ in e : print '    .', _
           print ''

    # verticalize edges
    vertical_edges = verticalize_edges(facing_edges)
    if VERBOSE:
        print '= verticalized edges:'
        for e in vertical_edges:
            for _ in e : print '    .', _
            print ''

    # sort edges along y
    vertical_edges = sorted(vertical_edges , key=lambda e: e[1].y, reverse=True)
    if VERBOSE:
        print '= Y sorted edges:'
        for e in vertical_edges:
            for _ in e : print '    .', _
            print ''

    # cut hidden parts
    '''
    for e in edge
        check if e.top is hidden :
            for rm in rightmost edges:
                if e.top.y between o.top.y and o.bottom.y :
                        follow chain from o.bottom
                            if all remaining  all rm.top and bottom upper than e.top the replace e.top with last in chain
                            or until rm. lower than e.bottom then remove e
        check if bottom
    '''

# TODO: ordered display list : let openGL do the job



# }}} ----------------------- END OF SCENE UPDATE -----------------------------


#---------------------------------- MAIN --------------------------------------
if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1.0/120)
    pyglet.app.run()

# vim: set foldmarker={{{,}}} foldlevel=0 foldmethod=marker foldcolumn=5 :
