#!/bin/python
#####################################################################
# k_cluster.py
# Max Libbrecht
# Updated 7/10
#####################################################################



import sys
sys.path.append('../../')

from parameters import *

from Pycluster import kcluster

#######################################################################
# k_cluster()
# -----------------------------------------------
# Simple wrapper on the kcluster function
#######################################################################
def k_cluster(data, num_clusters, npass=npass, dist='c'):
	# It doesn't make sense to cluster less than nclusters profiles
	assert(data.shape[0] > 0)
	if data.shape[0] < num_clusters:
		return range(data.shape[0])
	assignments, error, nfound = kcluster(data, nclusters=num_clusters, method='m', dist=dist, npass=npass)
	
	# It happens occasionally that one of the clusters is empty
	# In that case, we'll remap the assignments so that there aren't
	# any gaps in the cluster numbers
	if len(list(set(assignments))) < num_clusters:
		allocated_numbers = list(set(assignments))
		reverse_map = {}
		for i in range(len(allocated_numbers)):
			reverse_map[allocated_numbers[i]] = i
		assignments = map(lambda x: reverse_map[x], allocated_numbers)
	
	return assignments
		
	