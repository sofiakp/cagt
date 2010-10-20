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
from src.analysis.cluster_all import cluster_all
from src.output.make_all_plots import make_all_plots
from src.analysis.cluster_correlate import make_all_correlations
from src.analysis.gene_proximity_cluster import gene_proximity_cluster_all
from src.output.html_view import make_all_html_views

	

if __name__ == '__main__':
	t0 = time()
	output_id = make_output_id()
	cluster = False
	make_plots = False
	correlate = False
	make_html = False
	proximity_cluster = False
	
	if len(sys.argv) < 2:
		print "usage: TODO"
	
	# parse command line input
	for arg in sys.argv[1:]:
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
		else:
			try:
				input_output_id = int(arg)
				assert(input_output_id >= 0)
				assert(input_output_id < 100000)
				output_id = str(input_output_id)
			except:
				print "invalid input:", arg
				raise
	
	print "output_id:", output_id
	# make output dir
	if not os.path.isdir(make_output_foldername(output_id))	:
		os.system('mkdir '+make_output_foldername(output_id))

	# make clustering_info
	print "getting clustering_info..."
	t_ci = time()
	if os.path.isfile(make_clustering_info_dump_filename(output_id)):
		clustering_info = clustering_info_load(output_id)
	else:
		clustering_info = ClusteringInfo(output_id)
	print "time to get clustering_info:", time()-t_ci
	
	# TODO: check if all the necessary files are there, and that they're a reasonable length
	
	if cluster:
		print "Clustering..."
		t_cluster = time()
		cluster_all(clustering_info)
		clustering_info_dump(clustering_info)
		print "Total time to cluster:", time() - t_cluster
		
	if proximity_cluster:
		print "Clustering based on gene proximity..."
		t_prox = time()
		proximity_assignments = gene_proximity_cluster_all(clustering_info)
		pickle.dump(proximity_assignments, open(make_proximity_assignments_filename(output_id),"w"))
		print "Time to cluster based on gene proximity:", time()-t_prox
		
	if make_plots:
		print "Making plots..."
		t_plots = time()
		make_all_plots(clustering_info)
		print "Total time to make plots:", time()-t_plots

	if correlate:
		print "Making correlations..."
		t_cor = time()
		correlations = make_all_correlations(clustering_info)
		pickle.dump(correlations, open(make_correlations_filename(output_id),"w"))
		print "time to make correlations:", time()-t_cor
	
	if make_html:
		print "Making html..."
		t_html = time()
		make_all_html_views(clustering_info)
		print "Time to make html:", time()-t_html
	
		
	print "total time:", time() - t0
			
	
	
	
	
	
	
	
	
	

