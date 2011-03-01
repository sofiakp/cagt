signal_files_loc = "ftp://encodeftp.cse.ucsc.edu/users/akundaje/rawdata/rawsignal/jul2010/pooledReps/bedgraph/"
peak_files_loc = "ftp://encodeftp.cse.ucsc.edu/users/akundaje/rawdata/peaks/jul2010/idr0_02/narrowPeak_blacklistFiltered/"

import re

# Repurposed from:
# http://refactormycode.com/codes/675-camelcase-to-camel-case-python-newbie
def split_camel_case(string):
	sentinel = '#'
	pattern = re.compile('([A-Z][A-Z][a-z])|([a-z|0-9][A-Z])')
	split_with_sentinel = pattern.sub(lambda m: m.group()[:1] + sentinel + m.group()[1:], string)
	return split_with_sentinel.split(sentinel)

def parse_signal_line(line):
	parsed_line = {}
	line = line.split()
	filename = line[0]
	parsed_line['location'] = signal_files_loc + filename
	filename_elements = split_camel_case(filename.split('.')[0])
	
	if filename_elements[2] == 'Uw' and filename_elements[3] != 'Histone':
		filename_elements.insert(3,'Histone')
		(filename_elements[4], filename_elements[5]) = (filename_elements[5], filename_elements[4])
		# print "weirdly formatted signal line:", filename_elements
	if filename_elements[2] == 'Open':
		(filename_elements[4], filename_elements[5]) = (filename_elements[5], filename_elements[4])

	parsed_line['lab'] = filename_elements[2]
	
	parsed_line['cell_line'] = filename_elements[4]
	parsed_line['tag'] = filename_elements[5]
	if len(filename_elements) < 8:
		parsed_line['treatment1'] = "?"
		parsed_line['treatment2'] = "?"
	else:
		parsed_line['treatment1'] = filename_elements[6]
		parsed_line['treatment2'] = filename_elements[7]
	# if parsed_line['cell_line'] == 'GM12878': 
	# 	parsed_line['cell_line'] == 'Gm12878'
	return parsed_line

def parse_peak_line(line):
	parsed_line = {}
	line = line.split()
	filename = line[0]
	parsed_line['location'] = peak_files_loc + filename
	filename_elements = split_camel_case(filename.split('.')[0])

	# this is a mess
	# most of the lab names are of the form PlaceThingtheyusuallydo 
	# (two camel-case tokens)
	# But there's one called OpenChromChip, which is 3 camel-case tokens
	# we'll just delete "Chip"
	if filename_elements[2] == "Open" and filename_elements[3] == "Chrom" and filename_elements[4] == "Chip":
		del filename_elements[4]

	parsed_line['lab'] = filename_elements[2]
	parsed_line['cell_line'] = filename_elements[4]
	parsed_line['tag'] = filename_elements[5]

	# there's one profile that's formatted weirdly
	if len(filename_elements) < 9:
		# print "weirdly formatted filename:", filename_elements
		parsed_line['treatment1'] = "?"
		parsed_line['treatment2'] = "?"
	else:
		parsed_line['treatment1'] = filename_elements[6]
		parsed_line['treatment2'] = filename_elements[7]

	parsed_line['rep'] = filename_elements[-1]
	
	return parsed_line

def make_signal_file_line(signal_info):
	return signal_info['tag'] + '\t' + signal_info['cell_line'] + '\t' + \
	'0,50\t5\t10\t2510\t' + signal_info['location'] + '\n'

def make_peak_file_line(peak_info):
	return peak_info['tag'] + '\t' + peak_info['cell_line'] + '\t' + \
	'True\t' + peak_info['location'] + '\n'
	


if __name__ == "__main__":
	peak_files_raw_filename = "all_peak_files_raw.txt"
	signal_files_raw_filename = "all_signal_files_raw.txt"
	
	peak_files_filename = "../peak_files.txt"
	signal_files_filename = "../signal_files.txt"

	signal_files_raw = open(signal_files_raw_filename,'r').readlines()
	peak_files_raw = open(peak_files_raw_filename,'r').readlines()

	signal_files = map(parse_signal_line, signal_files_raw)
	peak_files = map(parse_peak_line, peak_files_raw)

	signal_files = filter(lambda x: x['cell_line'] in ['Gm12878','K562'], signal_files)
	peak_files = filter(lambda x: x['cell_line'] in ['Gm12878','K562'], peak_files)

	peak_files.sort(cmp=lambda x,y: cmp(x['tag'],y['tag']))
	signal_files.sort(cmp=lambda x,y: cmp(x['tag'],y['tag']))

	print "signal files:"
	print "cell_line:", list(set(map(lambda x: x['cell_line'], signal_files)))
	print "tag:", list(set(map(lambda x: x['tag'], signal_files)))
	print "lab:", list(set(map(lambda x: x['lab'], signal_files)))
	print "treatment1:", list(set(map(lambda x: x['treatment1'], signal_files)))
	print "treatment2:", list(set(map(lambda x: x['treatment2'], signal_files)))
	print ""

	print "peak files:"
 	print "cell_line:", list(set(map(lambda x: x['cell_line'], peak_files)))
	print "tag:", list(set(map(lambda x: x['tag'], peak_files)))
	print "lab:", list(set(map(lambda x: x['lab'], peak_files)))
	print "treatment1:", list(set(map(lambda x: x['treatment1'], peak_files)))
	print "treatment2:", list(set(map(lambda x: x['treatment2'], peak_files)))
	print "rep:", list(set(map(lambda x: x['rep'], peak_files)))


	signal_list_file = open(signal_files_filename,"w")
	for signal_file in signal_files:
		if signal_file['cell_line'] in ["K562","Gm12878"]:
			signal_list_file.write(make_signal_file_line(signal_file))

	peak_list_file = open(peak_files_filename,"w")
	for peak_file in peak_files:
		if peak_file['cell_line'] in ["K562","Gm12878"]:
			peak_list_file.write(make_peak_file_line(peak_file))
			
	
	
	
	
	
	
	
	
	
	
	
	