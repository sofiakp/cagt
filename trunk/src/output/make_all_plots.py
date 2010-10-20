
from time import time
import os

from parameters import *
from src.filenames import *
from src.output.boxplot_simple import boxplot_simple


def make_all_plots(clustering_info):
	for peak_tag in peak_tags:
		for signal_tag in signal_tags:
			t0 = time()
			print "------------------------------------------"
			print "making plots for", peak_tag, signal_tag, "..."
			clustering_info.make_PD(peak_tag, signal_tag)
			make_plots_for_pair(clustering_info, signal_tag=signal_tag, peak_tag=peak_tag)
			clustering_info.free_PD(peak_tag, signal_tag)
			print "time to make all plots for:", signal_tag, "around", peak_tag, ":", time()-t0
#		make_correlations_for_peak(peak_tag, clustering_info)

def make_plots_for_pair(clustering_info, peak_tag, signal_tag):
	if not os.path.isdir(make_aggregation_plots_foldername(peak_tag, signal_tag, clustering_info.output_id)):
#		print "making folder:", make_aggregation_plots_foldername(peak_tag, signal_tag, clustering_info.output_id)
		os.mkdir(make_aggregation_plots_foldername(peak_tag, signal_tag, clustering_info.output_id))
		assert(os.path.isdir(make_aggregation_plots_foldername(peak_tag, signal_tag, clustering_info.output_id)))
	
	boxplot_simple(clustering_info, peak_tag, signal_tag, "all")
	boxplot_simple(clustering_info, peak_tag, signal_tag, "low signal")
	boxplot_simple(clustering_info, peak_tag, signal_tag, "high signal")
	shape_clusters = list(set(clustering_info.shape_assignments[peak_tag][signal_tag]))
	shape_clusters_unflipped = list(set(clustering_info.shape_assignments_unflipped[peak_tag][signal_tag]))
	shape_clusters_oversegmented = list(set(clustering_info.shape_assignments_oversegmented[peak_tag][signal_tag]))
	group_clusters = list(set(clustering_info.group_assignments[peak_tag][signal_tag]))
	for shape_cluster in range(len(shape_clusters)):
		boxplot_simple(clustering_info, peak_tag, signal_tag,\
		"shape", shape_number=shape_cluster)
	for group_cluster in range(len(group_clusters)):
		boxplot_simple(clustering_info, peak_tag, signal_tag,\
		"group", group_number=group_cluster)
	for shape_cluster in range(len(shape_clusters)):
		for group_cluster in range(len(group_clusters)):
			boxplot_simple(clustering_info, peak_tag, signal_tag,\
			"grouped shape", shape_number=shape_cluster, group_number=group_cluster)
	for shape_cluster in range(len(shape_clusters_unflipped)):
		boxplot_simple(clustering_info, peak_tag, signal_tag,\
		"unflipped shape", shape_number=shape_cluster)
	for shape_cluster in range(len(shape_clusters_oversegmented)):
		boxplot_simple(clustering_info, peak_tag, signal_tag,\
		"oversegmented shape", shape_number=shape_cluster)
			
