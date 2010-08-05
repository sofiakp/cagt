
import numpy as np
import random
import pickle
from count_runs import *

def get_region_from_wig(filename, chr, start, stop):
	file = open(filename, "r")
	data = np.zeros(stop-start)

	while True:
		line = file.readline()
		if line[:9] == "fixedStep" and \
		line.split()[1].split('=')[1] == chr:
			for i in range(start): file.readline()
			for i in range(stop-start):
				line = file.readline()
				val = float(line[:-1])
				data[i] = val
			break
	return data
	


def pick_random_genomic_region(filename, chrs, length):

	total_len = sum(chrs.values())
	
	# pick a random chromosome
	rand = random.random() * total_len
	for key in chrs.keys():
		if rand <= chrs[key]:
			chr = key
			break
		else:
			rand -= chrs[key]
	
	# pick a random location along the chromosome
	start = int(random.random() * (chrs[chr]-length))
	stop = start + length
	
	print chr, start, stop
	
	return ([chr,start,stop], get_region_from_wig(filename, chr, start, stop))
	

if __name__ == "__main__":
	filename = "../data/wgEncodeBroadChipSeqSignalK562H3k27ac.wig"
	#file = open(filename, "r")
	
	chrs = pickle.load(open("../tmp/histone_signal_genome_sizes.pickle","r"))
	
	region_len = 10000
	num_regions = 10
	
	data = []
	for i in range(num_regions):
		data.append(pick_random_genomic_region(filename, chrs, region_len))
	
	pickle.dump(data, open("../tmp/random_regions_small.pickle","w"))
	
	data = pickle.load(open("../tmp/random_regions_small.pickle","r"))
	
	
			









