
from time import time

from parameters import *
from src.analysis.group_by_magnitude import group_by_magnitude
from src.analysis.cluster_then_merge import cluster_then_merge

def cluster_all(clustering_info):
	for peak_tag in peak_tags:
		for signal_tag in signal_tags:
			if clustering_info.shape_assignments[peak_tag].has_key(signal_tag) and\
				 clustering_info.group_assignments[peak_tag].has_key(signal_tag):
				print "skipping", peak_tag, signal_tag
				continue
			print "----------------------------"
			print "starting", peak_tag, signal_tag, "..."
			t0 = time()
			clustering_info.make_PD(peak_tag, signal_tag)
			group_by_magnitude(clustering_info, peak_tag, signal_tag)
			cluster_then_merge(clustering_info, peak_tag, signal_tag)
			clustering_info.free_PD(peak_tag, signal_tag)
			print "time to cluster", peak_tag, signal_tag, ":", time()-t0
