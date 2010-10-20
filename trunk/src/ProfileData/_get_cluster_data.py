#!/bin/python
#####################################################################
# get_cluster_data.py
# Max Libbrecht
# Updated 7/10
#####################################################################

import sys
sys.path.append('../../')
import numpy as np

#####################################################################
# get_cluster_data()
# ----------------------------------------------
# Takes the full set of histone data and a cluser assignment. 
# The assignment argument should have the format returned by the 
# clustering algorithms: data point i is assigned to 
# cluster number assigmennts[i].  
# 
# Returns a list of clusters, where each cluster has only
# the data points associated with it.  Returns the indices 
# associated with the cluster and the cluster's dimnames 
# likewise.
#####################################################################
def get_cluster_data(data, dimnames, assignments):
	nclusters = len(list(set(assignments)))
	nrow = data.shape[0]
	cluster_indices = map(lambda cluster: \
	np.array(filter(lambda i: assignments[i]==cluster, range(nrow))), \
	range(nclusters))
	
#	cluster_data = map(lambda cluster: data[cluster,:], cluster_indices)
	cluster_data = []
	for cluster in cluster_indices:
#		data[cluster,:]
		cluster_data.append(data[cluster,:])
	
	cluster_dimnames = map(lambda i:\
	[map(str, cluster_indices[i]), dimnames[1]],\
	range(nclusters))
	
	return cluster_data, cluster_indices, cluster_dimnames
