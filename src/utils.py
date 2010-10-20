
import numpy as np

import rpy2.robjects as rpy
r = rpy.r

def opposite_indices(cluster_info, peak_tag, signal_tag, indices):
	return filter(lambda i: i not in indices,\
	range(cluster_info.num_peaks[peak_tag]))

def map_indices(indices, mapping):
	return map(lambda i: mapping[i], indices)
	
def find_in_list(list, item):
	for i in range(len(list)):
		if list[i] == item:
			return i
	print "find_in_list: not found!"
	return None

def map_indices_backwards(indices, mapping):
	return map(lambda i: find_in_list(mapping, i), indices)
	
def map_assignments(assignments, mapping, num_peaks):
	mapped_assignments = [-1]*num_peaks
	for i in range(len(assignments)):
		mapped_assignments[mapping[i]] = assignments[i]
	return mapped_assignments

def quantile(arr, q):
	return sorted(arr)[int(len(arr)*q)]

def transpose(m):
	return map(list,zip(*m))

def get_assignment_indices(assignments):
	clusters = sorted(list(set(assignments)))
#	num_clusters = len(list(set(assignments)))
	num_profiles = len(assignments)
	return map(lambda cluster: \
	np.array(filter(lambda i: assignments[i]==cluster, range(num_profiles))), \
#	range(num_clusters))
	clusters)

def index_r_data(r_data, indices):
	# R is 1-indexed
	r_indices = rpy.IntVector(map(lambda x:x+1, indices))
	rpy.globalenv['indices'] = r_indices
	rpy.globalenv['data'] = r_data
	return r('data[indices,]')
