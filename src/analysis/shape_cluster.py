#!/bin/python
#####################################################################
# k_cluster.py
# Max Libbrecht
# Updated 7/10
#####################################################################



import sys
sys.path.append('../../')

from src.utils import *

from src.analysis.k_cluster import k_cluster

def shape_cluster(clustering_info, peak_tag, signal_tag):
    shape_num_clusters = clustering_info.profiles_info.args.shape_num_clusters
	norm_data = clustering_info.PDs[peak_tag][signal_tag].high_signal_norm_data

	assignments = k_cluster(norm_data, num_clusters=shape_num_clusters)
#	assignments = map_indices(norm_data_assignments,\
#	clustering_info.high_signal[peak_tag][signal_tag])

	clustering_info.shape_assignments[peak_tag][signal_tag] = assignments
	clustering_info.flipped[peak_tag][signal_tag] = []
