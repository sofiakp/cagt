
space_between_colnames = 20

def make_dimnames(clustering_info, peak_tag, signal_tag, row_indices=None):
	rownames = map(lambda peak: peak[0]+" "+str(peak[1]),\
	clustering_info.peaks[peak_tag])
	
	if row_indices is not None:
		rownames = map(lambda i: rownames[i], row_indices)

	num_cols = clustering_info.PDs[peak_tag][signal_tag].data.shape[1]
	colnames = num_cols*[""]
	middle = int(float(num_cols)/2)
	colnames[middle] = ["0"]
	for i in range(middle,0,-space_between_colnames):
		colnames[i]=str(middle-i)
	for i in range(middle+space_between_colnames,num_cols,space_between_colnames):
		colnames[i]=str(middle-i)
	
	

	return [rownames, colnames]