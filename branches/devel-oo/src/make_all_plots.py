
from time import time
import os
import sys
import logging
import traceback

from parameters import *
from src.filenames import *
from src.output.boxplot_simple import boxplot_simple
from src.ClusteringInfo.ClusteringInfo import clustering_info_load

# def make_all_plots(profiles_info_list):
# 	for profiles_info in profiles_info_list:
# 		make_plots_for_profile(profiles_info)

def make_plots_for_profile(profiles_info):
	try:
		t0 = time()
		if not os.path.isfile(make_plots_done_filename(profiles_info)):
			clustering_info = clustering_info_load(profiles_info)
			clustering_info.make_PD()
			make_plots_for_pair(clustering_info)
			clustering_info.free_PD()
			open(make_plots_done_filename(profiles_info),"w").close() # make a file with nothing in it
		else:
			print "skipping making plots for:", profiles_info
	except Exception,error:
		logging.error("Hit error in make_plots_for_profile")
		logging.error("profiles_info: %s", str(profiles_info))
		logging.error(str(error))
		logging.error(traceback.format_exc())
		print "HIT ERROR WHILE MAKING PLOTS FOR", profiles_info, " -- SKIPPING"
		traceback.print_exc()
		print "Skipping this set of profiles"
		print "See logs for details"




def make_plots_for_pair(clustering_info):
	# if not os.path.isdir(make_aggregation_plots_foldername(peak_tag, signal_tag, clustering_info.output_id)):
#		print "making folder:", make_aggregation_plots_foldername(peak_tag, signal_tag, clustering_info.output_id)
		# os.mkdir(make_aggregation_plots_foldername(peak_tag, signal_tag, clustering_info.output_id))
		# assert(os.path.isdir(make_aggregation_plots_foldername(peak_tag, signal_tag, clustering_info.output_id)))
	
	boxplot_simple(clustering_info, "all")
	boxplot_simple(clustering_info, "low_signal")
	boxplot_simple(clustering_info, "high_signal")
	shape_clusters = range(len(clustering_info.shape_clusters))
	shape_clusters_unflipped = range(len(clustering_info.shape_clusters_unflipped))
	shape_clusters_oversegmented = range(len(clustering_info.shape_clusters_oversegmented))
		
	group_clusters = range(len(clustering_info.group_clusters))
	for shape_cluster in shape_clusters:
		boxplot_simple(clustering_info, "shape_cluster", shape_number=shape_cluster)
	for group_cluster in group_clusters:
		boxplot_simple(clustering_info, "magnitude_group", group_number=group_cluster)
	for shape_cluster in shape_clusters:
		for group_cluster in group_clusters:
			boxplot_simple(clustering_info, "grouped_shape", shape_number=shape_cluster, group_number=group_cluster)
	for shape_cluster in shape_clusters_unflipped:
		boxplot_simple(clustering_info, "shape_cluster_unflipped", shape_number=shape_cluster)
	for shape_cluster in shape_clusters_oversegmented:
		boxplot_simple(clustering_info, "shape_cluster_oversegmented", shape_number=shape_cluster)
			
