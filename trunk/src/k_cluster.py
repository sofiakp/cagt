#!/bin/python
#####################################################################
# k_cluster.py
# Max Libbrecht
# Updated 7/10
#####################################################################


import rpy2.robjects as rpy
r = rpy.r

import sys
sys.path.append('../')


import numpy as np
from rpy_matrix_conversion import *
from Pycluster import kcluster

from time import time
from random import random

import pickle


#######################################################################
# k_cluster()
# -----------------------------------------------
# Uses kcluster from the Pycluster module to cluster the cluster the data.
#######################################################################
def k_cluster(data, dimnames, nclusters, npass, dist='e'):
	assignments, error, nfound = kcluster(data, nclusters=nclusters, method='m', dist=dist, npass=npass)
	return assignments
		
	
#######################################################################
# k_cluster_bin() - deprecated
#######################################################################
#def k_cluster_bin(data, dimnames, nclusters, npass, num_bins):
#	bin_data, bin_dimnames = bin(data, dimnames, num_bins)
#	return k_cluster(bin_data, bin_dimnames, nclusters, npass)
