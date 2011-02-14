#!/bin/python
#####################################################################
# boxplot.py
# ---------------------------------------------------------
# boxplot is a wrapper for rpy's boxplot function.  It's quite low-level;
# it should only be called from boxplot_simple.  
#####################################################################

import rpy2.robjects as rpy
r = rpy.r

from copy import deepcopy
import numpy as np

import sys

from parameters import *
from src.filenames import *
from src.utils import *
from src.output.make_dimnames import make_dimnames
from src.output.rpy_matrix_conversion import np_matrix_to_r
#from src.output.rpy_matrix_conversion import *


# Wrapper on rpy's boxplot(), with quite a few arguments defined.
#
# If normalize is True, boxplot expects high-signal indices,
# but if normalize is False, boxplot expects full-range indices
# That's ridiculous, I really need to change that soon.
def boxplot(clustering_info, ids,\
filename=None, title="",\
ylim=[-4,4], ylab="Normalized Signal", xlab="Relative distance to TF binding site",\
flipped=None, normalize=False,\
make_horizontal_line_at_origin = False, make_vertical_line_in_middle = True):

	if filename is not None:
		r['png'](file=filename)

	num_flipped = 0 if flipped is None else len(flipped) 
	if num_flipped != 0:
		title += " ("+str(num_flipped)+" flipped)"

	if normalize:
		data_to_plot = clustering_info.PD.high_signal_norm_data.get_rows(ids)
	else:
		data_to_plot = clustering_info.PD.data.get_rows(ids)
	
	if num_flipped != 0:
		for flipped_id in flipped:
			data_to_plot.set_row(flipped_id, np.array(data_to_plot.get_row(flipped_id))[::-1])

	r_data_to_plot = np_matrix_to_r(data_to_plot.data)

	dimnames = make_dimnames(clustering_info, ids)


	##############################
	# Make boxplot
	r['boxplot'](r['as.data.frame'](r_data_to_plot), \
	ylim=rpy.IntVector(ylim),\
	outline=False,
	names=rpy.StrVector(dimnames[1]),\
	xlab=xlab,\
	ylab=ylab,\
	main=title,\
	# sub="signal file: "+clustering_info.profiles_info.signal_filename+\
	# "; peak file: "+clustering_info.profiles_info.peak_filename,\
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
	# avoids printing dimnames on top of one another.  Naively, to avoid
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
		
	return 
	
	
















	
	
