#!/bin/python

import numpy as np
import itertools

import sys
sys.path.append('../../')

from src.utils import *


def assign_to_group(val, cutoffs):
	group = 0
	for cutoff in cutoffs:
		if val <= cutoff:
			break
		group += 1
	return group


def group_by_magnitude(clustering_info):
	num_groups = clustering_info.profiles_info.args.num_groups
	group_by_quantile = clustering_info.profiles_info.args.group_by_quantile
	group_quantile_bounds = [clustering_info.profiles_info.args.group_quantile_lower_bound, clustering_info.profiles_info.args.group_quantile_upper_bound]
	group_quantile_lower_bound = clustering_info.profiles_info.args.group_quantile_lower_bound
	group_quantile_upper_bound = clustering_info.profiles_info.args.group_quantile_upper_bound
	data = clustering_info.PD.high_signal_data
	if len(data.ids) < 5:
		clustering_info.group_cutoffs = [0.0]*num_groups
		clustering_info.group_clusters = [0]*len(data.ids)
		return

	quantiles = map(lambda id: quantile(np.array(data.get_row(id)), group_by_quantile),\
	data.ids)

	lower_bound = sorted(quantiles)[int(len(quantiles)*group_quantile_bounds[0])]
	upper_bound = sorted(quantiles)[int(len(quantiles)*group_quantile_bounds[1])]

	rng = upper_bound-lower_bound
	cutoffs = map(lambda i: lower_bound+rng*i/(num_groups+1), range(1,num_groups))
	clustering_info.group_cutoffs = cutoffs

	clustering_info.group_clusters =\
	assignments_to_clusters(map(assign_to_group, quantiles,\
	itertools.repeat(cutoffs,len(quantiles))), data.ids)

	return
