#!/bin/python
# make_profiles.py

# todo: comment

import sys
sys.path.append('../../')

import gzip 
import pickle
import array
from math import log

from time import time

from parameters import *
from src.file_processing.find_peak_centers import find_peak_centers
from src.file_processing.build_bed_file_map import build_bed_file_map

def bin_block(block, bin_size):
	binned_block = array.array('f')
	for i in range(len(block)/bin_size):
		if len(block) > bin_size*i:
			binned_block.append(sum(block[i*bin_size:(i+1)*bin_size])/bin_size)
		else:
			binned_block.append(sum(block[i*bin_size:])/len(block[i*bin_size:]))
	return binned_block



def make_profiles(peaks, data_filename, data_file_map, map_resolution, profiles_filename):
	data_file = open(data_filename, "r")
		
#	peaks = find_peak_centers(peak_filename, peak_gz)
#	print "num peaks:", sum(map(lambda chr: len(peaks[chr]), peaks.keys()))
	
	profiles_file = open(profiles_filename, "w")
	
#	print "making file map..."
#	t0 = time()
#	map_filename = "../tmp/file_map.pickle"
#	build_bed_file_map(data_filename, MAP_RESOLUTION, map_filename)
#	file_map = pickle.load(open(map_filename,"r"))
#	print "time to make file map:", time()-t0
	
#	print "finding peaks..."
#	n = 0
	t = time()
#	for peak_chr in peaks.keys():
#		print peak_chr,
#		sys.stdout.flush()
#	for peak_loc in peaks[peak_chr]:
	last_chr = ""
	for peak_loc in peaks:
		peak_chr = peak_loc[0]
		peak = peak_loc[1]
		if last_chr != peak_chr:
			print peak_chr,
			sys.stdout.flush()
		last_chr = peak_chr
		
		profile_start = peak - profile_window_size
		profile_end = peak + profile_window_size
		profile_data = array.array('f')
		t4 = time()
		last_pos = data_file.tell()
		next_pos = data_file_map[peak_chr][profile_start/map_resolution]
		data_file.seek(data_file_map[peak_chr][profile_start/map_resolution])
											
		t1 = time()
		while True:
			looking_for_start = profile_start+len(profile_data)
			line = data_file.readline()
			if len(line.split()) < 4:
#					print "peak occurs after the end of the chromosome:", peak_chr, peak
				profile_data.extend([0]*(profile_end-looking_for_start))
				break
			chr = line.split()[0]
			start = int(line.split()[1])
			end = int(line.split()[2])
			val = float(line.split()[3])
			
			if peak_chr != chr:
				print "peak occurs after the end of the chromosome:", peak_chr, peak
				profile_data.extend([0]*(profile_end-looking_for_start))
				break
			if peak_chr == chr and looking_for_start < end:
				if looking_for_start < start:
					# missing data, fill with 0's
					if profile_end < start:
						profile_data.extend([0]*(profile_end-looking_for_start))
						break
					else:
						profile_data.extend([0]*(start-looking_for_start))
						looking_for_start = profile_start+len(profile_data)
				if profile_end < end:
					profile_data.extend([val]*(profile_end-looking_for_start))
					break
				else:
					profile_data.extend([val]*(end-looking_for_start))
		
		
		t2 = time()
		binned_profile = bin_block(profile_data, profile_bin_size)
		assert(len(profile_data)==profile_end-profile_start)
		profiles_file.write(peak_chr)
		profiles_file.write("\t")
		profiles_file.write(str(profile_start))
		profiles_file.write("\t")
		profiles_file.write(str(profile_end))
		profiles_file.write("\t")
		for i in range(len(binned_profile)):
			if i != 0: profiles_file.write(',')
			profiles_file.write(str(binned_profile[i]))
		profiles_file.write("\n")
#			print "time to write file:", time()-t2
	profiles_file.close()
	print ""
	return
	


#if __name__ == "__main__":
#	peak_filename = "../data/wgEncodeBroadHistoneGm12878CtcfStdAlnRep0.bam_VS_wgEncodeBroadHistoneGm12878ControlStdAlnRep0.bam.regionPeak.gz"
#	peak_gz = True
#	data_filename = "../data/H3K27ac.K562.Bernstein.bedGraph"
#	data_gz = False
#	profiles_filename = "../tmp/CTCF_H3K27ac_profiles.bed3"
#	
#	make_profiles(peak_filename, peak_gz, data_filename, data_gz, profiles_filename)








