
import pickle

from src.filenames import *
from src.mutual_information import mutual_information as find_mutual_information

def pairwise_cluster_all(clustering_info):

	pairwise_clustering_info = ClusteringInfo()
	pairwise_clustering_info.output_id = clustering_info.output_id
	pairwise_clustering_info.peaks = clustering_info.peaks
	pairwise_clustering_info.num_peaks = clustering_info.num_peaks


	significant_pairs = {}
	for peak_tag in peak_tags: significant_pairs[peak_tag] = []

	# Make mutual entropy matrix
	mutual_information = {}
	for peak_tag in peak_tags:
		mutual_information[peak_tag] = {}
		# add signal tag entry for each one
		for signal_tag in signal_tags:
		  mutual_information[signal_tag] = {}

		for signal_tag_index1 in range(len(signal_tags)):
			signal_tag1 = signal_tags[signal_tag_index1]
			for signal_tag2 in range(signal_tag_index1+1,len(signal_tags)):
				signal_tag2 = signal_tags[signal_tag_index2]
				MI = find_mutual_information\
				(clustering_info.unflipped_shape_assignments[peak_tag][signal_tag1],\
				clustering_info.unflipped_shape_assignments[peak_tag][signal_tag2])
				mutual_information[signal_tag1][signal_tag2] = MI
				mutual_information[signal_tag2][signal_tag1] = MI
				if MI > pairwise_cluster_mutual_information_cutoff:
					significant_pairs[peak_tag].append([signal_tag1, signal_tag2])

	# For each highly mutually informative pair, do clustering
	for peak_tag in peak_tags:
		for significant_pair in significant_pairs[peak_tag]:
			signal_tag1 = significant_pair[0]
			signal_tag2 = significant_pair[1]

			pairwise_cluster_pair(clustering_info, pairwise_clustering_info,\
			peak_tag, signal_tag1, signal_tag2)


def pairwise_cluster_pair(clustering_info, pairwise_clustering_info,\
peak_tag, signal_tag1, signal_tag2):

	paired_signal_tag = signal_tag1 + '+' + signal_tag2

	pairwise_clustering_info.PDs[peak_tag][paired_signal_tag] = None
	group_by_magnitude(pairwise_clustering_info, clustering_info, peak_tag, paired_signal_tag)
	cluster_then_merge(pairwise_clustering_info, clustering_info, peak_tag, paired_signal_tag)
	del pairwise_clustering_info.PDs[peak_tag][paired_signal_tag]

	#












