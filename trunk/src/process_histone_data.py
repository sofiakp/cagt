#!/bin/python
#####################################################################
# process_histone_data.py
# Max Libbrecht
# Updated 7/10
# -------------------------------------------
# This module is reponsible for reading the histone data file,
# and doing some processing, including defining the axis names
# and removing low-signal profiles.
#####################################################################

import sys
sys.path.append('../')

import random
from math import log
import numpy as np

import rpy2.robjects as rpy
r = rpy.r


#######################################################################
# remove_noise()
# -----------------------------------------------
#	Returns a list of profile indices with significant signal.  
# The a profile is considered to have significant signal if
# its cutoff_quantile-th quantile is at least cutoff_value.
# This is valuable because low-signal profiles are generally
# just noise.
#######################################################################
def remove_noise(data, dimnames, cutoff_quantile, cutoff_value):
	ncol = data.shape[1]
	nonnoise_rows = filter(\
	lambda i: sorted(data[i,:].flat)[int(float(ncol)*cutoff_quantile)]>=cutoff_value,\
	range(data.shape[0]))
	return nonnoise_rows


#######################################################################
# get_histone_data()
# -----------------------------------------------
# Reads the passed file and converts it to an numpy matrix.
# Also creates dimnames for the data.
#######################################################################
def get_histone_data(filename):
	print "reading data file..."
	data = map(lambda row: (map(lambda x: float(x), row.split())), open(filename,"r").readlines())
	data = np.matrix(data, np.float_)
	
	colnames = 251*[""]
	colnames[125] = "center"
	colnames[105] = "-200bp"
	colnames[145] = "+200bp"
	colnames[25] = "-1000bp"
	colnames[225] = "+1000bp"

	dimnames = [map(str, range(data.shape[0])), colnames]
	return data, dimnames
	

#######################################################################
# get_filtered_histone_data()
# -----------------------------------------------
# Reads the passed file and converts it to an numpy matrix.
# Also creates dimnames for the data. In addition, filters out
# the profiles with cutoff-quantile-th quantil less than
# cutoff_value.
#######################################################################
def get_filtered_histone_data(filename, cutoff_quantile, cutoff_value):
	data, dimnames = get_histone_data(filename)
	nonnoise_rows = remove_noise(data, dimnames, cutoff_quantile, cutoff_value)
	filtered_data = data[nonnoise_rows,:]
	return filtered_data, [map(str, nonnoise_rows), dimnames[1]]
	
	
#######################################################################
# get_filtered_histone_data()
# -----------------------------------------------
#######################################################################
def normalize(data, dimnames):
	norm_data = np.zeros(data.shape)
	
	for row in range(data.shape[0]):
		std = np.std(data[row,:])
		avg = np.mean(data[row,:])
		norm_data[row,:] = (np.array(data[row,:])-avg)/std
	
	return norm_data, dimnames















