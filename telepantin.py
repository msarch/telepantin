#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# http://www.github.com/msarch/slide

import pyglet
from shapes import *
from colors import *
from canvas import redraw
# debug flags
VERBOSE = False
VERBOSE = True
if VERBOSE : frame_number, duration = 0,0

REV_PER_SEC = 0.1                   # angular velocity 0.5= 0.5rev/s
alpha = 0.0                         # flywheel initial angle

# kapla colors ----------------------------------------------------------------
kr  = Color(255,  69,   0, 255)  # red kapla
kg  = Color(  0,  99,   0, 255)  # green kapla
kb  = Color(  0,   0, 140, 255)  # blue kapla
ky  = Color(255, 214,   0, 255)  # yellow kapla
'''
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
    print '-                        scene data'
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

# -------------------------------- END OF SCENE INIT --------------------------

# -----------------------------------------------------------------------------
# ----------------------------- SCENE HELPERS FUNC ----------------------------
# -----------------------------------------------------------------------------
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

    # first sort edges along X first, from rightmost (+) to leftmost (-)
    sorted_e = sorted(sorted_e , key=lambda e: e[1].x, reverse=True)

    if VERBOSE:
        print '= Y sorted edges:'
        for e in sorted_e:
            for _ in e : print '    .', _
            print ''

    # then sort edges along Y from highest (+) to lowest (-)
    # former X order will persist after this sorting
    sorted_e = sorted(edges , key=lambda e: e[1].y, reverse=True)


    if VERBOSE:
        print '= Y+X sorted edges:'
        for e in sorted_e:
            for _ in e : print '    .', _
            print ''


    return(sorted_e)


# ---------------------------- END OF HELPERS FUNCTIONS -----------------------

# -----------------------------------------------------------------------------
# -------------------------------- UPDATE SECTION -----------------------------
# -----------------------------------------------------------------------------
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
            print '-----------------------------------------------------------'
            print '-'
            print '-                    updating'
            print '-                    . alpha    :', alpha
            print '-                    . duration :', duration
            print '-                    . frame #  :', frame_number
            print '-                    . FPS      :', 1/dt
            print '-'
            print '-----------------------------------------------------------'
            print ''

        scene_update(dt)

    redraw()

def scene_update(dt):

    # --- main movement update section ----------------------------------------

    # wheel sketch is always rotating
    wheel.ro = alpha

    # hard (non GL) move all points to have access to coordinates
    live_points = transform(scene_points, dx=0, dy=0, ro=alpha)

    # true rotation of recs : update recs vertices from live points
    update_quads(kaplas, live_points, quads_colors)


    # --- project edges section -----------------------------------------------

    '''
    1- get shortlist of only front facing edges
    by filtering backward oriented normal edges
    '''
    facing_edges = filter_edges(get_edges(live_points, edges_colors))

    '''
    2- flip edges
    if necessary flip end/start so highest point is first
    '''
    oriented_edges = flip_edges(facing_edges)

    '''
    3- sort edges.starts :
        highest Y
        closest to the right CENTROID first if Y's are equal
    '''
    sorted_edges = sort_edges(oriented_edges)

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

# ---------------------------  END OF SCENE UPDATE  ---------------------------

# -----------------------------------------------------------------------------
#---------------------------------- MAIN --------------------------------------
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1.0/120)
    pyglet.app.run()

# vim: set foldmarker={{{,}}} foldmethod=marker foldcolumn=4 :
