
import sys
sys.path.append('../')

import numpy as np
import itertools
import pickle

from src.k_cluster import k_cluster
from src.process_histone_data import remove_noise
from src.get_cluster_data import get_cluster_data

import matplotlib.pyplot as plt

# from http://docs.python.org/library/itertools.html
def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)


def quantile(arr, q):
	return sorted(arr)[int(len(arr)*q)]

def assign_to_group(val, cutoffs):
	group = 0
	for cutoff in cutoffs:
		if val <= cutoff:
			break
		group += 1
	return group

def ts_cluster(data, dimnames, num_groups, clusters_per_group,\
cutoff_quantile, npass):
#def ts_cluster(data, dimnames, nclusters_stage1, nclusters_stage2, npass,\
#cutoff_quantile, cutoff_value, ):

	####################################
	# First stage:
	# Split clusters by the value of the 
	# cutoff_quantile-th quantile.
	####################################

	quantiles = map(lambda i: quantile(np.array(data[i,].flat), cutoff_quantile),\
	range(data.shape[0]))
	
	# get .05-.95 range of quantiles
	lower_bound = sorted(quantiles)[int(len(quantiles)*.01)]
	upper_bound = sorted(quantiles)[int(len(quantiles)*.99)]
	print lower_bound,upper_bound

	rng = upper_bound-lower_bound
	cutoffs = map(lambda i: lower_bound+rng*i/(num_groups+1), range(1,num_groups))


	group_assignments = map(assign_to_group, quantiles,\
	itertools.repeat(cutoffs,len(quantiles)))
	
	group_data, group_indices, group_dimnames = \
	get_cluster_data(data, dimnames, group_assignments)
	
	print map(len, group_data)
	print cutoffs
		
	####################################
	# Second stage:
	# Cluster using correlation
	####################################
	group_cluster_assignments = [None]*num_groups
	for group in range(num_groups):
		group_cluster_assignments[group] = \
		map(lambda assignment: assignment+group*clusters_per_group,\
		k_cluster(group_data[group], group_dimnames[group],\
		nclusters=clusters_per_group, npass=npass, dist='c')\
		)
	
	
	assignments = np.zeros(data.shape[0])
	for group in range(num_groups):
		assignments[group_indices[group]] = group_cluster_assignments[group]
	
	return assignments


#	nonnoise_rows = remove_noise(data, dimnames, cutoff_quantile, cutoff_value)
#	nonnoise_data = data[nonnoise_rows:]
#	nonnoise_dimnames = [np.array(dimnames[0])[nonnoise_rows],dimnames[1]]
#
#	nonnoise_assignments = k_cluster(data, dimnames, nclusters_stage1, npass, dist='e')

	# Set all the nonnoise rows to their respective cluster,
	# and set all the noise rows cluster nclusters_stage1
	# (such that there are nclusters_stage1+1 clusters total)
#	assignments = np.array([nclusters_stage1]*data.shape[0])
#	assignments[nonnoise_rows] = nonnoise_assignments
#
#	cluster1_data, cluster1_indices, cluster1_dimnames = \
#	get_cluster_data(data, dimnames, assignments)

	