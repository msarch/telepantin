#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


from pyglet.clock import schedule_interval
import wheel
import canvas
from canvas import CANVAS_PAUSED
from wheel import ALL_VERTS, quads_from_points
from sidevision import spine_from_quad
from shapes import transform
from shapes import quad_verts_update, update_line_verts, update_quad_colors
# import sidevision
# from sidevision import sort_vertical, make_recs_from_points, line_to_pts

alpha = 0.0                         # flywheel initial angle
REV_PER_SEC = 0.05                   # flywheel angular velocity 0.5= 0.5rev/s

'''
scene stuff -------------------------------------------------------------------
'''


def update(dt):
    '''
    color wheel spinning
    scene actions update with alpha who describes a uniform circular motion
    '''
    if CANVAS_PAUSED:
        pass
    else:
        global alpha
        alpha += dt * REV_PER_SEC * 360  # alpha is in degrees
        if alpha > 360:
            alpha -= 360    # stay within [0,360°]

        # update points (hard move (not GLrotate) to keep track of coordinates)
        live_verts = transform(ALL_VERTS, dx=0, dy=0, ro=alpha)
        # update quads vertices from live verts
        live_quads_verts = quads_from_points(live_verts)
        [quad_verts_update(k, q) for k, q in zip(kapla_shapes, live_quads_verts)]
        # update spine lines of live quads
        live_spines_verts = [spine_from_quad(q) for q in live_quads_verts]
        [update_line_verts(s, l) for s, l in zip(spine_shapes, live_spines_verts)]

        canvas.redraw()


# --------------------------------- MAIN --------------------------------------
if __name__ == "__main__":
    wheel.init_constructions()
    kapla_shapes = wheel.init_kaplas()
    spine_shapes = wheel.init_spines()
    side_lines = wheel.init_projected_lines()
    # side_shapes = sidevision.init_side_quads()
    schedule_interval(update, 1.0/60)
    print "+ revolving ..."
    canvas.run()
