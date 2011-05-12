
from time import time
import numpy as np
from numpy import corrcoef
from math import sqrt


from src.utils import *
from src.analysis.k_cluster import k_cluster
from src.analysis.hcluster import hcluster



def cluster_then_merge(clustering_info):
	num_groups = clustering_info.profiles_info.args.num_groups
	args = clustering_info.profiles_info.args
	norm_data = clustering_info.PD.high_signal_norm_data
	if len(norm_data.ids) < 5:
		clustering_info.group_cutoffs = [0.0]*num_groups
		clustering_info.shape_clusters = [0]*len(norm_data.ids)
		clustering_info.shape_clusters_unflipped = [0]*len(norm_data.ids)
		clustering_info.shape_clusters_oversegmented = [0]*len(norm_data.ids)
		clustering_info.flipped = [False]*len(norm_data.ids)
		return


	t0 = time()
	oversegmented_assignments = k_cluster(norm_data, num_clusters=args.cluster_then_merge_num_clusters, npass=args.npass, args=args)
	oversegmented_clusters = assignments_to_clusters(oversegmented_assignments, norm_data.ids)
	clustering_info.shape_clusters_oversegmented = oversegmented_clusters

	t1 = time()
	unflipped_clusters, tmp = hcluster(norm_data, oversegmented_clusters, args, flipping=False)
	clustering_info.shape_clusters_unflipped = unflipped_clusters

	if clustering_info.profiles_info.flip:
		flipped_clusters, flipped = hcluster(norm_data, unflipped_clusters, args, flipping=True)
		clustering_info.shape_clusters = flipped_clusters
		clustering_info.flipped = flipped
	else:
		clustering_info.shape_cluster = unflipped_clusters
		clustering_info.flipped = []

	print "number of clusters after merging:", len(flipped_clusters)









