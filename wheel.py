#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


from shapes import line, circle, quad, moveto
from colors import Color, CLINE
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

# list of vtx counterclockwise from 'a' to 'l' and to 'a' again
k_vertex = (a,b,c,d,e,f,g,h,i,j,k,l,a)

# colors
kr  = Color(255,  69,   0, 255)  # red kapla
kg  = Color(  0,  99,   0, 255)  # green kapla
kb  = Color(  0,   0, 140, 255)  # blue kapla
ky  = Color(255, 214,   0, 255)  # yellow kapla
quads_colors = (kr, kg, kb, ky)    # quads colors
edges_colors = (kr, kr, kr, kg, kg, kg, kb, kb, kb, ky, ky, ky)


def get_edges(vtx):
    '''
    yelds edges
    making pairs of vertex from a suite
    '''
    for i in xrange(len(vtx)-1):
        yield (vtx[i], vtx[i+1], edges_colors[i])

def get_quads(vtx):
    # yields number, coords and color
    for i in range(0,len(vtx)-1, 3):
        yield ((vtx[i], vtx[i+1], vtx[i+2], vtx[i+3], quads_colors[(i+3)/4]))

# edges
scene_edges = get_edges(k_vertex)

# quads
scene_quads = get_quads(k_vertex)


'''
II. sketches ------------------------------------------------------------------
'''
def init():

    # construction lines
    line(Pt(-CANVAS_WIDTH*0.16,CANVAS_HEIGHT/2),
         Pt(-CANVAS_WIDTH*0.16, -CANVAS_HEIGHT/2),
         color=CLINE)
    moveto(Pt(CANVAS_WIDTH*0.16,0))   # new current location
    circle(radout, color=CLINE)
    circle(radin, color=CLINE)

    # four rects in a cross, rotation will be applied to every point @ every dt
    kaplas=[quad(a, b, c, d, color=clr)
            for  a, b, c, d, clr in get_quads(k_vertex)]

    return(kaplas)


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

#-------------------------- MAIN for SELF-TESTING -----------------------------
def update(dt):
    redraw()

if __name__ == "__main__":

    from canvas import redraw, run
    from pyglet.clock import schedule_interval

    init()
    schedule_interval(update,1.0/60)
    run()

