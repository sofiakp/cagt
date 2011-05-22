

import sys
import random
import array
from math import log
import numpy as np
import logging

import rpy2.robjects as rpy
r = rpy.r

from src.filenames import *
from src.utils import MatrixMap
from src.ProfilesInfo import ProfileInfo


def read_assignments(cluster_type, peak_tag, signal_tag):
    filename = make_assignments_filename(peak_tag, signal_tag, output_id)
    return map(int,open(filename, "r").read().split())


def normalize(data):
    ids = data.ids
    data = data.data
    norm_data = np.zeros(data.shape)

    for row in range(data.shape[0]):
        std = np.std(data[row,:])
        avg = np.mean(data[row,:])
        if std < .001:
            norm_data[row,:] = np.array(data[row,:])-avg
        else:
            norm_data[row,:] = (np.array(data[row,:])-avg)/std

    return MatrixMap(norm_data, ids)


global made_converting_NaNs_warning
made_converting_NaNs_warning = False

def convert_to_float(x):
    try:
        ret = float(x)
        if ret == float('NaN'):
            if not made_converting_NaNs_warning:
                logging.warning('Converting NaNs to 0s')
                global made_converting_NaNs_warning
                made_converting_NaNs_warning = True
            return float(0)
        else:
            return ret
    except TypeError:
        logging.warning('Couldn\'t convert value "%s" to float' % x)
        return float(0)

def read_profiles_file(filename):
    file = open(filename, "r")

    raw_data = []
    peaks = []
    for line in file:
        chr = line.split()[0]
        start = int(line.split()[1])
        stop = int(line.split()[2])
#       rownames.append(chr+" "+str((start+stop)/2))
        peaks.append([chr, (start+stop)/2])
        vals = array.array('f', map(convert_to_float, line.split()[3].split(',')))
        raw_data.append(vals)

    data = np.array(raw_data)
    ids = range(len(peaks))
    data = MatrixMap(data, ids)

    return data, peaks


def read_profiles_list_file(filename, output_id, args):
    f = open(filename,"r")
    profiles = []
    for line in f:
        profiles.append(ProfileInfo(line, output_id, args))
        return profiles


def get_low_signal_profiles(data, low_signal_cutoff_value, low_signal_cutoff_quantile):
    ncol = data.data.shape[1]
    nrow = len(data.ids)
    low_signal_rows = filter(\
    lambda id: sorted(data.get_row(id))\
    [int(float(ncol)*low_signal_cutoff_quantile)]<low_signal_cutoff_value,\
    data.ids)
    return low_signal_rows





