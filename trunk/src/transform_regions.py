
import pickle
import numpy as np

from count_runs import *

def median(lst):
	return sorted(lst)[int(len(lst)/2)]

def display(lst):
	return reduce(lambda x,y: str(x)+"\t"+str(y), lst,"")

def percentize(lst):
	s = sum(lst)
	return map(lambda val: int(1000*float(val)/s), lst)

def bin(data, bin_size):
	bin_data = []
	for entry in data:
		bin_entry = [entry[0], None]
		 
		num_bins = int(float(len(entry[1]))/bin_size)
		bin_entry[1] = np.zeros(num_bins)
		for i in range(num_bins):
			start = bin_size*i
			stop = start+bin_size
			bin_entry[1][i] = median(entry[1][start:stop])
			
		bin_data.append(bin_entry)
	
	return bin_data
	
def transform(data, cutoffs):
	transform_data = []
	for entry in data:
		transform_entry = [entry[0], None]
		transform_entry[1] = np.zeros(len(entry[1]))
		
		for i in range(len(entry[1])):
			val = entry[1][i]
			transform_val = 0
			for cutoff in cutoffs:
				if val < cutoff:
					break
				else:
					transform_val += 1
			transform_entry[1][i] = transform_val
		
		transform_data.append(transform_entry)
	return transform_data


if __name__ == "__main__":
	chrs = pickle.load(open("../tmp/histone_signal_genome_sizes.pickle","r"))
	data = pickle.load(open("../tmp/random_regions.pickle","r"))

	bin_size = 10
	cutoffs = [2]
	show_top = 10
	
	bin_data = bin(data, bin_size)
	transform_data = transform(bin_data, cutoffs)
	
	num_sig = sum(map(lambda entry: sum(entry[1]), transform_data))
	total_len = sum(map(lambda entry: len(entry[1]), transform_data))
	print "total number of bins:", total_len
	print "sum of signal:", num_sig
	
	runs = map(lambda entry: count_runs(entry[1], show_top), transform_data)
	for i in range(len(runs)):
		print data[i][0], runs[i]
	
	sum_runs = np.zeros(show_top)
	for run in runs:
		sum_runs += np.array(run)
#	sum_runs = map(lambda val: int(1000*float(val)/sum(sum_runs)), sum_runs)
	print "           ", display(range(show_top))
	print "run counts:", display(percentize(sum_runs))
	print "expected:  ", display(percentize(map(int, expected_run_counts(total_len, float(num_sig)/total_len, show_top))))
	
#	print transform_data
	
	
	
	
	
	

