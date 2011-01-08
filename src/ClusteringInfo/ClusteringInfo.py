#########################################################
# ClusteringInfo.py
# ------------------------------------
# A ClusteringInfo object should hold all the data relevant to
# a clustering of profiles.  This approach was chosen because
# almost all the choices that are made in clustering need to
# be referred to again when plotting clusters, and it becomes unweildy
# to pass them around separately.  
#########################################################


import sys
import pickle
import os

from parameters import *
from src.filenames import *
from src.ProfileData.ProfileData import make_ProfileData
from src.file_processing.compute_signal_ylims import compute_signal_ylims

class ClusteringInfo:
	def __init__(self, profiles_info):
		self.profiles_info = profiles_info
		self.PD = None
		self.num_peaks = None
		self.peaks = None
		self.low_signal = None
		self.high_signal = None
		self.shape_clusters_oversegmented = None
		self.shape_clusters_unflipped = None
		self.shape_clusters = None
		self.flipped = None
		self.group_cutoffs = None
		self.group_clusters = None
		# self.gene_proximity_assignments = None


	def make_PD(self):
		self.PD, self.peaks, self.num_peaks, self.low_signal, self.high_signal = make_ProfileData(self.profiles_info, self)
		self.ids = self.PD.data.ids
		# if not self.PDs.has_key(peak_tag):
		# 	self.PDs[peak_tag] = {}
		# if self.PDs[peak_tag].has_key(signal_tag):
		# 	return
		# self.PDs[peak_tag][signal_tag] = ProfileData(self, peak_tag, signal_tag)
	
	def free_PD(self):
		del self.PD
		self.PD = None
	
	
	
def clustering_info_dump(clustering_info):
	if not os.path.isdir(make_profiles_foldername(clustering_info.profiles_info)):
		os.mkdir(make_profiles_foldername(clustering_info.profiles_info))
	pickle.dump(clustering_info, open(make_clustering_info_dump_filename(clustering_info.profiles_info),"w"))

def clustering_info_load(profiles_info):
	return pickle.load(open(make_clustering_info_dump_filename(profiles_info),"r"))

def clustering_info_delete(profiles_info):
	filename = make_clustering_info_dump_filename(profiles_info)
	if os.path.isfile(filename):
		os.remove(filename)
	
		
