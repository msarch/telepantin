#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


from pyglet.clock import schedule_interval
from shapes import circle, line, quad
from colors import *
from canvas import redraw, run, CANVAS_HEIGHT, CANVAS_PAUSED
from definitions import BACKGROUND, ORIGIN
from wheel import alpha, radout, radin, scene_points, get_quads


'''
scene stuff -------------------------------------------------------------------
'''
def init():
    line(Pt(-CANVAS_CENTER.x*0.25,CANVAS_HEIGHT/2),
         Pt(-CANVAS_CENTER.x*0.25, -CANVAS_HEIGHT/2),
         color=CLINE)
    circle(radout, color=CLINE)
    circle(radin, color=CLINE)
    # four rects in a cross, rotation will be applied to every point @ every dt
    kaplas=[quad(a, b, c, d, color=clr)
            for  a, b, c, d, clr in get_quads(scene_points)]
    return()

def update(dt):
    global alpha
    if CANVAS_PAUSED:pass
    else:
        # The 'Flywheel' has an uniform circular motion
        # all scene actions should update according to alpha
        alpha +=  dt * REV_PER_SEC * 360  # alpha is in degrees
        if alpha > 360 : alpha -= 360    # stay within [0,360°]
        print alpha
        # hard (non GL) move all points to have access to coordinates
        live_points = transform(scene_points, dx=0, dy=0, ro=alpha)
        print live_points
        # true rotation of recs : update recs vertices from live points
        #for a,b,c,d,clr in get_quads(scene_points, edges_colors):
        #    kaplas[i].vertices = (a.x, a.y, b.x, b.y, c.x, c.y,
        #                          c.x, c.y, d.x, d.y, a.x, a.y)


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
    redraw(BATCH)
    return()

#---------------------------------- MAIN --------------------------------------
if __name__ == "__main__":
    init()
    schedule_interval(update,1.0/60)
    run()

