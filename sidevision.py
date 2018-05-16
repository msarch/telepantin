#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


from shapes import PT0
from colors import C0
from canvas import Pt, CANVAS_WIDTH


# 2D VISIBILITY ---------------------------------------------------------------

def spine_from_quad(q):
    return (min(q, key=lambda x: x[1]), max(q, key=lambda x: x[1]))

def line_to_pts(lines):
    '''
    flatten a list of lines
    returns a continuous list of pts
    '''
    return([point for line in lines for point in line])

def sort_vertical(pts, clrs=DBL_COLORS):
    # sort augmented points along X first from closest (-) to furthest (+)
    #pts = sorted(pts , key=lambda e: e[0].x)
    # sort again along Y  from upper (+) to lower (-)
    #pts = sorted(pts , key=lambda e: e[0].y, reverse=True)
    pts, clrs = zip(*sorted(zip(pts,clrs),key=lambda e: e[0].x))
    pts, clrs = zip(*sorted(zip(pts,clrs),key=lambda e: e[0].y,reverse=True))
    return (pts, clrs)

def is_visible(points,lines):
    return(points)

    return (a,b,c,d)


def is_hidden(point,line):
    return(True)

def is_right_of(point, line, epsilon=0.1):
    position = sign((Bx - Ax) * (Y - Ay) - (By - Ay) * (X - Ax))

    '''
    0  : on the line,
    +1 : on one side,
    -1 : on the other side
    '''
    return(True)

def intersection_of(l1,l2):

    denom  = (y4-y3) * (x2-x1) - (x4-x3) * (y2-y1)
    numera = (x4-x3) * (y1-y3) - (y4-y3) * (x1-x3)
    numerb = (x2-x1) * (y1-y3) - (y2-y1) * (x1-x3)
    mua = numera / denom
    mub = numerb / denom
    x = x1 + mua * (x2 - x1);
    y = y1 + mua * (y2 - y1)
    return(Point(x,y))

def get_side_strip(sorted_pts,sorted_segments):
        final_ptlist=(sorted_pts[0])
        final_cllist=(sorted_clrs[0])
        for p in sorted_pts:
            # p is next highest point
            for line in live_spines_verts:
                if is_left(p,line):
                    # point is not hidden by this line:
                    # goto next line
                    continue
                else:  #pt is on right side
                    if is_in_between(point,line):
                    # point is hidden by this line
                        continue
                    else:
                    # break line loop and goto next point
                        break



                # point is left of all lines
                # add point and goto next point

# DRAWING UTILITIES -----------------------------------------------------------
def init_side_quads():
    return([(PT0,PT0,PT0,PT0, C0)for i in range(4)])

# iter through pair of coordinates in a flat list of coords to make quads
def project(spines, x=-CANVAS_WIDTH*0.32):
    # first : spines to list of points augmented with colors
    pts_n_color =[(coord,i) for i,point in enumerate(spines) for coord in point]
    return([(Pt(x,p.y),c)for p,c in pts_n_color])

def make_recs_from_points(pts):
    p = iter(pts)
    for i in xrange(len(pts)/2):
        p1 = p.next()
        p2 = p.next()
        a = Pt(p1[0][0]-300,p1[0][1]),
        b = Pt(p2[0][0],p1[0][1]),
        c = Pt(p1[0][0],p2[0][1]),
        d = Pt(p2[0][0]-300,p2[0][1])


#-------------------------- MAIN for SELF-TESTING -----------------------------
def _update(dt):
    redraw()

if __name__ == "__main__":

    from canvas import redraw, run
    from pyglet.clock import schedule_interval

    schedule_interval(_update,1.0/60)
    run()


