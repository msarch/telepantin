#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


from pyglet.clock import schedule_interval
import canvas
import wheel
from wheel import ALL_VERTS, quads_from_points, spine_from_quad
from wheel import sort_vertical, project, make_recs_from_points
from wheel import is_visible
from shapes import transform, update_quad_verts, update_line_verts, flatten

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

        # update points (hard (non GL) move to have access to coordinates)
        live_verts = transform(ALL_VERTS, dx=0, dy=0, ro=alpha)
        # update recs (quads vertices from live verts)
        live_quads_verts = quads_from_points(live_verts)
        [update_quad_verts(k,q) for k,q in zip(kapla_shapes,live_quads_verts)]
        # update spine lines of live quads
        live_spines_verts = [spine_from_quad(q) for q in live_quads_verts]
        [update_line_verts(s,l) for s,l in zip(spine_shapes,live_spines_verts)]

'''
wrong data type : go back to points and use 2 sorted lists: pt + clr:
    Dev, Python, Lists 6a, Sorting Two Lists Simulteanously

        # projection and hidden lines
        projected_points = project(live_spines_verts) #returns pts + color data
        print 'projected points', projected_points
        print '___________________'
        sorted_pts = sort_vertical(projected_points)
        print 'sorted points', sorted_pts
        print '___________________'
        side_view_points = is_visible(sorted_pts, live_spines_verts)
        print 'side view points', side_view_points
        print '___________________'
        (vtx, clr) = make_recs_from_points(side_view_points)
        [update_quad_verts(q,v) for q,v in zip(siderec_shapes,vtx)]
        q.colors = [c*6 for q,c in zip(siderec_shapes, clr)]

        canvas.redraw()

#---------------------------------- MAIN --------------------------------------
if __name__ == "__main__":
    wheel.init_constructions()
    kapla_shapes = wheel.init_kaplas()
    spine_shapes = wheel.init_spines()
    siderec_shapes = wheel.init_side_quads()
    schedule_interval(update,1.0/60)
    print "+ revolving ..."
    canvas.run()

