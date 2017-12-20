#/usr/bin/python
# -*- coding: iso-8859-1 -*-


# ------------------------- STANDARD SHAPES (rev 5) ---------------------------
'''
Calling a shape function will add a new shape
    to the current Sketch (pyglet graphics group) : _drawto
    at the current location                       : _moveto
    at the current angle                          : _headto
    with the current color                        : ccolor
This will return the vertex list object returned by pyglet's 'batch.add()'

Create a shape:
---------------
set current layer, pos and angle
    _drawto = BACKGROUND  # define current Sketch new shape will be added to
    _moveto = ORIGIN      # define current location
    _headto = 0           # define current angle in degrees

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

from math import pi, cos, sin
from pyglet.gl import GL_LINES, GL_TRIANGLES
from colors import CLINE
from canvas import  Point, Pt, BACKGROUND, BATCH


TWOPI = 2*pi
ORIGIN = Point(0,0)

_drawto = BACKGROUND              # default Sketch new shapes will be added to
_moveto = ORIGIN                  # default location
_headto = 0                       # default angle in degrees


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

def moveto(point):
    global _moveto
    _moveto = point
    print '+ moveto :', point

def update_vertices(sh,vtx):
    sh.vertices=flatten(vtx)





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
    c = BATCH.add(len(points), GL_LINES, _drawto, 'v2f/static', 'c4B/static')
    c.colors = color*(len(points))
    c.vertices = flatten(transform(points, _moveto.x, _moveto.y, _headto))
    print '+ circle :', len(points), ' points; x,y =', _moveto.x, _moveto.y, '; rad =', radius
    return(c) # c is a vertex_list since batch.add() returns a vertex_list


# Line ------------------------------------------------------------------------
def line(point1, point2, color):
    '''
    line from 2 points
    '''
    l = BATCH.add(2, GL_LINES, _drawto, 'v2f/static', 'c4B/static')
    l.colors= color*2
    points = (point1, point2)
    l.vertices = flatten(transform(points, _moveto.x, _moveto.y, _headto))
    print '+ line : from', point1, 'to', point2
    return(l)


# Quadrangle ------------------------------------------------------------------
def quad(a, b, c, d, color):
    '''
    quadrangle shape from 4 points,
    filled with 2 triangles
    '''
    q = BATCH.add(6, GL_TRIANGLES, _drawto, 'v2f/static', 'c4B/static')
    q.colors = color*6
    points = (a, b, c, c, d, a)  # @actually filled with 2 triangles
    q.vertices = flatten(transform(points, _moveto.x, _moveto.y, _headto))
    print '+ quad :', a, b ,c ,d
    return(q) # returns the vertex_list

def quad_vertices_renew(quad, vtx):
    '''
    updates kaplas vertices from 4 points
    '''
    quad.vertices = (
            vtx[0].x, vtx[0].y,
            vtx[1].x, vtx[1].y,
            vtx[2].x, vtx[2].y,
            vtx[2].x, vtx[2].y,
            vtx[3].x, vtx[3].y,
            vtx[0].x, vtx[0].y)

# Rectangle -------------------------------------------------------------------
def rec(w, h, color):
    '''
    from width and height
    origin at lower left corner
    '''
    r = BATCH.add(6, GL_TRIANGLES, _drawto, 'v2f/static', 'c4B/static')
    r.colors = color*6
    # filled with triangles
    points = [Pt(p[0],p[1]) for p in ((0,0),(0,h),(w,h),(w,h),(w,0),(0,0))]
    r.vertices = flatten(transform(points, _moveto.x, _moveto.y, _headto))
    print '+ rec :', points, '; x,y =', _moveto.x, _moveto.y
    return(r) # batch.add() returns a vertex_list

print '+ shapes.py loaded'


#-------------------------- MAIN for SELF-TESTING -----------------------------
def update(dt):
    redraw()

if __name__ == "__main__":

    from canvas import CANVAS_CENTER, redraw, run
    from pyglet.clock import schedule_interval

    circle(radius=100, color=CLINE)
    line(Pt(-CANVAS_CENTER.x, 100), Pt(CANVAS_CENTER.x, 100), color=CLINE)
    rec(w=10, h=400, color=CLINE)
    quad(Pt(-100,100), Pt(100,100),Pt(100,-100), Pt(-100,-100), color=CLINE)

    schedule_interval(update,1.0/60)
    run()

