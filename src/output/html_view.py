
import sys
sys.path.append('../../')
import pickle
import os
from copy import deepcopy
import logging
import traceback

from parameters import *
from src.filenames import *
from src.ClusteringInfo.ClusteringInfo import *

def make_all_html_views(profiles_info_list):
	t0 = time()
	if not os.path.isdir(make_html_views_foldername(profiles_info_list[0].output_folder)):
		os.mkdir(make_html_views_foldername(profiles_info_list[0].output_folder))
	make_html_view(profiles_info_list)
	for profiles_info in profiles_info_list:
		try:
			clustering_info = clustering_info_load(profiles_info)
			make_html_clustering_view(clustering_info)
			write_members(clustering_info)
		except Exception,error:
			logging.error("Hit error while making html")
			logging.error("profiles_info: %s", str(clustering_info.profiles_info))
			logging.error(traceback.format_exc())
			print "HIT ERROR WHILE MAKING HTML"
			traceback.print_exc()
			print "Skipping this html file"
			print "See logs for details"
		


def make_html_view(profiles_info_list):
	profiles_info_example = profiles_info_list[0]
	filename = make_filename(profiles_info_example, file_type="html_view", type_of_data="all")
	f = open(filename, "w")

	f.write('<html>')
	f.write('<body>')
	f.write('<h1>Profiles:</h1>')
	for profiles_info in profiles_info_list:
		f.write("<a href=")
		profiles_info_copy = deepcopy(profiles_info)
		profiles_info_copy.output_folder = "../"
		link = make_filename(profiles_info_copy, file_type="html_view", type_of_data="profiles")
		f.write(link)
		f.write(">")
		f.write(profiles_info.signal_tag + " around " + profiles_info.peak_tag + " (" + profiles_info.cell_line + ")")
		f.write("</a><br>")
	f.write('</body>')
	f.write('</html>')


def make_html_clustering_view(clustering_info):
	
	profiles_info = deepcopy(clustering_info.profiles_info)
	profiles_info.output_folder = "../../"
	peak_tag = profiles_info.peak_tag
	signal_tag = profiles_info.signal_tag
	cell_line = profiles_info.cell_line
	filename = make_filename(clustering_info.profiles_info, file_type="html_view", type_of_data="profiles")
	f = open(filename, "w")
	
	
	f.write('<html>')
	f.write('<body>')
	f.write('<h1>'+signal_tag+' around '+peak_tag+'</h1>')
	f.write('<br>')
	f.write('Peak filename:'+profiles_info.peak_filename)
	f.write('<br>')
	f.write('Signal filename:'+profiles_info.signal_filename)
	f.write('<br>')
	f.write('Cell line:'+profiles_info.cell_line)
	f.write('<br>')
	f.write('<h2>All profiles:</h2>')
	f.write('<br>')
	f.write('<image src='+make_filename(profiles_info, file_type="boxplot", type_of_data="all")+'>')
	f.write('<br>')
	f.write('<h2>Low signal:</h2>')
	f.write('<br>')
	f.write('<a href='+make_filename(profiles_info, file_type="members", type_of_data="low_signal")+'>')
	f.write('<image src='+make_filename(profiles_info, file_type="boxplot", type_of_data="low_signal")+'>')
	f.write('</a>')
	f.write('<br>')
	f.write('<h2>High signal:</h2>')
	f.write('<br>')
	f.write('<a href='+make_filename(profiles_info, file_type="members", type_of_data="high_signal")+'>')
	f.write('<image src='+make_filename(profiles_info, file_type="boxplot", type_of_data="high_signal")+'>')
	f.write('</a>')
	f.write('<br>')
	f.write('<h2>Shape clusters:</h2>')
	shape_clusters = range(len(clustering_info.shape_clusters))
	for shape_cluster in shape_clusters:
		f.write('<a href='+make_filename(profiles_info, file_type="members", type_of_data="shape_cluster", shape_number=shape_cluster)+'>')
		f.write('<image src='+make_filename(profiles_info, file_type="boxplot", type_of_data="shape_cluster", shape_number=shape_cluster)+'>')
		f.write('</a>')
	f.write('<br>')
	f.write('<h2>Magnitude groups:</h2>')
	group_clusters = range(len(clustering_info.group_clusters))
	for group_cluster in group_clusters:
		f.write('<a href='+make_filename(profiles_info, file_type="members", type_of_data="magnitude_group", group_number=group_cluster)+'>')
		f.write('<image src='+make_filename(profiles_info, file_type="boxplot", type_of_data="magnitude_group", group_number=group_cluster)+'>')
		f.write('</a>')
	f.write('<br>')
	f.write('<h2>Shapes grouped by magnitude:</h2>')
	for shape_cluster in shape_clusters:
		for group_cluster in group_clusters:
			f.write('<image src='+make_filename(profiles_info, file_type="boxplot", type_of_data="grouped_shape", shape_number=shape_cluster, group_number=group_cluster)+'>')
		f.write('<br>')
	if profiles_info.flip:
		f.write('<h2>Shapes before flipping:</h2>')
		unflipped_shape_clusters = range(len(clustering_info.shape_clusters_unflipped))
		for shape_cluster in unflipped_shape_clusters:
			f.write('<a href='+make_filename(profiles_info, file_type="members", type_of_data="shape_cluster_unflipped", shape_number=shape_cluster)+'>')
			f.write('<image src='+make_filename(profiles_info, file_type="boxplot", type_of_data="shape_cluster_unflipped", shape_number=shape_cluster)+'>')
			f.write('</a>')
	f.write('<h2>Shapes before merging:</h2>')
	oversegmented_shape_clusters = range(len(clustering_info.shape_clusters_oversegmented))
	for shape_cluster in oversegmented_shape_clusters:
		f.write('<image src='+make_filename(profiles_info, file_type="boxplot", type_of_data="shape_cluster_oversegmented", shape_number=shape_cluster)+'>')
		
	f.write('<br>')
	f.write('</body>')
	f.write('</html>')

# def make_html_cluster_correlation_view(clustering_info, correlations, peak_tag, signal_tag1, signal_tag2):
# 		
# 	f = open(filename, "w")
# 	hpp = "../../"
# 	
# 	f.write("<h1>Correlation between "+signal_tag1+" and "+signal_tag2+" around "+peak_tag+"</h1>")
# 	
# #	cor = pickle.load(open(make_correlations_filename(clustering_info.output_id),"r"))[peak_tag][signal_tag1][signal_tag2]
# 	cor = correlations[peak_tag][signal_tag1][signal_tag2]
# 	
# 	num_clusters1 = len(list(set(clustering_info.shape_assignments_unflipped[peak_tag][signal_tag1])))
# 	num_clusters2 = len(list(set(clustering_info.shape_assignments_unflipped[peak_tag][signal_tag2])))
# 		
# 	# sort pairs by p-value
# 	pairs = []
# 	for c1 in range(len(cor)):
# 		for c2 in range(len(cor[0])):
# #			pairs.append(cor[c1][c2])
# 			pairs.append([c1,c2,int(cor[c1][c2]['intersection']),\
# 			float(cor[c1][c2]['p_val']), int(cor[c1][c2]['num_c1']), int(cor[c1][c2]['num_c2'])])
# 	pairs = sorted(pairs, cmp=lambda p1,p2: cmp(p1[3],p2[3]))
# 	
# 	for pair in pairs:
# 		if pair[3] > .1: break
# 		
# 		cluster1_low_signal = pair[0]==num_clusters1
# 		cluster2_low_signal = pair[1]==num_clusters2
# 		cluster1_name =  "Low-signal profiles" if cluster1_low_signal else "Cluster "+str(pair[0])
# 		cluster2_name =  "Low-signal profiles" if cluster2_low_signal else "Cluster "+str(pair[1])
# 		
# 		cluster1_filename = \
# 		make_low_signal_boxplot_filename(peak_tag, signal_tag1, clustering_info.output_id, hpp)\
# 		if cluster1_low_signal else\
# 		make_unflipped_shape_boxplot_filename(peak_tag, signal_tag1, clustering_info.output_id, pair[0], hpp)
# 		
# 		cluster2_filename = \
# 		make_low_signal_boxplot_filename(peak_tag, signal_tag2, clustering_info.output_id, hpp)\
# 		if cluster2_low_signal else\
# 		make_unflipped_shape_boxplot_filename(peak_tag, signal_tag2, clustering_info.output_id, pair[1], hpp)
# 		
# 		f.write("<p>" + cluster1_name + " in "+signal_tag1+" and "+ cluster2_name + "in "+signal_tag2+" are correlated with p="+str(pair[3])+":</p><br>")
# 		f.write('<image src='+cluster1_filename+'>')
# 		f.write('<image src='+cluster2_filename+'>')
# 		f.write('<p>Num c1: '+str(pair[4])+'<br>Num c2:'+str(pair[5])+'<br>Intersection:'+str(pair[2])+'</p>')
# 		f.write("<hr>")
# 		
# #		f.write(str(pair[0])+"\t"+str(pair[1])+"\t"+str(pair[2])+\
# #		"\t"+str(pair[4])+"\t"+str(pair[5])+"\t"+str(pair[3]))
# #		cor_file.write("\n")
# 	f.close()

def write_members(clustering_info):
	def write_members_list_to_file(assignments, filename):
		f = open(filename,"w")
		f.write(reduce(lambda x,y: x+"\n"+y,map(str, assignments),""))
		f.close()

	profiles_info = clustering_info.profiles_info
	peak_tag = profiles_info.peak_tag
	signal_tag = profiles_info.signal_tag
	
	write_members_list_to_file(clustering_info.high_signal,\
	make_filename(profiles_info, file_type="members", type_of_data="high_signal"))
	write_members_list_to_file(clustering_info.low_signal,\
	make_filename(profiles_info, file_type="members", type_of_data="low_signal"))
	
	for number in range(len(clustering_info.shape_clusters)):
		write_members_list_to_file(clustering_info.shape_clusters[number],\
		make_filename(profiles_info, file_type="members", type_of_data="shape_cluster",shape_number=number))
	
	for number in range(len(clustering_info.shape_clusters_unflipped)):
		write_members_list_to_file(clustering_info.shape_clusters_unflipped[number],\
		make_filename(profiles_info, file_type="members", type_of_data="shape_cluster_unflipped",shape_number=number))
	
	for number in range(len(clustering_info.group_clusters)):
		write_members_list_to_file(clustering_info.group_clusters[number],\
		make_filename(profiles_info, file_type="members", type_of_data="magnitude_group",group_number=number))
		
	

#def make_html_correlation_view(clustering_info, peak_tag, signal_tag1, signal_tag2):
#	filename = make_html_correlation_view_filename(peak_tag, signal_tag1, signal_tag2, 
#	clustering_info.output_id)
#	f = open(filename, "w")
#	hpp = "../../"
#
#	num_peaks = clustering_info.num_peaks[peak_tag]
#	clusters1 = map_assignments(clustering_info.shape_assignments[peak_tag][signal_tag1],\
#	clustering_info.high_signal[peak_tag][signal_tag1], num_peaks)
#	clusters2 = map_assignments(clustering_info.shape_assignments[peak_tag][signal_tag2],\
#	clustering_info.high_signal[peak_tag][signal_tag2], num_peaks)
#	correlations = pickle.load(open(make_correlations_filename(clustering_info.output_id),"r"))
##	cor = clustering_info.correlations[peak_tag][signal_tag1][signal_tag2]
#	
#	pairs = []
#	for c1 in clusters1:
#		for c2 in clusters2:
#			pairs.append([c1,c2,int(cor[c1][c2]['intersection']),\
#			float(cor[c1][c2]['p_val']), int(cor[c1][c2]['num_c1']), int(cor[c1][c2]['num_c2'])])
#	pairs = sorted(pairs, cmp=lambda p1,p2: cmp(p1[3],p2[3]))
#
#
#	f.write('<html>')
#	f.write('<body>')
#	f.write('<h1>Correlation between'+signal_tag1+' and '+signal_tag2+' around '+peak_tag+'</h1>')
#	for pair in pairs:
#		if pair[3] <= correlation_significance_cutoff:
#			f.write('<h3><p>Significant correlation between cluster '+str(pair[0])+' in '+signal_tag1+' and '+str(pair[1])+' in '+signal_tag2+'<\p><\h3><br>')
#			f.write('Size of cluster '+str(pair[0])+' in '+signal_tag1+': '+str(pair[4])+'<br>')
#			f.write('Size of cluster '+str(pair[1])+' in '+signal_tag2+': '+str(pair[5])+'<br>')
#			f.write('Size of intersection: '+str(pair[2]))
#			f.write('<image src='+make_shape_boxplot_filename\
#			(peak_tag, signal_tag1, output_id, pair[0], hpp)+'>')
#			f.write('<image src='+make_shape_boxplot_filename\
#			(peak_tag, signal_tag2, output_id, pair[1], hpp)+'>')
#			f.write('<br><br>')
#	f.write('</body>')
#	f.write('</html>')
