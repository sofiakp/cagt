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
from src.utils import get_assignment_indices, map_indices
from src.output.make_dimnames import make_dimnames
from src.output.boxplot import boxplot

def get_group_bounds(clustering_info, peak_tag, signal_tag, group_number):
	group_cutoffs = clustering_info.group_cutoffs[peak_tag][signal_tag]
	if group_number == 0:
		group_lower_bound = "0"
	else:
		group_lower_bound = str(group_cutoffs[group_number-1])[:3]
	if group_number == num_groups-1:
		group_upper_bound = "inf"
	else:
		group_upper_bound = str(group_cutoffs[group_number])[:3]
	return group_lower_bound, group_upper_bound


def boxplot_simple(clustering_info, peak_tag, signal_tag,\
cluster_type, shape_number=None, group_number=None):
	

	output_id = clustering_info.output_id

	if cluster_type == "all":
		indices = range(clustering_info.num_peaks[peak_tag])
		boxplot(clustering_info, peak_tag, signal_tag, indices,\
		filename=make_all_profiles_boxplot_filename(peak_tag, signal_tag, output_id),\
		title="All profiles: "+str(clustering_info.num_peaks[peak_tag])+" profiles",\
		ylim=clustering_info.boxplot_ylims[signal_tag],\
		make_horizontal_line_at_origin = False, make_vertical_line_in_middle = True)
	
	elif cluster_type == "low signal":
		indices = clustering_info.low_signal[peak_tag][signal_tag]
		
		boxplot(clustering_info, peak_tag, signal_tag, indices,\
		filename=make_low_signal_boxplot_filename(peak_tag, signal_tag, output_id),\
		title="low signal profiles: "+str(len(indices))+" profiles",\
		ylim=clustering_info.boxplot_ylims[signal_tag],\
		make_horizontal_line_at_origin = False, make_vertical_line_in_middle = True)
		
	
	elif cluster_type == "high signal":
		indices = clustering_info.high_signal[peak_tag][signal_tag]
		
		boxplot(clustering_info, peak_tag, signal_tag, indices,\
		filename=make_high_signal_boxplot_filename(peak_tag, signal_tag, output_id),\
		title="High signal profiles: "+str(len(indices))+" profiles",\
		ylim=clustering_info.boxplot_ylims[signal_tag],\
		make_horizontal_line_at_origin = False, make_vertical_line_in_middle = True)

	elif cluster_type == "group":
		# Find cutoffs for this group
		group_lower_bound, group_upper_bound = get_group_bounds\
		(clustering_info, peak_tag, signal_tag, group_number)

		indices = map_indices(get_assignment_indices\
		(clustering_info.group_assignments[peak_tag][signal_tag])[group_number], 
		clustering_info.high_signal[peak_tag][signal_tag])
		
		boxplot(clustering_info, peak_tag, signal_tag, indices,\
		filename=make_group_boxplot_filename(peak_tag, signal_tag, output_id, group_number),\
		title="Profiles with "+ str(int(group_by_quantile*100))+\
		"% quantile in the range "+group_lower_bound+"-"+group_upper_bound+\
		": "+str(len(indices))+" profiles"\
		+" ("+str(int(100*float(len(indices))/len(clustering_info.high_signal[peak_tag][signal_tag])))+"%)",\
		ylim=clustering_info.boxplot_ylims[signal_tag],\
		make_horizontal_line_at_origin = False, make_vertical_line_in_middle = True)
		
	elif cluster_type == "unflipped shape":
		indices = get_assignment_indices(clustering_info.shape_assignments_unflipped[peak_tag][signal_tag])[shape_number]

		if len(indices) < 4:
			return

		boxplot(clustering_info, peak_tag, signal_tag, indices,\
		filename=make_unflipped_shape_boxplot_filename(peak_tag, signal_tag, output_id, shape_number),\
		title="Unflipped shape "+str(shape_number)+": "+str(len(indices))+" profiles"\
		+" ("+str(int(100*float(len(indices))/len(clustering_info.high_signal[peak_tag][signal_tag])))+"%)",\
		ylim=normalize_ylims,\
		ylab="Signal z-score",\
		make_horizontal_line_at_origin = True, make_vertical_line_in_middle = True,\
		normalize=True)

	elif cluster_type == "oversegmented shape":
		indices = get_assignment_indices(clustering_info.shape_assignments_oversegmented[peak_tag][signal_tag])[shape_number]

		if len(indices) < 4:
			return

		boxplot(clustering_info, peak_tag, signal_tag, indices,\
		filename=make_oversegmented_shape_boxplot_filename(peak_tag, signal_tag, output_id, shape_number),\
		title="Oversegmented shape "+str(shape_number)+": "+str(len(indices))+" profiles"\
		+" ("+str(int(100*float(len(indices))/len(clustering_info.high_signal[peak_tag][signal_tag])))+"%)",\
		ylim=normalize_ylims,\
		ylab="Signal z-score",\
		make_horizontal_line_at_origin = True, make_vertical_line_in_middle = True,\
		normalize=True)

	elif cluster_type == "shape":
		indices = get_assignment_indices(clustering_info.shape_assignments[peak_tag][signal_tag])[shape_number]

		if len(indices) < 4:
			return

		flipped = filter(lambda i: i in indices, clustering_info.flipped[peak_tag][signal_tag])

		boxplot(clustering_info, peak_tag, signal_tag, indices,\
		filename=make_shape_boxplot_filename(peak_tag, signal_tag, output_id, shape_number),\
		title="Shape "+str(shape_number)+": "+str(len(indices))+" profiles"\
		+" ("+str(int(100*float(len(indices))/len(clustering_info.high_signal[peak_tag][signal_tag])))+"%)",\
		ylim=normalize_ylims,\
		ylab="Signal z-score",\
		make_horizontal_line_at_origin = True, make_vertical_line_in_middle = True,\
		flipped=flipped,\
		normalize=True)

	elif cluster_type == "grouped shape":
		group_cutoffs = clustering_info.group_cutoffs[peak_tag][signal_tag]
		group_lower_bound, group_upper_bound = get_group_bounds\
		(clustering_info, peak_tag, signal_tag, group_number)

#		shape_indices = map_indices(get_assignment_indices\
#		(clustering_info.shape_assignments[peak_tag][signal_tag])[shape_number],\
#		clustering_info.high_signal[peak_tag][signal_tag])
#		group_indices = map_indices(get_assignment_indices\
#		(clustering_info.group_assignments[peak_tag][signal_tag])[group_number],\
#		clustering_info.high_signal[peak_tag][signal_tag])
#		indices = list(set(shape_indices) & set(group_indices))
		shape_indices = get_assignment_indices(clustering_info.shape_assignments[peak_tag][signal_tag])[shape_number]
		group_indices = get_assignment_indices(clustering_info.group_assignments[peak_tag][signal_tag])[group_number]
		indices = list(set(shape_indices) & set(group_indices))

		flipped = filter(lambda i: i in indices, clustering_info.flipped[peak_tag][signal_tag])
		
		# Since we're passing normalize=False to boxplot, it expects
		# full-range indices.
		indices = map_indices(indices, clustering_info.high_signal[peak_tag][signal_tag])
		flipped = map_indices(flipped, clustering_info.high_signal[peak_tag][signal_tag])

		if len(indices) < 4:
			return
			print "not outputing figure due to too few profiles:"
			print "boxplot_simple:", shape_number, group_number, len(indices)

		boxplot(clustering_info, peak_tag, signal_tag, indices,\
		filename=make_grouped_shape_boxplot_filename(peak_tag, signal_tag, output_id, shape_number, group_number),\
		title="Shape "+str(shape_number)+", group ("+group_lower_bound+"-"+group_upper_bound+")"+\
		": "+str(len(indices))+" profiles"\
		+" ("+str(int(100*float(len(indices))/len(clustering_info.high_signal[peak_tag][signal_tag])))+"%)",\
#		title="Profiles with shape "+str(shape_number)+" and "+str(int(group_by_quantile*100))+\
#		"% quantile in the range "+group_lower_bound+"-"+group_upper_bound+\
#		": "+str(len(indices))+" profiles"\
#		+" ("+str(int(100*float(len(indices))/len(clustering_info.high_signal[peak_tag][signal_tag])))+"%)",\
		ylim=clustering_info.boxplot_ylims[signal_tag],\
		normalize=False,
		make_horizontal_line_at_origin = False, make_vertical_line_in_middle = True,\
		flipped=flipped)
		
	else:
		print "cluster_type unrecognized"
	return
	
		
	
	
	
	
	
	
	
	
	
	
	
















	
	
