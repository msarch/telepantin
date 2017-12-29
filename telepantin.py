#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


from pyglet.clock import schedule_interval
import canvas
import wheel
from wheel import all_verts, quads_from_points, quad_spine
from shapes import transform, update_quad_verts, update_line_verts

alpha = 0.0                         # flywheel initial angle
REV_PER_SEC = 0.1                   # flywheel angular velocity 0.5= 0.5rev/s

'''
scene stuff -------------------------------------------------------------------
'''

def update(dt):
    if canvas.CANVAS_PAUSED:
        pass
    else:
        global alpha
        # The 'Flywheel' has an uniform circular motion
        # all scene actions should update according to alpha
        alpha +=  dt * REV_PER_SEC * 360  # alpha is in degrees
        if alpha > 360 : alpha -= 360    # stay within [0,360°]

        # hard (non GL) move all points to have access to coordinates
        live_verts = transform(all_verts, dx=0, dy=0, ro=alpha)
        live_quads = quads_from_points(live_verts)
        # true rotation of recs : update recs vertices from live points
        [update_quad_verts(k,q) for k,q in zip(kaplas,live_quads)]

        #make simple lines
        [update_line_verts(l,quad_spine(q)) for l,q in zip(spines,live_quads)]

    canvas.redraw()

#---------------------------------- MAIN --------------------------------------
if __name__ == "__main__":
    wheel.init_constructions()
    kaplas = wheel.init_kaplas()
    spines = wheel.init_spines()
    schedule_interval(update,1.0/60)
    print "+ revolving ..."
    canvas.run()

