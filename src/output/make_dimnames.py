
def make_dimnames(clustering_info, ids):
	space_between_colnames = clustering_info.profiles_info.args.space_between_colnames
	# rownames = map(lambda peak: peak[0]+" "+str(peak[1]),\
	# clustering_info.peaks[peak_tag])
	#
	# if row_indices is not None:
	# 	rownames = map(lambda i: rownames[i], row_indices)

	rownames = ids

	num_cols = clustering_info.PD.data.data.shape[1]
	colnames = num_cols*[""]
	middle = int(float(num_cols)/2)
	colnames[middle] = ["0"]

	for i in range(middle,0,-space_between_colnames):
		colnames[i]= str((i-middle)*clustering_info.profiles_info.bin_size)
	for i in range(middle+space_between_colnames,num_cols,space_between_colnames):
		colnames[i]= "+" + str((i-middle)*clustering_info.profiles_info.bin_size)

	return [rownames, colnames]
