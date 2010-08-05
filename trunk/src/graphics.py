#!/bin/python
#####################################################################
# graphics.py
# Max Libbrecht
# Updated 7/10
# ---------------------------------------------------------
# This module is responsible for generating figures.
# These functions are mostly just interfaces to their R counterparts.
# Most parameters of the generated figures are determined here,
# except for the main title of the figure, which is passed as 
# an argument.  This module relies heavily on rpy.
#####################################################################

import sys
sys.path.append('../')

from rpy_matrix_conversion import *
from parameters import *

def heatmap(data, dimnames, mode, filename=None, title=""):
	r_data = np_matrix_to_r(data, dimnames=dimnames)

	if mode == "normalize":
		heatmap_lims = normalize_heatmap_lims
	if mode == "group":
		heatmap_lims = group_heatmap_lims

	if filename is not None:
		r['png'](file=filename)
	
	
	
	
	r['heatmap'](r_data, Colv=r('NA'), Rowv=r('NULL'),\
	distfun=r['dist'], hclustfun=r['hclust'], col=r('heat.colors(100)'),\
	zlim=r('c('+str(heatmap_lims[0])+','+str(heatmap_lims[1])+')'), scale="none",\
	xlab="Positions within a 2500bp window around TF binding site",\
	ylab="TF binding sites",\
	main=title,\
	)
		
	if filename is not None:
		r('dev.off()')

	return
	
	
def boxplot(data, dimnames, mode, filename=None, title=""):
	r_data = np_matrix_to_r(data, dimnames)
	if filename is not None:
		r['png'](file=filename)

	if mode == "normalize":
		boxplot_lims = normalize_boxplot_lims
	if mode == "group":
		boxplot_lims = group_boxplot_lims


	r['boxplot'](r['as.data.frame'](r_data), ylim=r('c('+str(boxplot_lims[0])+','+str(boxplot_lims[1])+')'), outline=False,
	names=rpy.StrVector(dimnames[1]),\
	xlab="Positions within a 2500bp window around TF binding site",\
	ylab="Intensity",\
	main=title)

	if filename is not None:
		r('dev.off()')
	return 
