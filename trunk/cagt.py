#!/bin/python
#####################################################################
# cagt.py
# Max Libbrecht
# Updated 7/10
# ---------------------------------------------------------
# See cagt/docs/docs.pdf
#####################################################################

from time import time
import pickle

import os
import sys
sys.path.append("../")
from parameters import *
from src.graphics import *
from src.process_histone_data import *
from src.get_cluster_data import *
from src.k_cluster import *
from src.two_stage_cluster import *



def write_assignments(assignments, filename):
	f = open(filename, "w")
	f.write(reduce(lambda x,y: str(x)+" "+str(y), assignments, ""))
	f.close()
	
def make_plots(filename):
	t0 = time()
	###################################################################
	# The first time you run make_plots, you'll have to run
	# the clustering.  We pickle the result, though, so if you want to 
	# skip that step the second time, comment out these two lines,
	# and the pickled result will be loaded.
	if mode == "normalize":
		data, dimnames = get_filtered_histone_data(filename, \
		normalize_cutoff_quantile, normalize_cutoff_value)
		data, dimnames = normalize(data,dimnames)	
	if mode == "group":
		data, dimnames = get_histone_data(filename)
	pickle.dump((data, dimnames), open("tmp/data.pickle","w"))
	###################################################################
	data, dimnames = pickle.load(open("tmp/data.pickle","r"))
	print "number of non-noise profiles:", len(data)
	print "time to read file:", time()-t0
	
	# cluster
	print "clustering..."
	t1 = time()
	###################################################################
	# The first time you run make_plots, you'll have to run
	# the clustering.  We pickle the result, though, so if you want to 
	# skip that step the second time, comment out these two lines,
	# and the pickled result will be loaded.
#	assignments = k_cluster(data, dimnames, num_clusters, num_passes)
	if mode == "normalize":
		assignments = k_cluster(data, dimnames, nclusters=normalize_num_clusters,\
		npass=num_passes, dist='c')
	if mode == "group":
#		assignments = k_cluster(data, dimnames, num_clusters=normalize_num_clusters,\
#		npass=num_passes, dist='c')
		assignments = ts_cluster(data, dimnames, num_groups=group_num_groups,\
		clusters_per_group=group_clusters_per_group,\
		cutoff_quantile=group_by_quantile, npass=num_passes)
	pickle.dump(assignments, open("tmp/assignments.pickle","w"))
	###################################################################
	assignments = pickle.load(open("tmp/assignments.pickle","r"))
	print "time to cluster:", time() - t1
	
	write_assignments(assignments, "output/cluster_assignments")
	
	cluster_data, cluster_indices, cluster_dimnames = \
	get_cluster_data(data, dimnames, assignments)

	# print some statistics about the clustering
	print ""
	print "clustering stats:"
	print "total number of profiles clustered:", len(data)
	print "number of clusters:", len(cluster_data)
	cluster_sizes = map(lambda x: len(x), cluster_indices)
	print "cluster sizes:", reduce(lambda x,y: str(x)+' '+str(y), cluster_sizes, "")


	print "writing all-profiles images..."
	t2 = time()
	# heatmap of all profiles
	# (For a large number of profiles, this takes a long time
	# and usually dominates the running time.  This is because heatmap
	# clusters the data to display it better (an n^2 operation))
#	heatmap(data, dimnames, mode, filename="output/heatmap_all.png",\
#	title="All profiles: "+str(data.shape[0])+" total profiles")
#	print "time to write all-profile heatmap:", time()-t2

	t3 = time()
	boxplot(data, dimnames, mode, filename="output/boxplot_all.png",\
	title="All profiles: "+str(data.shape[0])+" total profiles")
	print "time to write all-profile boxplot:", time()-t3
	

	print "writing cluster images..."	
	t4 = time()
	# for each cluster, make boxplot and heatmap
	for c in range(len(cluster_data)):
		heatmap(cluster_data[c], cluster_dimnames[c], mode,\
		filename="output/heatmap_cluster_"+str(c)+".png",
		title="Cluster "+str(c)+": "+str(cluster_data[c].shape[0])+" members")
		
		boxplot(cluster_data[c], cluster_dimnames[c], mode,\
		filename="output/boxplot_cluster_"+str(c)+".png",
		title="Cluster "+str(c)+": "+str(cluster_data[c].shape[0])+" members")
	print "time to write cluster images:", time()-t4
	print "time to print image files", time() - t2
	
	
	print "total time:", time() - t0
	return


if __name__ == '__main__':
	make_plots(filename)


















