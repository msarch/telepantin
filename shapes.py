#/usr/bin/python
# -*- coding: iso-8859-1 -*-


# ------------------------- STANDARD SHAPES (rev 5) ---------------------------
'''
Calling a shape function will add a new shape
    to the current Sketch (pyglet graphics group) : drawto
    at the current location                       : moveto
    at the current angle                          : headto
    with the current color                        : ccolor
This will return the vertex list object returned by pyglet's 'batch.add()'

Create a shape:
---------------
set current layer, pos and angle
    drawto = BACKGROUND  # define current Sketch new shape will be added to
    moveto = ORIGIN      # define current location
    headto = 0           # define current angle in degrees

call shape function : shape(geometry, color)
example :

    c = circle(radius=100, color=CLINE)

or, if no later reference to the shape is needed, just call the function:

    circle(radius=100, color=CLINE)

Remove a shape
--------------
call 'vertex_list.delete' if the shape object has been referenced :

    c.delete


Changing a shape's color, replacing vertices
--------------------------------------------
Color and vertex positions are later accessible with object.colors and
object.vertices.

'''

from math import  cos, pi, sin
from collections import namedtuple
import pyglet
from pyglet.gl import *
from canvas import BACKGROUND, ORIGIN, CANVAS_CENTER, BATCH, Pt, run
from colors import *

Edge = namedtuple('Edge', 'id start end color') # name + 2 pts + color
TWOPI = 2*pi

drawto = BACKGROUND  # current Sketch new shapes will be added to
moveto = ORIGIN      # current location
headto = 0           # current angle in degrees

# Geometry helpers functions --------------------------------------------------
def transform(pts, dx=0, dy=0, ro=0):
    '''
    translate + rotate a list of points
    result of rotation/translation is computed (non-GL)
    return new list of points
    '''
    cosro, sinro = cos(ro*TWOPI/360), sin(ro*TWOPI/360) #cos() uses radians
    return([Pt(cosro*pt.x-sinro*pt.y+dx,
               sinro*pt.x+cosro*pt.y+dy)
               for pt in pts])

def flatten(points):
    '''
    flatten a list of floats
    returns a continuous list of x(n), y(n) coordinates
    directly usable as openGL vertex list ie: 'v2f/static'
    '''
    return([coord for point in points for coord in point])

def midpoint(pt1,pt2):
    # get centroid of 2 points
    return(Pt((pt1.x+pt2.x)*0.5,(pt1.y+pt2.y)*0.5))




# Circle ----------------------------------------------------------------------
def circle(radius, color):
    '''
    Circle, from center
    outline only
    '''
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
    c = BATCH.add(len(points), GL_LINES, drawto, 'v2f/static', 'c4B/static')
    c.colors = color*(len(points))
    c.vertices = flatten(transform(points, moveto.x, moveto.y, headto))
    print '+ circle :', len(points), ' points; x,y =', moveto.x, moveto.y, '; rad =', radius
    return(c) # c is a vertex_list since batch.add() returns a vertex_list

# Line ------------------------------------------------------------------------
def line(point1, point2, color):
    '''
    line from 2 points
    '''
    l = BATCH.add(2, GL_LINES, drawto, 'v2f/static', 'c4B/static')
    l.colors= color*2
    points = (point1, point2)
    l.vertices = flatten(transform(points, moveto.x, moveto.y, headto))
    print '+ line : from', point1, 'to', point2
    return(l)

# Quadrangle ------------------------------------------------------------------
def quad(a, b, c, d, color):
    '''
    quadrangle shape from 4 points,
    filled with 2 triangles
    '''
    q = BATCH.add(6, pyglet.gl.GL_TRIANGLES, drawto, 'v2f/static', 'c4B/static')
    q.colors = color*6
    points = (a, b, c, c, d, a)  # @actually filled with 2 triangles
    q.vertices = flatten(transform(points, moveto.x, moveto.y, headto))
    print '+ quad :', a, b ,c ,d
    return(q) # returns the vertex_list

# Rectangle -------------------------------------------------------------------
def rec(w, h, color):
    '''
    from width and height
    origin at lower left corner
    '''
    r = BATCH.add(6, pyglet.gl.GL_TRIANGLES, drawto, 'v2f/static', 'c4B/static')
    r.colors = color*6
    # filled with triangles
    points = [Pt(p[0],p[1]) for p in ((0,0),(0,h),(w,h),(w,h),(w,0),(0,0))]
    r.vertices = flatten(transform(points, moveto.x, moveto.y, headto))
    print '+ rec :', points, '; x,y =', moveto.x, moveto.y
    return(r) # batch.add() returns a vertex_list

# Test ------------------------------------------------------------------------
def test():

    # half screen line
    # circles
    circle(radius=100, color=CLINE)
    line(Pt(-CANVAS_CENTER.x, 100), Pt(CANVAS_CENTER.x, 100), color=CLINE)
    rec(w=10, h=400, color=CLINE)
    quad(Pt(-100,100), Pt(100,100),Pt(100,-100), Pt(-100,-100), color=CLINE)


print '+ shapes.py loaded'
#---------------------------------- MAIN --------------------------------------
if __name__ == "__main__":
    test()
    run()

