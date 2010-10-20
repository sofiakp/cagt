#!/bin/python

import numpy as np
import itertools

import sys
sys.path.append('../../')

from parameters import *
from src.utils import *


def assign_to_group(val, cutoffs):
	group = 0
	for cutoff in cutoffs:
		if val <= cutoff:
			break
		group += 1
	return group


def group_by_magnitude(clustering_info, peak_tag, signal_tag):
	data = clustering_info.PDs[peak_tag][signal_tag].data\
	[clustering_info.high_signal[peak_tag][signal_tag]]
	quantiles = map(lambda i: quantile(np.array(data[i,].flat), group_by_quantile),\
	range(data.shape[0]))
	
	lower_bound = sorted(quantiles)[int(len(quantiles)*group_quantile_bounds[0])]
	upper_bound = sorted(quantiles)[int(len(quantiles)*group_quantile_bounds[1])]
	
	rng = upper_bound-lower_bound
	cutoffs = map(lambda i: lower_bound+rng*i/(num_groups+1), range(1,num_groups))
	clustering_info.group_cutoffs[peak_tag][signal_tag] = cutoffs

	clustering_info.group_assignments[peak_tag][signal_tag] =\
	map(assign_to_group, quantiles,\
	itertools.repeat(cutoffs,len(quantiles)))
	
	return