

def make_dimnames(clustering_info, peak_tag, signal_tag, row_indices=None):
	rownames = map(lambda peak: peak[0]+" "+str(peak[1]),\
	clustering_info.peaks[peak_tag])
	
	if row_indices is not None:
		rownames = map(lambda i: rownames[i], row_indices)
	
	# I've been sticking to 251-width profiles. At some point 
	# I should let this be able to deal with any width of profiles,
	# but since that's kind of non-trivial, this is fine.
#	assert(clustering_info.PDs[peak_tag][signal_tag].data.shape[1]==251)
	colnames = 251*[""]
	colnames[125] = "0"
	colnames[75] = "-500"
	colnames[175] = "+500"
	colnames[25] = "-1000"
	colnames[225] = "+1000"

	return [rownames, colnames]