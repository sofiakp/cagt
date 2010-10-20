
import sys
sys.path.append('../../')

from parameters import *

def get_low_signal_profiles(data):
	ncol = data.shape[1]
	low_signal_rows = filter(\
	lambda i: sorted(data[i,:].flat)\
	[int(float(ncol)*low_signal_cutoff_quantile)]<low_signal_cutoff_value,\
	range(data.shape[0]))
	return low_signal_rows
