import numpy as np
from numpy import corrcoef
from math import sqrt
from copy import deepcopy
from time import time

from src.utils import get_assignment_indices


def medians(data):
	return np.apply_along_axis(lambda col: sorted(col)[int(len(col)*0.5)], 0, data.data)

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


def hcluster(norm_data, clusters, args, flipping=False):
	cluster_merge_correlation_cutoff = args.cluster_merge_correlation_cutoff
	t1 = time()
	# clusters = get_assignment_indices(clustering_assignments)
	cluster_medians = map(lambda ids: medians(norm_data.get_rows(ids)), clusters)
	flipped = set()

	clusters = deepcopy(clusters)

	t5 = time()
	# We're going to re-impliment heirarchical clustering here.
	# It's frustrating, but since we want to change all the clusters
	# after each pass, I don't think we can use any of the packages.
	# We won't do it very efficiently, but it doesn't matter since there
	# aren't too many clusters at this point.
	while True:
		if len(clusters) <= 1:
			break
		pairs = []
		for cluster1 in range(len(clusters)):
			for cluster2 in range(cluster1+1, len(clusters)):
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
		new_cluster = clusters[c1] + clusters[c2]
		new_cluster_medians = medians(norm_data.get_rows(new_cluster))

		if pairs[0]['c1_flipped']:
			for i in clusters[c1]:
				if i in flipped:
					flipped -= set([i])
				else:
					flipped |= set([i])
		if pairs[0]['c2_flipped']:
			for i in clusters[c2]:
				if i in flipped:
					flipped -= set([i])
				else:
					flipped |= set([i])

		# Since we're deleting out of a list, we have to make sure to delete
		# the higher-index element first
		# Also, after this point, all of our indices into these lists are invalid
		del clusters[c2]
		del clusters[c1]
		del cluster_medians[c2]
		del cluster_medians[c1]


		clusters.append(new_cluster)
		cluster_medians.append(new_cluster_medians)


	# Flip clusters so the higher-magnitude side is on the right
	for i in range(len(clusters)):
		cluster_medians = medians(norm_data.get_rows(clusters[i]))
		midpoint = int(len(cluster_medians)/2)
		left_magnitude = sum(cluster_medians[:midpoint])/len(cluster_medians[:midpoint])
		right_magnitude = sum(cluster_medians[midpoint:])/len(cluster_medians[midpoint:])
		if left_magnitude > right_magnitude:
			flipped = flipped.symmetric_difference(set(clusters[i]))


	# Sort clusters in descending order of size
	clusters = sorted(clusters, cmp=lambda x,y: -cmp(len(x),len(y)))

	return clusters, sorted(list(flipped))
