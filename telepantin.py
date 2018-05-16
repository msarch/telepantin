#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


from pyglet.clock import schedule_interval
import canvas
import wheel
from wheel import ALL_VERTS, quads_from_points, spine_from_quad
from shapes import transform
from shapes import update_quad_verts, update_line_verts, update_quad_colors
# import sidevision
# from sidevision import sort_vertical, make_recs_from_points, line_to_pts

alpha = 0.0                         # flywheel initial angle
REV_PER_SEC = 0.05                   # flywheel angular velocity 0.5= 0.5rev/s

'''
scene stuff -------------------------------------------------------------------
'''


def update(dt):
    if canvas.CANVAS_PAUSED:
        pass
    else:
        '''
        WHEEL module --------------------------------------------------------
        color wheel spinning
        The 'Flywheel' has an uniform circular motion
        all scene actions should update according to alpha
        '''
        global alpha
        alpha += dt * REV_PER_SEC * 360  # alpha is in degrees
        if alpha > 360:
            alpha -= 360    # stay within [0,360°]

        # update points (hard move (not GLrotate) to keep track of coordinates)
        live_verts = transform(ALL_VERTS, dx=0, dy=0, ro=alpha)
        # update quads vertices from live verts
        live_quads_verts = quads_from_points(live_verts)
        [update_quad_verts(k, q) for k, q in zip(kapla_shapes, live_quads_verts)]
        # update spine lines of live quads
        live_spines_verts = [spine_from_quad(q) for q in live_quads_verts]
        [update_line_verts(s, l) for s, l in zip(spine_shapes, live_spines_verts)]

        '''
        SIDEVISION module ---------------------------------------------------
        projection and hidden lines

        #first make 2 lists  with points and their color data
        sp_pts = line_to_pts(live_spines_verts)
        print 'list of points', sp_pts
        print '- - - - - -'
        (sorted_pts,sorted_clrs) = sort_vertical(sp_pts)
        print 'sorted points', sorted_pts
        print 'sorted clrs', sorted_clrs
        print '- - - - - -'
        #side_view_points = is_visible(sorted_pts, live_spines_verts)
        #print 'side view points', side_view_points
        #print '___________________'
        get_side_strip(sorted_points,their_segment)

        live_siderec_verts = make_recs_from_points(sorted_pts)
        [update_quad_verts(i,v) for i,v in zip(siderec_shapes, live_siderec_verts)]
        [update_quad_colors(s,c) for s,c in zip(siderec_shapes,sorted_clrs)]
        '''
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
