
from time import time
import numpy as np
from numpy import corrcoef
from math import sqrt


from parameters import *
from src.utils import get_assignment_indices
from src.analysis.k_cluster import k_cluster

def medians(data):
	return np.apply_along_axis(lambda col: sorted(col)[int(len(col)*0.5)], 0, data)

def euc(profile1, profile2):
	dist = 0.0
	for i in range(len(profile1)):
		dist += (profile1[i]-profile2[i])**2
	return sqrt(dist) / len(profile1)

def correlation_with_flipping(profile1, profile2):
	cors = []
	cors.append((False,False,corrcoef(profile1,profile2)[0][1]))
	cors.append((True,False,corrcoef(profile1[::-1],profile2)[0][1]))
	cors = sorted(cors, cmp=lambda x,y: -cmp(x[2],y[2]))
	return cors[0]



def merge_clusters(norm_data, clustering_assignments, flipping=False):
	t1 = time()
	cluster_indices = get_assignment_indices(clustering_assignments)
	cluster_medians = map(lambda indices: medians(norm_data[indices,:]), cluster_indices)
	flipped = set()
		
	t5 = time()
	# We're going to re-impliment heirarchical clustering here.
	# It's frustrating, but since we want to change all the clusters
	# after each pass, I don't think we can use any of the packages.
	# We won't do it very efficiently, but it doesn't matter since there 
	# aren't too many clusters,
	while True:
		if len(cluster_indices) <= 1:
			break
		pairs = []
		for cluster1 in range(len(cluster_indices)):
			for cluster2 in range(cluster1+1, len(cluster_indices)):
				pair = {}
				pair['c1'] = cluster1
				pair['c2'] = cluster2

				if flipping:
					pair['c1_flipped'], pair['c2_flipped'], pair['cor'] =\
					correlation_with_flipping(cluster_medians[cluster1],cluster_medians[cluster2])
				else:
					pair['c1_flipped'] = False
					pair['c2_flipped'] = False
					pair['cor'] = corrcoef(cluster_medians[cluster1],cluster_medians[cluster2])[0][1]
				
				pairs.append(pair)
		
		pairs = sorted(pairs, cmp=lambda x,y: -cmp(x['cor'],y['cor']))
		
		if len(pairs) < 1:
			break
		if pairs[0]['cor'] < cluster_merge_correlation_cutoff:
			break
		
		c1 = pairs[0]['c1']
		c2 = pairs[0]['c2']
		new_cluster_indices = np.concatenate((cluster_indices[c1], cluster_indices[c2]))
		new_cluster_medians = medians(norm_data[new_cluster_indices,:])
		
		if pairs[0]['c1_flipped']:
			for i in cluster_indices[c1]:
				if i in flipped:
					flipped -= set([i])
				else:
					flipped |= set([i])
		if pairs[0]['c2_flipped']:
			for i in cluster_indices[c2]:
				if i in flipped:
					flipped -= set([i])
				else:
					flipped |= set([i])
		
		# Since we're deleting out of a list, we have to make sure to delete
		# the higher-index element first
		# Also, after this point, all of our indices into these lists are invalid
		del cluster_indices[c2]
		del cluster_indices[c1]
		del cluster_medians[c2]
		del cluster_medians[c1]
		
		cluster_indices.append(new_cluster_indices)
		cluster_medians.append(new_cluster_medians)
	
	
	# Sort clusters in ascending order of size
	sizes = map(lambda i: [i,len(cluster_indices[i])], range(len(cluster_indices)))
	cluster_order = map(lambda x: x[0], sorted(sizes, cmp=lambda x,y: -cmp(x[1],y[1])))
	
	new_assignments = [None]*len(clustering_assignments)
	for cluster in range(len(cluster_order)):
		for i in cluster_indices[cluster_order[cluster]]:
			new_assignments[i] = cluster
	
	return new_assignments, sorted(list(flipped))



def cluster_then_merge(clustering_info, peak_tag, signal_tag):
	print "starting cluster_then_merge..."
	norm_data = clustering_info.PDs[peak_tag][signal_tag].high_signal_norm_data
	
	print "clustering..."
	t0 = time()
	oversegmented_assignments = k_cluster(norm_data, num_clusters=cluster_then_merge_num_clusters)
	print "time to cluster:", time()-t0

	clustering_info.shape_assignments_oversegmented[peak_tag][signal_tag] = oversegmented_assignments

	assignments_unflipped, tmp = merge_clusters(norm_data, oversegmented_assignments, flipping=False)
	clustering_info.shape_assignments_unflipped[peak_tag][signal_tag] = assignments_unflipped
	
	assignments_flipped, flipped = merge_clusters(norm_data, assignments_unflipped, flipping=True)
	clustering_info.shape_assignments[peak_tag][signal_tag] = assignments_flipped
	clustering_info.flipped[peak_tag][signal_tag] = flipped
	
	print "time to merge clusters:", time()-t0
	print "number of clusters after merging:", len(list(set(assignments_flipped)))

	
	
	
	
	
	
	
	