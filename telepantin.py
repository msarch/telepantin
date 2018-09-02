#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


from math import hypot
from pyglet.clock import schedule_interval
from canvas import CANVAS_PAUSED, CANVAS_HEIGHT, CANVAS_WIDTH
import canvas
from colors import Color, DULL, TRANS
from shapes import transform, Pt, line, circle, quad, moveto
from shapes import quad_verts_update, line_verts_update, quad_colors_update

alpha = 0.0                         # flywheel initial angle
REV_PER_SEC = 0.08                  # angular velocity default =0.5 0.5rev/s



'''
I. geometric data -------------------------------------------------------------

kaplas vertex names are letters
edges have numbers and colors

        f--4---e
        |      |
        5 grn. 3
        |      |
 h--6---g      d---2---c
 |                     |
 7  blue   .     red  1
 |                     |
 i--8---j      a---0---b
        |      |
        9 yel. 11
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
# colors
RED  = Color(255,  69,   0, 255)  # red kapla
GRN  = Color(  0,  99,   0, 255)  # green kapla
BLU  = Color(  0,   0, 140, 255)  # blue kapla
YEL  = Color(255, 214,   0, 255)  # yellow kapla

# points
a, b, c = Pt( tk2, -tk2), Pt(span,-tk2),  Pt(span, tk2)
d, e, f = Pt( tk2,  tk2), Pt(tk2, span),  Pt(-tk2, span)
g, h, i = Pt(-tk2,  tk2), Pt(-span,tk2),  Pt(-span, -tk2)
j, k, l = Pt(-tk2, -tk2), Pt(-tk2,-span), Pt(tk2, -span)


ALL_COLORS = (RED, GRN, BLU, YEL)
DBL_COLORS = (RED, RED,GRN,GRN,BLU,BLU,YEL,YEL)


'''
II. geometric helper functions ------------------------------------------------
'''
def line_to_pts(lines):
    '''
    flatten a list of lines
    returns a continuous list of pts
    '''
    return([point for line in lines for point in line])

def wheel_from_points((a,b,c,d,e,f,g,h,i,j,k,l)):
    return ((a,b,c,d), (d,e,f,g), (g,h,i,j), (j,k,l,a))

ALL_VERTS = (a,b,c,d,e,f,g,h,i,j,k,l) # list of vtx counterclockwise
ALL_QUADS= wheel_from_points(ALL_VERTS)


'''
III. shapes init --------------------------------------------------------------
'''
def init_constructions():
    # construction lines
    circle(radout, color=DULL)
    circle(radin, color=DULL)

def init_kaplas():
    kpl=[quad(a, b, c, d, color=TRANS) for q, clr in zip(ALL_QUADS,ALL_COLORS)]
    return(kpl)

def init_spines():
    '''
    empty lines
    '''
    lns = [line(*spine_from_quad(q), color=clr)
            for q, clr in zip(ALL_QUADS,ALL_COLORS)]
    return(lns)

def init_sides():
    '''
    empty lines
    '''
    lns = [line(*spine_from_quad(q), color=clr)
            for q, clr in zip(ALL_QUADS,ALL_COLORS)]
    return(lns)


'''
IV. pseudo 2D VISIBILITY ------------------------------------------------------
'''
def spine_from_quad(q):
    '''
    returns the line corresponding to
    the maximum extents of the quad viewed from aside
    as a line
    '''
    print min(q, key=lambda x: x[1]), max(q, key=lambda x: x[1])
    return (min(q, key=lambda x: x[1]), max(q, key=lambda x: x[1]))

def project(lines,alpha):
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
    return([])



'''
V. scene stuff -------------------------------------------------------------------
'''


def update(dt):
    '''
    color wheel spinning
    scene actions update with alpha who describes a uniform circular motion
    '''
    if canvas.CANVAS_PAUSED:
        pass
    else:
        global alpha
        alpha += dt * REV_PER_SEC * 360  # alpha is in degrees
        if alpha > 360:
            alpha -= 360    # stay within [0,360°]

        # update points (hard move (not GLrotate) to keep track of coordinates)
        new_verts = transform(ALL_VERTS, dx=0, dy=0, ro=alpha)
        # update quads vertices from new verts
        new_kaplas = wheel_from_points(new_verts)
        [quad_verts_update(k, q) for k, q in zip(kaplas, new_kaplas)]
        # update spine lines of new quads
        new_spines = [spine_from_quad(q) for q in new_kaplas]
        [line_verts_update(s, l) for s, l in zip(spines, new_spines)]
        # side vision
        new_sides = project(sides, alpha)
        [line_verts_update(s, l) for s, l in zip(sides, new_sides)]
    canvas.redraw()


# --------------------------------- MAIN --------------------------------------
if __name__ == "__main__":
    init_constructions()
    kaplas = init_kaplas()
    spines = init_spines()
    sides = init_sides()
    # side_shapes = sidevision.init_side_quads()
    schedule_interval(update, 1.0/60)
    print "+ revolving ..."
    canvas.run()
