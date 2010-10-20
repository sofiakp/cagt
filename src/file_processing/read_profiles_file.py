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
sys.path.append('../../')

import random
import array
from math import log
import numpy as np

import rpy2.robjects as rpy
r = rpy.r


#######################################################################
# get_histone_data()
# -----------------------------------------------
# Reads the passed file and converts it to an numpy matrix.
# Also creates dimnames for the data.
#######################################################################
def read_profiles_file(filename):
	print "reading data file..."
	
	file = open(filename, "r")

	raw_data = []
	peaks = []
#	rownames = []
	for line in file:
		chr = line.split()[0]
		start = int(line.split()[1])
		stop = int(line.split()[2])
#		rownames.append(chr+" "+str((start+stop)/2))
		peaks.append([chr, (start+stop)/2])
		vals = array.array('f', map(lambda x: float(x), line.split()[3].split(',')))
		raw_data.append(vals)
	
#	data = np.matrix(raw_data)
	data = np.array(raw_data)
	
	return data, peaks
	













