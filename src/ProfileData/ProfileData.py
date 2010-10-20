


from src.filenames import *
from src.analysis.normalize import normalize
from src.analysis.get_low_signal_profiles import get_low_signal_profiles
from src.utils import opposite_indices
from src.get_assignment_indices import get_assignment_indices
from src.file_processing.read_profiles_file import read_profiles_file
from src.output.rpy_matrix_conversion import np_matrix_to_r

class ProfileData:
	def __init__(self, clustering_info, peak_tag, signal_tag):
		self.peak_tag = peak_tag
		self.signal_tag = signal_tag
		self.clustering_info = clustering_info
		
		profiles_filename = make_profiles_filename(peak_tag, signal_tag)
		
		self.data, self.clustering_info.peaks[peak_tag] =\
		read_profiles_file(profiles_filename)
		clustering_info.num_peaks[peak_tag] =\
		len(self.clustering_info.peaks[peak_tag])


		self.r_data = np_matrix_to_r(self.data)

		
		self.clustering_info.low_signal[peak_tag][signal_tag] =\
		get_low_signal_profiles(self.data)
		self.clustering_info.high_signal[peak_tag][signal_tag] =\
		opposite_indices(self.clustering_info, peak_tag, signal_tag,\
		self.clustering_info.low_signal[peak_tag][signal_tag])
		
		self.low_signal_data = self.data\
		[self.clustering_info.low_signal[peak_tag][signal_tag],:]
		self.high_signal_data = self.data\
		[self.clustering_info.high_signal[peak_tag][signal_tag],:]
		
		self.high_signal_norm_data = normalize(self.high_signal_data)
		
		self.r_high_signal_norm_data = np_matrix_to_r(self.high_signal_norm_data)

		
	
	
	
	
	