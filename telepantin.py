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


# {{{ -------------------- STANDARD ENGINE SECTION (rev 9) --------------------
import pyglet
from pyglet.gl import *
from collections import namedtuple
from itertools import cycle
from math import  atan, cos, hypot, pi, sin
from sys import stdout

Color = namedtuple('Color', 'r g b a') # RGB+ alpha (0 to 255)
Point = namedtuple('Point', 'id x y')  # name + 2 coordinates
Pt = Point
Edge = namedtuple('Edge', 'id start end color')

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

# {{{ -------------------- STANDARD SHAPES SECTION (rev 5) --------------------
# Geometry helpers functions --------------------------------------------------
# non-GL vertex rotation/translation of a list of points
def transform(pts, dx=0, dy=0, ro=0):
    cosro, sinro = cos(ro*TWOPI/360), sin(ro*TWOPI/360)  #in radians
    return([Pt(pt.id,
               cosro*pt.x-sinro*pt.y+dx,
               sinro*pt.x+cosro*pt.y+dy)
               for pt in pts])

def bare(point):  # strips 'id' and returns tuple with x,y coordinates only
    return ((point[1],point[2]))

# flatten a list of list : OpenGL vertexes are flat lists of floats
def flatten(l):
    return([coord for point in l for coord in bare(point)])

# Circle, outline only --------------------------------------------------------
# Adding a shape to a sketch(i.e. group) with batch.add returns a vertex list,
# Color and vertex positions are later accessible with .colors and .vertices
# Removing a shapes is done with vertex_list.delete(...)
def circle(radius, color, sketch,dx=0, dy=0, ro=0):
    # number of divisions, or segments size decrease w. rad.
    stepangle = TWOPI / (int(radius / 5) + 8)
    points = [Pt('_', x=0, y=radius)]  # create list and first element
    phi = 0
    while phi < TWOPI:
        # with GL_LINES we have to repeat same pt twice :
        # end of previous segment + start of next segment
        points.append(Pt('_',radius * sin(phi), radius * cos(phi)))
        points.append(Pt('_',radius * sin(phi), radius * cos(phi)))
        phi += stepangle
    points.append(Pt('_',x=0, y=radius))  # add right side vertex

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

# quadrangle from 4 points, filed with triangles ----------------------------------
def quadrangle(a, b, c, d , color, sketch, dx=0, dy=0, ro=0):
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
a, b, c = Pt('a',tk2, -tk2),  Pt('b',span,-tk2),  Pt('c',span, tk2)
d, e, f = Pt('d',tk2, tk2),   Pt('e',tk2, span),  Pt('f',-tk2, span)
g, h, i = Pt('g',-tk2, tk2),  Pt('h',-span,tk2),  Pt('i',-span, -tk2)
j, k, l = Pt('j',-tk2, -tk2), Pt('k',-tk2,-span), Pt('l',tk2, -span)

# list of pts counterclockwise from 'a' to 'l' and to 'a' again
scene_points = (a,b,c,d,e,f,g,h,i,j,k,l,a)

def get_edges(pts, colors):
    for i in xrange(len(pts)-1):
        yield (pts[i].id+pts[i+1].id, pts[i], pts[i+1], colors[i])

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
wheel_center=Pt('C',SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.5)
wheel = Sketch(wheel_center)  # revolving sketch
still = Sketch(wheel_center)  # 'default' still sketch

# scene shapes ----------------------------------------------------------------
# half screen line
line(Pt('_',wheel_center.x,SCREEN_HEIGHT/2),
     Pt('_',wheel_center.x, -SCREEN_HEIGHT/2),
     color=CLINE, sketch=still)

# circles
circle(radius=rd2, color=CLINE, sketch=still)
circle(radius=rd1, color=CLINE, sketch=still)


# scene shapes ----------------------------------------------------------------

# four rects in a cross, rotation will be applied to every point @ every dt
kaplas=[quadrangle(a, b, c, d, color=clr, sketch=still)
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

# {{{ ------------------------ SCENE HELPERS FUNC -----------------------------

    def update_quads(quads, points, colors):
        '''
        updates kaplas vertices from points and colors list
        '''
        for i, a,b,c,d,clr in get_quads(points, colors):
            quads[i].vertices = (a.x, a.y, b.x, b.y, c.x, c.y,
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
            for i,pt in enumerate(points[0: -1]):
                labels[i].x=int(pt.x)  # int() is MANDATORY to avoid weird results
                labels[i].y=int(pt.y)
            print '= updated labels positions'


def filter_edges(edges):
    '''
    returns edge shortlist of edges with normal pointing right
    (i.e. : eliminates those invisible from the right side)
    normal vector is : (end.y-start.y, -(end.x-start.x))
    we just check : normal.x > 0 which is equivalent to: end.y > start.y
    (equality would mean horizontal edge : discarded as not visible)
    '''

    facing_edges = [Edge(id, end, start, clr)
        for id, start, end, clr in edges
        if end.y > start.y]

    if VERBOSE:
        print '= selecting only projection facing edges:'
        for e in facing_edges:
           for _ in e : print '    .', _
           print ''


    return (facing_edges)


def flip_edges(edges):
    '''
    all edges should start from highest point, end at lowest
    '''

    for e in edges:
        if e.start.y < e.end.y: e=(edge.id,edge.end,edge.start,edge.color)
        else: pass


    if VERBOSE:
        print '= flipped edges:'
        for e in edges:
            for _ in e : print '    .', _
            print ''


    return (edges)


def sort_edges(edges):
    # sort edges along Y
    sorted_e = sorted(edges , key=lambda e: e[1].y, reverse=True)


    if VERBOSE:
        print '= Y sorted edges:'
        for e in sorted_e:
            for _ in e : print '    .', _
            print ''


    # sort edges along X
    sorted_e = sorted(sorted_e , key=lambda e: e[1].x, reverse=True)


    if VERBOSE:
        print '= Y+X sorted edges:'
        for e in sorted_e:
            for _ in e : print '    .', _
            print ''


    return(sorted_e)



# }}} --------------------- END OF SCENE HELPERS FUNCTIONS --------------------

# {{{ ---------------------- SCENE UPDATE SECTION -----------------------------

def scene_update(dt):
    # wheel sketch is always rotating
    wheel.ro = alpha

    # hard (non GL) move all points to have access to coordinates
    live_points = transform(scene_points, dx=0, dy=0, ro=alpha)

    # true rotation of recs : update recs vertices from live points
    update_quads(kaplas, live_points, quads_colors)

    # --- edges projection to the right ---
    # 1- shortlist of only front facing edges
    facing_edges = filter_edges(get_edges(live_points, edges_colors))

    # 2- flip edges, if necessary flip end/start so start is highest point
    oriented_edges = flip_edges(facing_edges)

    # 3- sort edges.starts along Y and X, highest first then closest first
    sorted_edges = sort_edges(oriented_edges)

    # cut and stitch hidden parts
    '''
    Hidden-line algorithms until 1980's divide edges into line segments by
    the intersection points of their images, and then test each segment
    for visibility against each face of the model.
    Our algorithm is:

    for each edge (i)
       for each other edge (j)

       +────-──+─────────────────────────────────────-───────────+
       │edge i |                   edge j                        │
       +.......+.........+.......+.......+.......+.......+.......+
       │       │  case1  │ case2 │ case3 │ case4 │ case5 │ case 6│
       +.......+.........+.......+.......+.......+.......+.......+
       │       │  start  │ start │ start │       │       │       │
       │       │   end   │       │       │       │       │       │
       │ start +---------+-------+-------+-------+-------+-------+
       │       │    *    │  end  │   X   │ start │   *   │   *   │
       │       │    *    │   *   │   X   │  end  │ start │   *   │
       │  end  +---------+-------+-------+-------+-------+-------+
       │       │         │       │  end  │       │  end  │ start │
       │       │         │       │       │       │       │  end  │
       +──────-+─────────+───────+───────+───────+─────-─+───────+

        rules to cut edge i :
            case1: edge i unchanged
            case2: edge i.start = j.end
            case3: delete edge i from list
            case4: delete edge i from list;
                   add (i.start,j.start);
                   add (j.end,i.end)
            case5: edge i.end = j.start
            case6: edge i unchanged

       question : is there a benefit in ordering edge centers on X axis?


    -     '''

    def check_hidden(point, edges):
        # if point is not hidden, check_hidden returns 0
        # if point is hidden, check_hidden returns index of hiding edge
        pass

    # final list init
    xalign = SCREEN_WIDTH*0.75
    i, ppoints, pcolors =0, [],[]
    while i < len(sorted_edges):
        # check start
        hid = check_hidden(sorted_edges[i].start,sorted_edges[i:])
        if hid:  # add hiding edge to our list
            ppoints.append(sorted_edges[hid].start)
            pcolors.append(sorted_edges[hid].color)
            i = hid
        else : # hid = 0, add current point is visible, add it to our list
            ppoints.append(sorted_edges[i].start)
            pcolors.append(sorted_edges[i].color)
            i += 1


# }}} ----------------------- END OF SCENE UPDATE -----------------------------


#---------------------------------- MAIN --------------------------------------
if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1.0/120)
    pyglet.app.run()

# vim: set foldmarker={{{,}}} foldmethod=marker foldcolumn=5 :
