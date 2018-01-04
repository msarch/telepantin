#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


from shapes import line, circle, quad, moveto, PT0
from colors import Color, C0, Term
from math import hypot
from canvas import Pt, CANVAS_HEIGHT, CANVAS_WIDTH

'''
I. geometric data -------------------------------------------------------------

kaplas vertex names are letters
edges have numbers and colors

        f--4---e
        |      |
        5  gr. 3
        |      |
 h--6---g      d---2---c
 |                     |
 7  blue   .     red  1
 |                     |
 i--8---j      a---0---b
        |      |
        9  yl. 11
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

# colors
KAPRD  = Color(255,  69,   0, 255)  # red kapla
kg  = Color(  0,  99,   0, 255)  # green kapla
kb  = Color(  0,   0, 140, 255)  # blue kapla
ky  = Color(255, 214,   0, 255)  # yellow kapla
TRANS = Color(0,0,100,100)

# list of vtx counterclockwise
ALL_VERTS = (a,b,c,d,e,f,g,h,i,j,k,l)
ALL_COLORS = (KAPRD, kg, kb, ky)

def quads_from_points((a,b,c,d,e,f,g,h,i,j,k,l)):
    return ((a,b,c,d), (d,e,f,g), (g,h,i,j), (j,k,l,a))

ALL_QUADS= quads_from_points(ALL_VERTS)


'''
II. shapes init ---------------------------------------------------------------
'''
def init_constructions():
    # construction lines
    line(Pt(-CANVAS_WIDTH*0.16,CANVAS_HEIGHT/2),
         Pt(-CANVAS_WIDTH*0.16, -CANVAS_HEIGHT/2),
         color=C0)
    moveto(Pt(CANVAS_WIDTH*0.16,0))   # new current location
    circle(radout, color=C0)
    circle(radin, color=C0)

def init_kaplas():
    moveto(Pt(CANVAS_WIDTH*0.16,0))   # new current location
    kpl=[quad(a, b, c, d, color=TRANS) for q, clr in zip(ALL_QUADS,ALL_COLORS)]
    return(kpl)

def init_spines():
    moveto(Pt(CANVAS_WIDTH*0.16,0))   # new current location
    lns = [line(*spine_from_quad(q), color=clr)
            for q, clr in zip(ALL_QUADS,ALL_COLORS)]
    return(lns)

def init_side_quads():
    return([(PT0,PT0,PT0,PT0, C0)for i in range(4)])

'''
III. 2d visibility helper functions -------------------------------------------
'''
def spine_from_quad(q):
    return (min(q, key=lambda x: x[1]), max(q, key=lambda x: x[1]))

# WIP v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v
def project(spines, x=-CANVAS_WIDTH*0.32):
    # first : spines to list of points augmented with colors
    pts_n_color =[(coord,i) for i,point in enumerate(spines) for coord in point]
    return([(Pt(x,p.y),c)for p,c in pts_n_color])

def sort_vertical(pts):
    # sort augmented points along X first from closest (-) to furthest (+)
    pts = sorted(pts , key=lambda e: e[0].x)
    # sort again along Y  from upper (+) to lower (-)
    pts = sorted(pts , key=lambda e: e[0].y, reverse=True)
    return (pts)

def is_visible(points,lines):
    return(points)

# iter through pair of coordinates in a flat list of coords to make quads -----
def make_recs_from_points(pts):
    p = iter(pts)
    for i in xrange(len(pts)/2):
        p1 = p.next()
        p2 = p.next()
        a = Pt(p1[0][0]-300,p1[0][1]),
        b = Pt(p2[0][0],p1[0][1]),
        c = Pt(p1[0][0],p2[0][1]),
        d = Pt(p2[0][0]-300,p2[0][1])

    return (a,b,c,c,d,a),(ALL_COLORS[p1[1]])



# WIP ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^


#-------------------------- MAIN for SELF-TESTING -----------------------------
def _update(dt):
    redraw()

if __name__ == "__main__":

    from canvas import redraw, run
    from pyglet.clock import schedule_interval

    init_constructions()
    schedule_interval(_update,1.0/60)
    run()

