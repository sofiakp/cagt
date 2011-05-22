#!/bin/python


#import sys
#import os
import scipy as sp
from scipy.stats import hypergeom

from src.filenames import *
from src.utils import transpose
from src.analysis.mutual_information import mutual_information




#def cluster_correlate(assignments1, assignments2):
#	H1 = entropy(assignments1)
#	H2 = entropy(assignments2)
#	H_joint = mutual_entropy(assignments1, assignments2)
#	MI = mutual_information(assignments1, assignments2)
#	return (H1, H2, H_joint, MI)

def cluster_correlate(assignments1, assignments2):
	num_profiles = len(assignments1)
	assert(len(assignments1) == len(assignments2))
	clusters1 = list(set(assignments1))
	clusters2 = list(set(assignments2))

	cor = [[{} for i in range(len(clusters2))] for j in range(len(clusters1))]

	for c1 in clusters1:
		num_c1 = len(filter(lambda i: assignments1[i]==c1, range(num_profiles)))
		for c2 in clusters2:
			num_c2 = len(filter(lambda i: assignments2[i]==c2, range(num_profiles)))

			num_profiles_in_common = len(filter(lambda i:\
			assignments1[i]==c1 and assignments2[i]==c2,\
			range(num_profiles)))

			# This is the same as n=num_c2, N=num_c1
			k = num_profiles_in_common
			M = num_profiles
			n = num_c1
			N = num_c2
#			print "hypergeom:", k,M,n,N
			p = hypergeom.sf(k,M,n,N)

			cor[c1][c2]['p_val'] = p
			cor[c1][c2]['intersection'] = num_profiles_in_common
			cor[c1][c2]['num_c1'] = num_c1
			cor[c1][c2]['num_c2'] = num_c2

	return cor

def make_correlations_for_peak(clustering_info, peak_tag):

	correlations = {}
	for signal_tag in signal_tags: correlations[signal_tag] = {}

	num_peaks = clustering_info.num_peaks[peak_tag]
	for signal_tag_index1 in range(len(signal_tags)):
		for signal_tag_index2 in range(signal_tag_index1+1, len(signal_tags)):
			signal_tag1 = signal_tags[signal_tag_index1]
			signal_tag2 = signal_tags[signal_tag_index2]
			high_signal_assignments1 = clustering_info.shape_assignments_unflipped[peak_tag][signal_tag1]
			high_signal_assignments2 = clustering_info.shape_assignments_unflipped[peak_tag][signal_tag2]

			assignments1 = map_assignments(high_signal_assignments1,\
			clustering_info.high_signal[peak_tag][signal_tag1], num_peaks)
			assignments2 = map_assignments(high_signal_assignments2,\
			clustering_info.high_signal[peak_tag][signal_tag2], num_peaks)

			assert(len(assignments1)==len(assignments2))

			cor = cluster_correlate(assignments1,assignments2)
			correlations[signal_tag1][signal_tag2] = cor
			correlations[signal_tag2][signal_tag1] = transpose(cor)

	return correlations


def make_all_correlations(clustering_info):

	correlations = {} # peak_tag, signal_tag1, signal_tag2 -> correlations

	for peak_tag in peak_tags:
		print "starting correlations on", peak_tag, "..."
		t0 = time()
		num_peaks = clustering_info.num_peaks[peak_tag]
#		for signal_tag_index1 in range(len(signal_tags)):
#			for signal_tag_index2 in range(signal_tag_index1+1, len(signal_tags)):
#				signal_tag1 = signal_tags[signal_tag_index1]
#				signal_tag2 = signal_tags[signal_tag_index2]
#				high_signal_assignments1 = clustering_info.shape_assignments[peak_tag][signal_tag1]
#				high_signal_assignments2 = clustering_info.shape_assignments[peak_tag][signal_tag2]
#
#				assignments1 = map_assignments(high_signal_assignments1,\
#				clustering_info.high_signal[peak_tag][signal_tag1], num_peaks)
#				assignments2 = map_assignments(high_signal_assignments2,\
#				clustering_info.high_signal[peak_tag][signal_tag2], num_peaks)
#
#				assert(len(assignments1)==len(assignments2))

		cor = make_correlations_for_peak(clustering_info, peak_tag)
		correlations[peak_tag] = cor
		print "time to get correlations for", peak_tag, ":", time()-t0


	return correlations
