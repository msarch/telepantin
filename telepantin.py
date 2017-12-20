#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


from pyglet.clock import schedule_interval
from canvas import redraw, run, CANVAS_PAUSED
from wheel import init, k_vertex
from shapes import transform, quad_vertices_renew

alpha = 0.0                         # flywheel initial angle
REV_PER_SEC = 0.1                   # flywheel angular velocity 0.5= 0.5rev/s

'''
scene stuff -------------------------------------------------------------------
'''

def update(dt):
    global alpha
    if CANVAS_PAUSED:pass
    else:
        # The 'Flywheel' has an uniform circular motion
        # all scene actions should update according to alpha
        alpha +=  dt * REV_PER_SEC * 360  # alpha is in degrees
        if alpha > 360 : alpha -= 360    # stay within [0,360°]
        print "+ alpha =", alpha
        # hard (non GL) move all points to have access to coordinates
        new_vtx = transform(k_vertex, dx=0, dy=0, ro=alpha)
        # true rotation of recs : update recs vertices from live points
        #for a,b,c,d,clr in get_quads(scene_points, edges_colors):
        #    kaplas[i].vertices = (a.x, a.y, b.x, b.y, c.x, c.y,
        #                          c.x, c.y, d.x, d.y, a.x, a.y)
        for quad in kaplas:
            print quad
            print new_vtx
            q = quad_vertices_renew(quad,new_vtx)
            print q
            print


    redraw()

#---------------------------------- MAIN --------------------------------------
if __name__ == "__main__":
    kaplas = init()
    schedule_interval(update,1.0/60)
    run()

