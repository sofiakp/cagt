import rpy2.robjects as rpy
r = rpy.r

from copy import deepcopy
import numpy as np
import gc
import sys
import logging
import traceback

from src.filenames import *
from src.utils import *
from src.utils import logTime
from src.rpy_matrix_conversion import np_matrix_to_r




def make_dimnames(profiles_info, ids, data):
    space_between_colnames = profiles_info.args.space_between_colnames

    rownames = ids

    num_cols = data.shape[1]
    colnames = num_cols*[""]
    middle = int(float(num_cols)/2)
    colnames[middle] = ["0"]

    for i in range(middle,0,-space_between_colnames):
        colnames[i]= str((i-middle)*profiles_info.bin_size)
    for i in range(middle+space_between_colnames,num_cols,space_between_colnames):
        colnames[i]= "+" + str((i-middle)*profiles_info.bin_size)

    return [rownames, colnames]



def get_group_bounds(clustering_info, group_number):
    num_groups = clustering_info.profiles_info.args.num_groups
    group_cutoffs = clustering_info.group_cutoffs
    if group_number == 0:
        group_lower_bound = "0"
    else:
        group_lower_bound = str(group_cutoffs[group_number-1])[:3]
    if group_number == num_groups-1:
        group_upper_bound = "inf"
    else:
        group_upper_bound = str(group_cutoffs[group_number])[:3]
    return group_lower_bound, group_upper_bound


#####################################################################
# boxplot_simple.py
# ---------------------------------------------------------
# boxplot_simple is designed to be a simple interface for making
# boxplots.  It takes a "type" argument (cluster_type), and
# passes different arguments to boxplot() based on the type.
# In general, if you want to make a new kind of plot, add another
# supported "type" argument.
#####################################################################
@logTime
def boxplot_simple(clustering_result, PD, cluster_id):
    ids = clustering_result.cluster_members(cluster_id)

    if len(ids) < 4:
        # too few profiles to plot
        return

    title = clustering_result.boxplot_title(cluster_id)
    make_vertical_line_in_middle = clustering_result.boxplot_make_verticle_line_in_middle(cluster_id)
    make_horizontal_line_at_origin = clustering_result.boxplot_make_horizontal_line_at_origin(cluster_id)
    ylims = clustering_result.boxplot_ylims(cluster_id)
    ylab = clustering_result.ylab(cluster_id)
    filename = make_filename('cluster', 'boxplot',
                             clustering_result=clustering_result,
                             cluster_id=cluster_id)
    data = clustering_result.data_for_plotting(PD, cluster_id)
    dimnames = make_dimnames(clustering_result.profiles_info, ids, data)

    boxplot(data, ids, dimnames, filename=filename, title=title, ylim=ylims,
            make_horizontal_line_at_origin=make_horizontal_line_at_origin,
            make_vertical_line_in_middle=make_vertical_line_in_middle)

    return



# Wrapper on rpy's boxplot(), with quite a few arguments defined.
@logTime
def boxplot(data, ids, dimnames,
            filename=None, title="",
            ylim=[-4,4], ylab="Normalized Signal", xlab="Relative distance to TF binding site",
            flipped=None, normalize=False,
            make_horizontal_line_at_origin = False, make_vertical_line_in_middle = True):

    data_to_plot = data

    # manually garbage collect
    gc.collect()

    if filename is not None:
        r['png'](file=filename)

    r_data_to_plot = np_matrix_to_r(data_to_plot.data)



    ##############################
    # Make boxplot
    r['boxplot'](r['as.data.frame'](r_data_to_plot), \
    ylim=rpy.IntVector(ylim),\
    outline=False,
    names=rpy.StrVector(dimnames[1]),\
    xlab=xlab,\
    ylab=ylab,\
    main=title,\
    medlwd=0,\
    boxlwd=3, boxcol="#444444",\
    whisklty=1, whisklwd=3, whiskcol="#777777",\
    staplelwd=0,\
    xaxt="n")

    ############################
    # Make mean line

    # Since rpy matrixes don't support multi-dimensional indexing,
    # we'll have to compute indices by hand.
    # rpy matrixes are indexed by column, then by row
    means = np.apply_along_axis(lambda col: sum(col)/len(col), 0, data_to_plot.data)
    r['lines'](\
    x=rpy.FloatVector(means),\
    lty=1, col="Black", lwd=3)

    #############################
    # Make x axis marks
    # ------------
    # Only plot nonempty row dimnames.  This is necessary because axis()
    # avoids printing dimnames on top of one another.    Naively, to avoid
    # this, one might set all but a few dimnames to be "", but axis()
    # doesn't recognize this.
    nonempty_row_dimnames_indices = \
    filter(lambda i: dimnames[1][i] != "" , range(len(dimnames[1])))
    nonempty_row_dimnames = map(lambda i: dimnames[1][i], nonempty_row_dimnames_indices)
    r['axis'](r('1:'+str(len(nonempty_row_dimnames)+1)), \
    at=nonempty_row_dimnames_indices, \
    labels=nonempty_row_dimnames, \
    )

    if make_horizontal_line_at_origin:
        r['lines'](\
        x=rpy.FloatVector([0,int(len(dimnames[1]))+1]),\
        y=rpy.FloatVector([0]*2),\
        lty=2)
    if make_vertical_line_in_middle:
        r['lines'](\
        x=rpy.FloatVector([int(r_data_to_plot.ncol/2)]*2),\
        y=rpy.FloatVector([-1000,1000]),\
        lty=2)

    if filename is not None:
        r('dev.off()')

    del r_data_to_plot

    gc.collect()

    return




















