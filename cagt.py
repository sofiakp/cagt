#!/bin/python
#####################################################################
# cagt.py
# Max Libbrecht
# Updated 7/10
# ---------------------------------------------------------
# See cagt/readme.txt
#####################################################################

from time import time
import pickle
import os
import sys
import argparse
import logging

from parameters import *
from src.filenames import *
from src.ClusteringInfo.ClusteringInfo import ClusteringInfo, clustering_info_dump, clustering_info_load
from src.analysis.cluster_all import *
from src.output.make_all_plots import *
from src.analysis.cluster_correlate import make_all_correlations
from src.output.html_view import make_all_html_views
from src.file_processing.read_profiles_list_file import read_profiles_list_file


def log_profiles_info(profiles_info):
	logging.info("Some info about profiles_info: %s" % str(profiles_info))
	logging.info("filenames: %s ; %s" % (profiles_info.peak_filename, profiles_info.signal_filename ))
	logging.info("low_signal_cutoff_value: %s ; ylims: %s ; flip: %s ; bin_size: %s" \
	% (profiles_info.low_signal_cutoff_value, str(profiles_info.ylims), \
	str(profiles_info.flip), str(profiles_info.bin_size)))


if __name__ == '__main__':
	t0 = time()
	
	sys.path.append(os.path.abspath(sys.argv[0]))
	
	# Parse command-line arguments
	parser = argparse.ArgumentParser(description="The CAGT tool for clustering histone shape")
	parser.add_argument('--cluster', action='store_true', default=False, help='Tells CAGT to run in cluster mode')
	parser.add_argument('--make-plots', action='store_true', default=False, help='Tells CAGT to run in make-plots mode')
	parser.add_argument('--make-html', action='store_true', default=False, help='Tells CAGT to run in make-html mode')
	parser.add_argument('-d', '--debug', action='store_true', default=False, help='Tells CAGT to run in debug mode (not recommended)')
	parser.add_argument('output_dir', help="All CAGT's output goes here. Use a different output_dir for each run")
	parser.add_argument('profiles_list_filename', help="Path to a file in the profiles_list format (see FILE_FORMATS.TXT)")

	args = parser.parse_args(sys.argv[1:])
	args.output_dir = os.path.normpath(args.output_dir)
	output_folder = args.output_dir
	print "Outputting to folder: %s" % output_folder
	if not os.path.isdir(args.output_dir):
		os.mkdir(args.output_dir)
	elif not os.path.listdir(args.output_dir) == []:
		print "Picking up from where the last run left off..."
		print "(Pick a different output directory to start fresh)"
		logging.info("Picking up from the last run")
		logging.info("Directory contains: %s" % str(os.path.listdir(args.output_dir)))

	log_filename = make_log_filename(output_folder)
	print "Logging to: %s" % log_filename
	logging.basicConfig(filename=log_filename, level=logging.DEBUG)
	logging.info("Starting CAGT")
	logging.info("args = %s", str(args))

	profiles_info_list = read_profiles_list_file(args.profiles_list_filename, output_folder)

	# If we're running in debug mode, delete old output and reproduce it
	if args.debug:
		for profiles_info in profiles_info_list:
			if args.cluster:
				clustering_info_delete(profiles_info)
			if args.make_plots:
				if os.path.isfile(make_plots_done_filename(profiles_info)):
					os.remove(make_plots_done_filename(profiles_info))
	
	
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
		
		if args.make_plots:
			logging.info("starting make_plots...")
			t_plots = time()
			make_plots_for_profile(profiles_info)
			logging.info("Time to make plots: %s", time()-t_plots)
		
		logging.info("Total time for %s: %i", str(profiles_info), time()-t0)

	# if proximity_cluster:
	# 	print "Clustering based on gene proximity..."
	# 	t_prox = time()
	# 	proximity_assignments = gene_proximity_cluster_all(clustering_info)
	# 	pickle.dump(proximity_assignments, open(make_proximity_assignments_filename(output_id),"w"))
	# 	print "Time to cluster based on gene proximity:", time()-t_prox
	# if correlate:
	# 	print "Making correlations..."
	# 	t_cor = time()
	# 	correlations = make_all_correlations(clustering_info)
	# 	pickle.dump(correlations, open(make_correlations_filename(output_id),"w"))
	# 	print "time to make correlations:", time()-t_cor
	
	if args.make_html:
		print "Making html..."
		logging.info("making html...")
		t_html = time()
		make_all_html_views(profiles_info_list)
		logging.info("Time to make html: %i", time()-t_html)
	
		
	logging.info("total time: %i", time() - t0)
			
	
	
	
	
	
	
	
	
	

