#!/bin/python
#####################################################################
# cagt.py
# Max Libbrecht
# Updated 7/10
# ---------------------------------------------------------
# See cagt/readme.txt
#####################################################################

import sys
import os
sys.path.append(os.path.abspath(__file__))

from time import time
import pickle
import logging

try:
	import argparse
except ImportError:
	import src.argparse as argparse

import logging

from parameters import *
from src.filenames import *
from src.ClusteringInfo.ClusteringInfo import ClusteringInfo, clustering_info_dump, clustering_info_load
from src.analysis.cluster_all import *
from src.output.make_all_plots import *
from src.analysis.cluster_correlate import make_all_correlations
from src.output.html_view import make_all_html_views
from src.file_processing.read_profiles_list_file import read_profiles_list_file
from src.analysis.gene_proximity_cluster import *


def log_profiles_info(profiles_info):
	logging.info("Some info about profiles_info: %s" % str(profiles_info))
	logging.info("filenames: %s ; %s" % (profiles_info.peak_filename, profiles_info.signal_filename ))
	logging.info("low_signal_cutoff_value: %s ; ylims: %s ; flip: %s ; bin_size: %s" \
	% (profiles_info.low_signal_cutoff_value, str(profiles_info.ylims), \
	str(profiles_info.flip), str(profiles_info.bin_size)))


if __name__ == '__main__':
	t0 = time()
	
	
	# Parse command-line arguments
	parser = argparse.ArgumentParser(description="The CAGT tool for clustering histone shape")
	parser.add_argument('--cluster', action='store_true', default=False, help='Tells CAGT to run in cluster mode')
	parser.add_argument('--make-plots', action='store_true', default=False, help='Tells CAGT to run in make-plots mode')
	parser.add_argument('--make-html', action='store_true', default=False, help='Tells CAGT to run in make-html mode')
	parser.add_argument('--gene-proximity', help='Tells CAGT to run in gene-proximity mode. This argument takes the location of a gene list file')
	parser.add_argument('-d', '--debug', action='store_true', default=False, help='Tells CAGT to run in debug mode (not recommended)')
	parser.add_argument('output_dir', help="All CAGT's output goes here. Use a different output_dir for each run")
	parser.add_argument('profiles_list_filename', help="Path to a file in the profiles_list format (see FILE_FORMATS.TXT)")
	args = parser.parse_args(sys.argv[1:])

	args.output_dir = os.path.normpath(args.output_dir)
	output_folder = args.output_dir
	print "Outputting to folder: %s" % output_folder
	if not os.path.isdir(args.output_dir):
		os.mkdir(args.output_dir)

	log_filename = make_log_filename(output_folder)
	print "Logging to: %s" % log_filename
	logging.basicConfig(filename=log_filename, level=logging.DEBUG)
	logging.info("Starting CAGT")
	logging.info("args = %s", str(args))

	if len(os.listdir(args.output_dir)) > 1:
		print "Picking up from where the last run left off..."
		print "(Pick a different output directory to start fresh)"
		logging.info("Picking up from the last run")
		logging.info("Directory contains: %s" % str(os.listdir(args.output_dir)))

	profiles_info_list = read_profiles_list_file(args.profiles_list_filename, output_folder)

	# If we're running in debug mode, delete old output and reproduce it
	if args.debug:
		for profiles_info in profiles_info_list:
			if args.cluster:
				clustering_info_delete(profiles_info)
			if args.make_plots:
				if os.path.isfile(make_plots_done_filename(profiles_info)):
					os.remove(make_plots_done_filename(profiles_info))
	
	do_gene_proximity = False
	if args.gene_proximity is not None:
	  do_gene_proximity = True
	  gene_list_filename = args.gene_proximity
	  get_genes_from_gencode_file(output_folder, gene_list_filename)
	
	for profiles_info in profiles_info_list:
		print "---------------------------------"
		print "Starting", profiles_info, "..."
		logging.info("Starting %s...", str(profiles_info))
		# log_profiles_info(profiles_info)
		t0 = time()
		if args.cluster:
			logging.info("starting clustering...")
			t_cluster = time()
			cluster_profile(profiles_info)
			logging.info("Time to cluster: %s", time() - t_cluster)
		
		if do_gene_proximity:
		  clustering_info = clustering_info_load(profiles_info)
		  (gene_proximity_assignments, expected) = proximity_cluster(clustering_info)
		  clustering_info.gene_proximity_assignments = gene_proximity_assignments
		  clustering_info.expected_gene_proximity = expected
		  clustering_info_dump(clustering_info)
		
		if args.make_plots:
			logging.info("starting make_plots...")
			t_plots = time()
			make_plots_for_profile(profiles_info)
			logging.info("Time to make plots: %s", time()-t_plots)
		
		logging.info("Total time for %s: %i", str(profiles_info), time()-t0)

	
	if args.make_html:
		logging.info("making html...")
		t_html = time()
		make_all_html_views(profiles_info_list, do_gene_proximity)
		logging.info("Time to make html: %i", time()-t_html)
	
		
	logging.info("total time: %i", time() - t0)
			
	
	
	
	
	
	
	
	
	

