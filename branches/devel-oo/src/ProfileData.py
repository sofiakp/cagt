
import scipy as sp

from src.filenames import *
from src.analysis.normalize import normalize
from src.analysis.get_low_signal_profiles import get_low_signal_profiles
from src.utils import *
from src.file_processing.read_profiles_file import read_profiles_file
from src.output.rpy_matrix_conversion import np_matrix_to_r
from src.ProfilesInfo.ProfilesInfo import *

def append_data(data1, data2):
	assert(len(data1.ids) == len(data2.ids))
	data = MatrixMap(sp.hstack((data1.data, data2.data)))
	return data

def make_ProfileData(profile_info, clustering_info):
	if isinstance(profile_info, ProfileInfoPair):
		data1, peaks1 = read_profiles_file(profile_info.profiles_info1.filename)
		data2, peaks2 = read_profiles_file(profile_info.profiles_info2.filename)
		assert(len(peaks1) == len(peaks2))
		peaks = peaks1
		data = append_data(data1,data2)
		# Ideally, we would use the right low_signal_cutoff_value for the right side
		# and the left for the left, but that's too much work, and it's not clear
		# how it would work given that we use the 90%th percentile.  So we'll
		# use the min of the two for both sides.
		low_signal_cutoff_value = min(profile_info.profiles_info1.low_signal_cutoff_value,\
		profiles_info.profiles_info2.low_signal_cutoff_value)
	else:
		data, peaks = read_profiles_file(profile_info.filename)
		low_signal_cutoff_value = profile_info.low_signal_cutoff_value
	num_peaks = len(peaks)
	low_signal_ids = get_low_signal_profiles(data, low_signal_cutoff_value)
	high_signal_ids = opposite_ids(low_signal_ids, data.ids)
	PD = ProfileData(profile_info, clustering_info, data, low_signal_ids, high_signal_ids)
	return PD, peaks, num_peaks, low_signal_ids, high_signal_ids

class ProfileData:
	def __init__(self, profile_info, clustering_info, data, low_signal_ids, high_signal_ids):
		self.profile_info = profile_info
		# self.peak_tag = peak_tag
		# self.signal_tag = signal_tag
		self.clustering_info = clustering_info
		
		# profiles_filename = make_profiles_filename(peak_tag, signal_tag)
		# profiles_filename = profile_info.filename

		self.data = data
		self.low_signal_data = data.get_rows(low_signal_ids)
		self.high_signal_data = data.get_rows(high_signal_ids)
		self.high_signal_norm_data = normalize(self.high_signal_data)
		
		
	
	
	
	
	