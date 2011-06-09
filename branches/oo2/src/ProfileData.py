
import scipy as sp

from src.filenames import *
from src.file_processing import normalize
from src.file_processing import get_low_signal_profiles
from src.utils import *
from src.file_processing import read_profiles_file
from src.rpy_matrix_conversion import np_matrix_to_r
from src.ProfilesInfo import *

def append_data(data1, data2):
    assert(len(data1.ids) == len(data2.ids))
    data = MatrixMap(sp.hstack((data1.data, data2.data)))
    return data


class ProfileData(object):
    def __init__(self, profiles_info):
        self.data, self.ids, self.peaks = read_profiles_file(profiles_info.filename)
        low_signal_cutoff_value = profiles_info.low_signal_cutoff_value
        num_peaks = len(self.peaks)
        self.low_signal_ids = get_low_signal_profiles(self.data, low_signal_cutoff_value,
                                                      profiles_info.args.low_signal_cutoff_quantile)
        self.high_signal_ids = opposite_ids(self.low_signal_ids, self.data.ids)
        self.low_signal_data = self.data.get_rows(self.low_signal_ids)
        self.high_signal_data = self.data.get_rows(self.high_signal_ids)
        self.high_signal_norm_data = normalize(self.high_signal_data)








