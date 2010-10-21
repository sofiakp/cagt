#!/bin/python

def get_assignment_indices(clustering_info, peak_tag, signal_tag, assignments):
	num_clusters = len(list(set(assignments)))
	num_profiles = len(assignments)
	high_signal = clustering_info.high_signal[peak_tag][signal_tag]
	return map(lambda cluster:\
	map_indices\
	(np.array(filter(lambda i: assignments[i]==cluster, range(num_profiles))),\
	high_signal), \
	range(num_clusters))
	
