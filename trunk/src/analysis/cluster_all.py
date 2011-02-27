
from time import time
import os

from parameters import *
from src.filenames import *
from src.ClusteringInfo.ClusteringInfo import *
from src.analysis.group_by_magnitude import group_by_magnitude
from src.analysis.cluster_then_merge import cluster_then_merge


def cluster_profile(profiles_info):
	try:
		t0 = time()
		if not os.path.isdir(make_profiles_foldername(profiles_info)):
			os.mkdir(make_profiles_foldername(profiles_info))
		if os.path.isfile(make_clustering_info_dump_filename(profiles_info)):
			print "skipping", profiles_info
			return
		clustering_info = ClusteringInfo(profiles_info)
		clustering_info.make_PD()
		group_by_magnitude(clustering_info)
		cluster_then_merge(clustering_info)
		clustering_info.free_PD()
		clustering_info_dump(clustering_info)
	except Exception,error:
		logging.error("Hit error in make_plots_for_profile")
		logging.error("profiles_info: %s", str(profiles_info))
		logging.error(str(error))
		logging.error(traceback.format_exc())
		print "HIT ERROR WHILE MAKING PLOTS FOR", profiles_info, " -- SKIPPING"
		traceback.print_exc()
		print "Skipping this set of profiles"
		print "See logs for details"

def cluster_profile_pair(profiles_info_pair):
	try:
		t0 = time()
		if not os.path.isdir(make_profiles_pair_foldername(profiles_info_pair)):
			os.mkdir(make_profiles_pair_foldername(profiles_info_pair))
		if os.path.isfile(make_clustering_info_dump_filename(profiles_info_pair)):
			print "skipping", profiles_info_pair
			return
		clustering_info = ClusteringInfo(profiles_info_pair)
		clustering_info.make_PD()
		group_by_magnitude(clustering_info)
		cluster_then_merge(clustering_info)
		clustering_info.free_PD()
		clustering_info_dump(clustering_info)
	except Exception,error:
		print "HIT ERROR:", error, " WHILE CLUSTERING", profiles_info, " -- SKIPPING"
	

# def cluster_all(profiles_info_list):
# 	for profiles_info in profiles_info_list:
# 		cluster_profile(profiles_info)

# def cluster_all(clustering_info):
# 	for peak_tag in peak_tags:
# 		for signal_tag in signal_tags:
# 			if clustering_info.shape_assignments[peak_tag].has_key(signal_tag) and\
# 				 clustering_info.group_assignments[peak_tag].has_key(signal_tag):
# 				print "skipping", peak_tag, signal_tag
# 				continue
# 			print "----------------------------"
# 			print "starting", peak_tag, signal_tag, "..."
# 			t0 = time()
# 			clustering_info.make_PD(peak_tag, signal_tag)
# 			group_by_magnitude(clustering_info, peak_tag, signal_tag)
# 			cluster_then_merge(clustering_info, peak_tag, signal_tag)
# 			clustering_info.free_PD(peak_tag, signal_tag)
# 			print "time to cluster", peak_tag, signal_tag, ":", time()-t0
