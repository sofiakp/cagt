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
sys.path.append('../../')
import pickle

from parameters import *
from src.filenames import *
from src.ProfileData.ProfileData import ProfileData
from src.file_processing.compute_signal_ylims import compute_signal_ylims

class ClusteringInfo:
	def __init__(self, output_id):
		self.output_id = str(output_id)
		self.PDs = {} # peak_tag, signal_tag -> profilesInfo
		self.num_peaks = {} # peak_tag -> num_peaks
		self.peaks = {} # peak_tag -> peaks
		self.low_signal = {} # peak_tag, signal_tag -> low_signal
		self.high_signal = {} # peak_tag, signal_tag -> low_signal
		self.shape_assignments_oversegmented = {} # peak_tag, signal_tag -> assignments
		self.shape_assignments_unflipped = {} # peak_tag, signal_tag -> assignments
		self.shape_assignments = {} # peak_tag, signal_tag -> assignments
		self.flipped = {} # peak_tag, signal_tag -> [flipped]
		self.group_cutoffs = {} # peak_tag, signal_tag -> [cutoffs]
		self.group_assignments = {} # peak_tag, signal_tag -> assignments
		self.gene_proximity_assignments = {} # peak_tag -> assignments
		self.boxplot_ylims = {} # signal_tag -> ylims

		for peak_tag in peak_tags: self.PDs[peak_tag] = {}
		for peak_tag in peak_tags: self.high_signal[peak_tag] = {}
		for peak_tag in peak_tags: self.low_signal[peak_tag] = {}
		for peak_tag in peak_tags: self.shape_assignments_oversegmented[peak_tag] = {}
		for peak_tag in peak_tags: self.shape_assignments_unflipped[peak_tag] = {}
		for peak_tag in peak_tags: self.shape_assignments[peak_tag] = {}
		for peak_tag in peak_tags: self.flipped[peak_tag] = {}
		for peak_tag in peak_tags: self.group_cutoffs[peak_tag] = {}
		for peak_tag in peak_tags: self.group_assignments[peak_tag] = {}

		for signal_tag in signal_tags:
			self.boxplot_ylims[signal_tag] = compute_signal_ylims(self, signal_tag)

	def make_PD(self, peak_tag, signal_tag):
		if not self.PDs.has_key(peak_tag):
			self.PDs[peak_tag] = {}
		if self.PDs[peak_tag].has_key(signal_tag):
			return
		self.PDs[peak_tag][signal_tag] = ProfileData(self, peak_tag, signal_tag)
	
	def free_PD(self, peak_tag, signal_tag):
		del self.PDs[peak_tag][signal_tag]
	
	
def clustering_info_dump(clustering_info):
	pickle.dump(clustering_info, open(make_clustering_info_dump_filename(clustering_info.output_id),"w"))

def clustering_info_load(output_id):
	return pickle.load(open(make_clustering_info_dump_filename(output_id),"r"))
	
		
