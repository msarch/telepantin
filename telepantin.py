#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# http://www.github.com/msarch/slide

WINDOWED = False
WINDOWED = True
VERBOSE = False
VERBOSE = True
PAUSED = False
PAUSED = True

# {{{ -------------------- STANDARD ENGINE SECTION (rev 7) --------------------
import pyglet
from pyglet.gl import *
from collections import namedtuple
from math import  atan, cos, hypot, pi, sin
from sys import stdout

Point = namedtuple('Point', 'x y')  # 2 coordinates
Pt = Point

ORIGIN = Point(0,0)
OO=ORIGIN
TWOPI = 2*pi
BLACK = (  0,   0,   0, 255)
WHITE = (255, 255, 255, 255)
CLINE = (125, 125, 100, 100)        # construction lines color
REV_PER_SEC = 0.1                   # angular velocity 0.5= 0.5rev/s
alpha = 0.0                         # flywheel initial angle


# Pyglet Window stuff ---------------------------------------------------------
batch = pyglet.graphics.Batch()  # holds all graphics
config = Config(sample_buffers=1, samples=4,depth_size=16, double_buffer=True, mouse_visible=False)
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
        print 'user quit'
        pyglet.app.exit()

def update(dt):  # updates an uniform circular motion then calls custom actions
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
    def __init__(self,pos=ORIGIN, ro=0):  # pos.x,pos.y=coords, ro=rotation angle
        super(Sketch, self).__init__()
        self.pos,self.ro = pos, ro

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
    return([Pt(cosro*pt.x-sinro*pt.y+dx, sinro*pt.x+cosro*pt.y+dy)for pt in pts])

# flatten a list of list : OpenGL vertexes are flat lists of floats
def flatten(l):
    return([item for sublist in l for item in sublist])

# Circle, outline only --------------------------------------------------------
# Adding a shape to a sketch(i.e. group) with batch.add returns a vertex list,
# Color and vertex positions are later accessible with .colors and .vertices
# Removing a shapes is done with vertex_list.delete(...)
def circle(radius, color, sketch,dx=0, dy=0, ro=0):
        # number of divisions per PI rads (half the circle)
    stepangle = TWOPI / (int(radius / 5) + 8)  # number of segments depends of size
    points = [Pt(x=0, y=radius)]  # create list and first element
    phi = 0
    while phi < TWOPI:
        # because GL_LINES is used, we have to repeat same pt twice :
        # end of previous segment + start of next segment
        points.append(Pt(radius * sin(phi), radius * cos(phi)))
        points.append(Pt(radius * sin(phi), radius * cos(phi)))
        phi += stepangle
    points.append(Pt(x=0, y=radius))  # add right side vertex
    if VERBOSE:
        print '    + defining circle : ', len(points), 'points...'
    c=batch.add(len(points), GL_LINES, sketch, 'v2f/static', 'c4B/static')
    c.colors = color*(len(points))
    c.vertices = flatten(transform(points, dx, dy, ro))
    return(c) # c is a vertex_list since batch.add() returns a vertex_list

# Line ------------------------------------------------------------------------
def line(point1, point2, color, sketch, dx=0, dy=0, ro=0):
    l = batch.add(2, GL_LINES, sketch, 'v2f/static', 'c4B/static')
    l.colors= color*2
    points = [point1, point2]
    l.vertices=flatten(transform(points, dx, dy, ro))
    if VERBOSE:
        print '    + defining line :', points
    return(l)

# Quadri from 4 points, filed with triangles ----------------------------------
def quadri(a, b, c, d , color, sketch, dx=0, dy=0, ro=0):
    r = batch.add(6, pyglet.gl.GL_TRIANGLES, sketch, 'v2f/static', 'c4B/static')
    r.colors = color*6
    points = (a, b, c, c, d, a)
    r.vertices = flatten(transform(points, dx, dy, ro))
    if VERBOSE:
        print '    + defining quad :', points
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

# {{{ ----------------------------- SCENE SECTION -----------------------------
# kapla colors ----------------------------------------------------------------
k_r  = (255,  69,   0, 255)  # red kapla
k_g  = (  0,  99,   0, 255)  # green kapla
k_b  = (  0,   0, 140, 255)  # blue kapla
k_y  = (255, 214,   0, 255)  # yellow kapla
'''
-------------------------------------------------------------------------------
geometric data

     f---e
     | g |
 h---g   d---c ... +alf
 | b   .   r | ... 0°
 i---j   a---b ... -alf
     | y |
     k---l
-------------------------------------------------------------------------------
'''
gu  = int(SCREEN_HEIGHT/110)              # global unit to fit screen
kal, kaw, kae = 33 * gu, 11 * gu, 6 * gu  # proportions of KAPLA wood blocks
rd1 = hypot(0.5 * kae, 0.5 * kae + kal)   # outer radius of blocks (acdfgijl)
rd2 = 0.5 * hypot(kae,kae)                # inner radius (behk)
alf  = atan(kae * 0.5 / kal)              # angle from center to a
tk2 = kae * 0.5
span = tk2+kal
# points
a, b, c, d = Pt(tk2, -tk2),   Pt(span,-tk2),  Pt(span, tk2),  Pt(tk2, tk2),
e, f, g, h = Pt(tk2, span),   Pt(-tk2, span), Pt(-tk2, tk2),  Pt(-span,tk2),
i, j, k, l = Pt(-span, -tk2), Pt(-tk2, -tk2), Pt(-tk2,-span), Pt(tk2, -span),
# list of pts counterclockwise from 'a' to 'l' and to 'a' again
base_pts = (a,b,c,d,e,f,g,h,i,j,k,l,a)

#edges generator
edge_color = [k_r, k_r, k_r, k_g, k_g, k_g, k_b, k_b, k_b, k_y, k_y, k_y]
def edges_gen(pts):
    for i in xrange(len(pts)-1):
        yield i, pts[i], pts[i+1], edge_color[i]

if VERBOSE:
    edg=edges_gen(base_pts)
    for e in edg:
        print '    + edge definition : ', e

# recs generator
rec_color = [k_r, k_g, k_b, k_y]
def quads_gen(pts):
    for i in range(0,len(pts)-1, 3):
        j=(i+3)/4
        yield j,  pts[i], pts[i+1], pts[i+2], pts[i+3], rec_color[j]

if VERBOSE:
    rcs=quads_gen(base_pts)
    for r in rcs:
        print '    + kapla definition : ', r
# shapes ----------------------------------------------------------------------
wheel_center=Pt(SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.5)
wheel = Sketch(wheel_center)  # revolving sketch
still = Sketch(wheel_center)  # 'default' still sketch

# half screen line
line(Pt(wheel_center.x,SCREEN_HEIGHT/2), Pt(wheel_center.x, -SCREEN_HEIGHT/2), color=CLINE, sketch=still)

# circles
circle(radius=rd2, color=CLINE, sketch=still)
circle(radius=rd1, color=CLINE, sketch=still)

# four rects in a cross, will rotate with wheel sketch
#r=rec(w=kal, h=kae, color=k_r, sketch=wheel, dx=kae/2, dy=-kae/2)]
#r=rec(w=kae, h=kal, color=k_g, sketch=wheel, dx=-kae/2, dy=kae/2)
#r=rec(w=kal, h=kae, color=k_b, sketch=wheel, dx=-kal-kae/2, dy=-kae/2)
#r=rec(w=kae, h=kal, color=k_y, sketch=wheel, dx=-kae/2, dy=-kal-kae/2)

# list of four rects in a cross, rotation will be computed
kaplas=[]
quads = quads_gen(base_pts)
for i, a, b, c, d, color in quads:
    kaplas.append(quadri(a, b, c, d, color=color, sketch=still))
    if VERBOSE:
        print i,a,b,c,d,color

if VERBOSE:
    labels=[]
    for i,pt in enumerate(base_pts):
        labels.append(pyglet.text.Label(str(i), group=still, batch=batch,
            font_name=['Courier'], font_size=10, anchor_x='center', anchor_y='center',
            color=(255, 255, 255, 255), width = 10, height = 10, x=pt.x, y=pt.y))

#generate  a list of horizontal rays from each vert to end_x
right_x = SCREEN_WIDTH/2
rays = []
edges = edges_gen(base_pts)
for i, start, end, color in edges:
    rays.append(line(start, Pt(right_x, start.y), color=color, sketch=still))
    rays.append(line(end, Pt(right_x, end.y), color=color, sketch=still))
    rays.append(line(Pt(right_x,start.y), Pt(right_x, end.y), color=color, sketch=still))

# TODO:  FIRST LINES DO  NOT ERASE THEMSELVES
print 'len rays', len(rays)

# scene update ----------------------------------------------------------------
def scene_update(dt):
    # wheel is rotating
    wheel.ro = alpha

    # we need to hard transform each scene point for later access to coordinates
    live_pts = transform(base_pts, dx=0, dy=0, ro=alpha)
    if VERBOSE:
        for i,pt in enumerate(live_pts):
            labels[i].x=pt.x
            labels[i].y=pt.y

    # update kaplas vertices from live points
    quads = quads_gen(live_pts)
    for i, a, b, c, d, color in quads:
        print i,a,b,c,d,color
        kaplas[i].vertices = (a.x, a.y, b.x, b.y, c.x, c.y, c.x, c.y, d.x, d.y, a.x, a.y)

    # update lines from live points only if edge normal points to the right
    global rays
    edges = edges_gen(live_pts)
    for i,start,end,color in edges:
        if VERBOSE:
            print ' = ray' , i
            print '    start', start
            print '    end', end
            print '    color', color
        rays[i].vertices = (start.x, start.y, right_x, start.y)
        rays[i].colors = color*2
        rays[i+1].vertices = (end.x, end.y, right_x, end.y)
        rays[i+1].colors = color*2
        rays[i+2].vertices = (right_x, start.y, right_x, end.y)
        rays[i+2].colors = color*2
    print len(rays)

#        normal = Point(-(end.y-start.y), end.x-start.x)
        #if normal.x > 0:
            #rays[i].vertices = (start.x, start.y, right_x, start.y)
            #rays[i+1].vertices = (end.x, end.y, right_x, end.y)
        #else:
            #rays[i].vertices = (0,0,0,0)
            #rays[i+1].vertices = (0,0,0,0)
    '''
    ---------------------------------------------------------------------------
    NORMAL VECTOR
    To get a normal between points p1 and p2 rotate the vector p1->p2 clockwise
    through 90 degrees. That is for a segment going from (x1,y1) to (x2,y2):

        n = (dy, -dx) with: dx=x2-x1 and dy=y2-y1,

    The opposite normal vector is: n’=(-dy, dx)
    ---------------------------------------------------------------------------
    '''
    stdout.write('.')

# }}} ------------------------ END OF SCENE SECTION ---------------------------


#---------------------------------- MAIN --------------------------------------
if __name__ == "__main__":
    print 'updating...'
    pyglet.clock.schedule_interval(update, 1.0/120)
    pyglet.app.run()

# vim: set foldmarker={{{,}}} foldlevel=0 foldmethod=marker foldcolumn=5 :


