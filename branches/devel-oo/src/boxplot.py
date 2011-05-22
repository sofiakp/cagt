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
from src.rpy_matrix_conversion import np_matrix_to_r




def make_dimnames(clustering_info, ids):
	space_between_colnames = clustering_info.profiles_info.args.space_between_colnames

	rownames = ids

	num_cols = clustering_info.PD.data.data.shape[1]
	colnames = num_cols*[""]
	middle = int(float(num_cols)/2)
	colnames[middle] = ["0"]

	for i in range(middle,0,-space_between_colnames):
		colnames[i]= str((i-middle)*clustering_info.profiles_info.bin_size)
	for i in range(middle+space_between_colnames,num_cols,space_between_colnames):
		colnames[i]= "+" + str((i-middle)*clustering_info.profiles_info.bin_size)

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
def boxplot_simple(clustering_info, cluster_type, shape_number=None, group_number=None):

	profiles_info = clustering_info.profiles_info
	peak_tag = profiles_info.peak_tag
	signal_tag = profiles_info.signal_tag

	# output_id = clustering_info.output_id
	args = clustering_info.profiles_info.args
	num_groups = args.num_groups
	group_by_quantile = args.group_by_quantile
	normalize_ylims = [args.normalize_lower_ylim, args.normalize_upper_ylim]
	# ids
	if cluster_type == "all":
		ids = clustering_info.ids
	elif cluster_type == "low_signal":
		ids = clustering_info.low_signal
	elif cluster_type == "high_signal":
		ids = clustering_info.high_signal
	elif cluster_type == "magnitude_group":
		ids = clustering_info.group_clusters[group_number]
	elif cluster_type == "shape_cluster_unflipped":
		ids = clustering_info.shape_clusters_unflipped[shape_number]
	elif cluster_type == "shape_cluster":
		ids = clustering_info.shape_clusters[shape_number]
	elif cluster_type == "shape_cluster_oversegmented":
		ids = clustering_info.shape_clusters_oversegmented[shape_number]
	elif cluster_type == "grouped_shape":
		shape_ids = clustering_info.shape_clusters[shape_number]
		group_ids = clustering_info.group_clusters[group_number]
		ids = list(set(shape_ids) & set(group_ids))
	else:
		print "cluster_type unrecognized"

	if cluster_type in ["shape_cluster","grouped_shape"]:
		flipped = list(set(ids) & set(clustering_info.flipped))
	else:
		flipped = None


	if len(ids) < 4:
		# too few profiles to plot
		return

	if cluster_type in ["magnitude_group", "grouped_shape"]:
		# Find cutoffs for this group
		group_lower_bound, group_upper_bound = get_group_bounds(clustering_info, group_number)

	# title
	if cluster_type == "all":
		title="All profiles: "+str(clustering_info.num_peaks)+" profiles"
	elif cluster_type == "low_signal":
		title="Low signal profiles: "+str(len(ids))+" profiles"
	elif cluster_type == "high_signal":
		title="High signal profiles: "+str(len(ids))+" profiles"
	elif cluster_type == "magnitude_group":
		title="Profiles with "+ str(int(group_by_quantile*100))+\
		"% quantile in the range "+group_lower_bound+"-"+group_upper_bound+\
		": "+str(len(ids))+" profiles"\
		+" ("+str(int(100*float(len(ids))/len(clustering_info.high_signal)))+"%)"
	elif cluster_type == "shape_cluster_unflipped":
		title="Unflipped shape "+str(shape_number)+": "+str(len(ids))+" profiles"\
		+" ("+str(int(100*float(len(ids))/len(clustering_info.high_signal)))+"%)"
	elif cluster_type == "shape_cluster":
		title="Shape "+str(shape_number)+": "+str(len(ids))+" profiles"\
		+" ("+str(int(100*float(len(ids))/len(clustering_info.high_signal)))+"%)"
	elif cluster_type == "shape_cluster_oversegmented":
		title = "Oversegmented shape "+str(shape_number)+": "+str(len(ids))+" profiles"\
		+" ("+str(int(100*float(len(ids))/len(clustering_info.high_signal)))+"%)"
	elif cluster_type == "grouped_shape":
		title = "Shape "+str(shape_number)+", group ("+group_lower_bound+"-"+group_upper_bound+")"+\
		": "+str(len(ids))+" profiles"\
		+" ("+str(int(100*float(len(ids))/len(clustering_info.high_signal)))+"%)"
	else:
		print "cluster_type unrecognized"

	make_vertical_line_in_middle=True
	if cluster_type in ["shape_cluster","shape_cluster_unflipped","shape_cluster_oversegmented"]:
		normalize = True
		ylims = normalize_ylims
		make_horizontal_line_at_origin = True
	else:
		normalize = False
		ylims = profiles_info.ylims
		make_horizontal_line_at_origin = False

	filename = make_filename(profiles_info, file_type="boxplot", type_of_data=cluster_type,\
	shape_number=shape_number, group_number=group_number)

	try:
		boxplot(clustering_info, ids, filename=filename, title=title, ylim=ylims, flipped=flipped,\
		make_horizontal_line_at_origin=make_horizontal_line_at_origin,
		make_vertical_line_in_middle=make_vertical_line_in_middle, normalize=normalize)
	except Exception, error:
		logging.error("Hit error while making boxplot")
		logging.error("profiles_info: %s", str(clustering_info.profiles_info))
		logging.error("boxplot_simple arguments: cluster_type=%s ; shape_number=%s ; group_number=%s",
		cluster_type, str(shape_number), str(group_number))
		logging.error(str(error))
		logging.error(traceback.format_exc())
		print "HIT ERROR WHILE MAKING PLOT"
		traceback.print_exc()
		print "Skipping this plot"
		print "See logs for details"


	return



# Wrapper on rpy's boxplot(), with quite a few arguments defined.
def boxplot(clustering_info, ids,\
filename=None, title="",\
ylim=[-4,4], ylab="Normalized Signal", xlab="Relative distance to TF binding site",\
flipped=None, normalize=False,\
make_horizontal_line_at_origin = False, make_vertical_line_in_middle = True):

  # manually garbage collect
  gc.collect()

  if filename is not None:
    r['png'](file=filename)

  if flipped is None:
    num_flipped = 0
  else:
    num_flipped = len(flipped)
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

  del r_data_to_plot

  gc.collect()

  return




















