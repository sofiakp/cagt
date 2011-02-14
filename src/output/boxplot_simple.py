#!/bin/python
#####################################################################
# boxplot_simple.py
# ---------------------------------------------------------
# boxplot_simple is designed to be a simple interface for making
# boxplots.  It takes a "type" argument (cluster_type), and 
# passes different arguments to boxplot() based on the type.
# In general, if you want to make a new kind of plot, add another 
# supported "type" argument.
#####################################################################

from rpy_matrix_conversion import *
from parameters import *
from src.filenames import *
from src.utils import index_r_data
from src.output.make_dimnames import make_dimnames
from src.output.boxplot import boxplot

def get_group_bounds(clustering_info, group_number):
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


def boxplot_simple(clustering_info, cluster_type, shape_number=None, group_number=None):
	
	profiles_info = clustering_info.profiles_info
	peak_tag = profiles_info.peak_tag
	signal_tag = profiles_info.signal_tag

	output_id = clustering_info.output_id

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

	
