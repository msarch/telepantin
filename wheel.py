#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


from shapes import line, circle, quad, moveto
from colors import Color, C0
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
# TODO
# points
a, b, c = Pt( tk2, -tk2), Pt(span,-tk2),  Pt(span, tk2)
d, e, f = Pt( tk2,  tk2), Pt(tk2, span),  Pt(-tk2, span)
g, h, i = Pt(-tk2,  tk2), Pt(-span,tk2),  Pt(-span, -tk2)
j, k, l = Pt(-tk2, -tk2), Pt(-tk2,-span), Pt(tk2, -span)

# colors
RED  = Color(255,  69,   0, 255)  # red kapla
GRN  = Color(  0,  99,   0, 255)  # green kapla
BLU  = Color(  0,   0, 140, 255)  # blue kapla
YEL  = Color(255, 214,   0, 255)  # yellow kapla
TRANS = Color(50,50,50,100)
ALL_COLORS = (RED, GRN, BLU, YEL)
DBL_COLORS = (RED, RED,GRN,GRN,BLU,BLU,YEL,YEL)


'''
II. geometric helper functions ------------------------------------------------
'''
def spine_from_quad(q):
    '''
    returns maximum visible extents
    viewed from sides
    as a line
    '''
    return (min(q, key=lambda x: x[1]), max(q, key=lambda x: x[1]))

def line_to_pts(lines):
    '''
    flatten a list of lines
    returns a continuous list of pts
    '''
    return([point for line in lines for point in line])

def quads_from_points((a,b,c,d,e,f,g,h,i,j,k,l)):
    return ((a,b,c,d), (d,e,f,g), (g,h,i,j), (j,k,l,a))

ALL_VERTS = (a,b,c,d,e,f,g,h,i,j,k,l) # list of vtx counterclockwise
ALL_QUADS= quads_from_points(ALL_VERTS)


'''
III. shapes init --------------------------------------------------------------
'''
def init_constructions():
    # construction lines
    circle(radout, color=C0)
    circle(radin, color=C0)

def init_kaplas():
    kpl=[quad(a, b, c, d, color=TRANS) for q, clr in zip(ALL_QUADS,ALL_COLORS)]
    return(kpl)

def init_spines():
    lns = [line(*spine_from_quad(q), color=clr)
            for q, clr in zip(ALL_QUADS,ALL_COLORS)]
    return(lns)

def init_projected_lines():
    return()

#-------------------------- MAIN for SELF-TESTING -----------------------------
def _update(dt):
    redraw()

if __name__ == "__main__":

    from canvas import redraw, run
    from pyglet.clock import schedule_interval

    init_constructions()
    init_kaplas()
    init_spines()
    schedule_interval(_update,1.0/60)
    run()

