#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


import pyglet
from pyglet.clock import schedule_interval
from shapes import *
from colors import *
from math import hypot
from canvas import Sketch, redraw, run, CANVAS_HEIGHT, CANVAS_PAUSED

alpha = 0.0                         # flywheel initial angle
REV_PER_SEC = 0.1                   # flywheel angular velocity 0.5= 0.5rev/s

'''
I. geometric data -------------------------------------------------------------
        f--4---e
        |      |
        5  g   3
        |      |
 h--6---g      d---2---c
 |                     |
 7   b      .     r    1
 |                     |
        |      |
 i--8---j      a---0---b
        9  y   11
        |      |
        k--10--l

'''
gu  = int(CANVAS_HEIGHT/110)                # global unit to fit screen
kal, kaw, kae = 33 * gu, 11 * gu, 6 * gu    # proportions of KAPLA wood blocks
radout = hypot(0.5 * kae, 0.5 * kae + kal)  # outer radius of blocks (acdfgijl)
radin = 0.5 * hypot(kae,kae)                # inner radius (behk)
tk2 = kae * 0.5
span = tk2+kal

# points
a, b, c = Pt( tk2, -tk2), Pt(span,-tk2),  Pt(span, tk2)
d, e, f = Pt( tk2,  tk2), Pt(tk2, span),  Pt(-tk2, span)
g, h, i = Pt(-tk2,  tk2), Pt(-span,tk2),  Pt(-span, -tk2)
j, k, l = Pt(-tk2, -tk2), Pt(-tk2,-span), Pt(tk2, -span)

# list of pts counterclockwise from 'a' to 'l' and to 'a' again
scene_points = (a,b,c,d,e,f,g,h,i,j,k,l,a)

# colors
kr  = Color(255,  69,   0, 255)  # red kapla
kg  = Color(  0,  99,   0, 255)  # green kapla
kb  = Color(  0,   0, 140, 255)  # blue kapla
ky  = Color(255, 214,   0, 255)  # yellow kapla
kaplas_colors = (kr, kg, kb, ky)    # quads colors
edges_colors = (kr, kr, kr, kg, kg, kg, kb, kb, kb, ky, ky, ky)


def get_edges(pts):
    for i in xrange(len(pts)-1):
        yield (pts[i], pts[i+1], edges_colors[i])

def get_quads(pts):
    # yields number, coords and color
    for i in range(0,len(pts)-1, 3):
        yield ((pts[i], pts[i+1], pts[i+2], pts[i+3], quads_colors[(i+3)/4]))

# edges
scene_edges = get_edges(scene_points)

# quads
scene_quads = get_quads(scene_points)


'''
II. sketches ------------------------------------------------------------------
'''


# -------------------------------- UPDATE SECTION -----------------------------
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
    print '= flipped edges:'
    for e in edges:
        for _ in e : print '    .', _
        print ''
    return (edges)

def sort_edges(edges):
    # first sort edges along X first, from rightmost (+) to leftmost (-)
    sorted_e = sorted(sorted_e , key=lambda e: e[1].x, reverse=True)
    print '= Y sorted edges:'
    for e in sorted_e:
        for _ in e : print '    .', _
        print ''
    # then sort edges along Y from highest (+) to lowest (-)
    # former X order will persist after this sorting
    sorted_e = sorted(edges , key=lambda e: e[1].y, reverse=True)
    print '= Y+X sorted edges:'
    for e in sorted_e:
        for _ in e : print '    .', _
        print ''
    return(sorted_e)


def update(dt):
    global alpha
    if CANVAS_PAUSED:pass
    else:
        # The 'Flywheel' has an uniform circular motion
        # all scene actions should update according to alpha
        alpha +=  dt * REV_PER_SEC * 360  # alpha is in degrees
        print alpha
        if alpha > 360 : alpha -= 360    # stay within [0,360°]
        # hard (non GL) move all points to have access to coordinates
        live_points = transform(scene_points, dx=0, dy=0, ro=alpha)
        # true rotation of recs : update recs vertices from live points
        for a,b,c,d,clr in get_quads(scene_points, edges_colors):
            kaplas[i].vertices = (a.x, a.y, b.x, b.y, c.x, c.y,
                                  c.x, c.y, d.x, d.y, a.x, a.y)


        # project edges section ---------------------------------------------------

        '''
        1- get shortlist of only front facing edges
        by filtering backward oriented normal edges
        '''
        # facing_edges = filter_edges(get_edges(live_points, edges_colors))

        '''
        2- flip edges
        if necessary flip end/start so highest point is first
        '''
        # oriented_edges = flip_edges(facing_edges)

        '''
        3- sort edges.starts :
            highest Y
            closest to the right CENTROID first if Y's are equal
        '''
        # sorted_edges = sort_edges(oriented_edges)

        '''
        4- scan edges startpoints
        for e in sorted_edges:
            if e.start is visible
                ppoints.append(e.start)
                pcolors.append(e.color)
                for f in sorted_edges with lower edge.start(*)
                    (*)we dont have to check edges with higher y because they
                    cant be in front unless they cross current edge

                    if f.start.y < e.end.y


        '''
    redraw()
    return()



