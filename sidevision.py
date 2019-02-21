#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


# 2D VISIBILITY ---------------------------------------------------------------
def spine_from_quad(q):
    '''
    returns maximum visible extents of a quad
    viewed from sides
    as a line
    '''
    print min(q, key=lambda x: x[1]), max(q, key=lambda x: x[1])
    return (min(q, key=lambda x: x[1]), max(q, key=lambda x: x[1]))

'''
III. SIDEVISION  -projection and hidden lines ---------------------------------

def project_spines (list_of_spines, spines_colors)
    # empty return lists
    list_of_segments, segment_colors = [],[]

    for s in list_of_spines:
        others=list_fo_spines-s

        # project me to the left : check against others that might hide me
        # and get projected parts of me

        list_of_segments.append(project_me(s, others))

    return(list_of_segments, segment_colors)

def project_me (me others)

'''

#-------------------------- MAIN for SELF-TESTING -----------------------------
def _update(dt):
    redraw()

if __name__ == "__main__":

    from canvas import redraw, run
    from pyglet.clock import schedule_interval

    schedule_interval(_update,1.0/60)
    run()
