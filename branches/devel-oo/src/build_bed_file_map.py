#####################################################################
# build_bed_file_map.py
# --------------------------------------
# Creates a BED file map.  File maps facilitate random access of
# a BED file, without loading the whole file into memory or
# converting it to another format.  This is done with a preprocessing
# step that reads the whole file, saving positions periodically;
# then lookups can be done quickly by seek-ing to a position
# near the desired chromosome location.  

# File maps take one parameter: resolution.  In general, higher
# value for resolution results in a larger map file, while a lower
# value for resolution results in faster lookup.

# The file map has the following specification:
# The file map is a pickled tuple (data_filename, resolution, map)
# data_filename contains the filename of the BED file the map
# refers to.  resolution is the resolution of the map.
# map is a dictionary {chromosome_name : file_position}
# map[chr2][i] returns a position into data_filename guaranteed to 
# be before the entry for chr2:(i*resolution).  In addition,
# it's guaranteed to point to a position directly after a newline.

# Suggested usage:
# data_filename = "my_file.bed"
# map_filename = "bed_map_for_my_file.pickle"
# resolution = 1000
# build_bed_file_map(data_filename, resolution, map_filename)
# map_filename, map_resolution, file_map = pickle.load(open(map_filename, "r"))
# assert(data_filename == map_filename)
# assert(map_resolution == resolution)
# data_file = open(data_filename, "r")
# location_to_look_up_chr = "chr5"
# location_to_look_up_index = 100
# starting_pos = file_map[location_to_look_up_chr][location_to_look_up_index]/resolution
# data_file.seek(starting_pos)
# for line in data_file:
#		if location_to_look_up_chr == line.split()[0] and \
#		location_to_look_up_index <= line.split()[2]:
#			print line

import pickle
import sys

def build_bed_file_map(data_filename, resolution, map_filename):
	data_file = open(data_filename, "r")

	file_map = {}
	pickle.dump(file_map, open(map_filename,'w'))

	while True:
		# Read next line and parse
		pos = data_file.tell()
		line = data_file.readline()
		if len(line.split()) < 3:
			break
		chr = line.split()[0]
		start = int(line.split()[1])
		end = int(line.split()[2])
		if chr not in file_map.keys():
			print chr,
			sys.stdout.flush()
			file_map[chr] = [pos]
		# Let pos be the position associated with all 
		# previously-undefined positions up to the 
		# chromosome position of the line we just read 
		while start > (len(file_map[chr])*resolution):
			file_map[chr].append(pos)
	
	print ""
	pickle.dump((data_filename, resolution, file_map), open(map_filename,'w'))


