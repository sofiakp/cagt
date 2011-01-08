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

from parameters import *
from src.filenames import *
from src.ClusteringInfo.ClusteringInfo import ClusteringInfo, clustering_info_dump, clustering_info_load
from src.analysis.cluster_all import *
from src.output.make_all_plots import *
from src.analysis.cluster_correlate import make_all_correlations
from src.output.html_view import make_all_html_views
from src.file_processing.read_profiles_list_file import read_profiles_list_file

	

if __name__ == '__main__':
	
	t0 = time()
	cluster = False
	make_plots = False
	correlate = False
	make_html = False
	proximity_cluster = False
	test_mode = False
	all_profiles = True
	

	
	# parse command line input
	# for arg in sys.argv[1:]:
	arg_index = 1
	while True:
		arg = sys.argv[arg_index]
		if arg == '--make-plots':
			make_plots = True
		elif arg == '--make-html':
			make_html = True
		elif arg == '--cluster':
			cluster = True
		elif arg == '--correlate':
			correlate = True
		elif arg == '--proximity-cluster':
			proximity_cluster = True
		elif arg == '--test':
			test_mode = True
		elif arg == '--profile':
			all_profiles = False
			arg_index += 1
			assert(arg_index < len(sys.argv))
			next_arg = sys.argv[arg_index]
			try:
				use_only_profile = int(next_arg)
				# assert(use_only_profile >= 0)
				# assert(use_only_profile < len(profiles_info))
			except:
				print "invalid profile number:", next_arg
				raise
		else:
			output_folder = arg
		arg_index += 1
		if arg_index == len(sys.argv): break

	if test_mode:
		profiles_info_list = read_profiles_list_file(test_mode_profiles_list_filename, output_folder)
	else:
		profiles_info_list = read_profiles_list_file(profiles_list_filename, output_folder)

	if not all_profiles:
		profiles_info_list = [profiles_info_list[use_only_profile]]
	
	if test_mode:
		for profiles_info in profiles_info_list:
			if cluster:
				clustering_info_delete(profiles_info)
			if make_plots:
				if os.path.isfile(make_plots_done_filename(profiles_info))
					os.remove(make_plots_done_filename(profiles_info))
	
	print "output_folder:", output_folder
	# if not os.path.isdir(make_output_foldername(output_id)):
	# 	os.system('mkdir '+make_output_foldername(output_id))
	
	for profiles_info in profiles_info_list:
		print "---------------------------------"
		print "Starting", profiles_info, "..."
		t0 = time()
		if cluster:
			print "Clustering..."
			t_cluster = time()
			cluster_profile(profiles_info)
			# clustering_info_dump(clustering_info)
			print "Time to cluster:", time() - t_cluster
		
		if make_plots:
			print "Making plots..."
			t_plots = time()
			make_plots_for_profile(profiles_info)
			print "Time to make plots:", time()-t_plots
		
		print "Total time for", profiles_info, ":", time()-t0

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
	
	if make_html:
		print "Making html..."
		t_html = time()
		make_all_html_views(profiles_info_list)
		print "Time to make html:", time()-t_html
	
		
	print "total time:", time() - t0
			
	
	
	
	
	
	
	
	
	

