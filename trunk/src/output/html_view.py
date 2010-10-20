
import sys
sys.path.append('../../')
import pickle
import os

from parameters import *
from src.filenames import *
from src.utils import map_assignments

def make_all_html_views(clustering_info):
	t0 = time()
	make_html_view(clustering_info)
	for peak_tag in peak_tags:
		make_html_peak_view(clustering_info, peak_tag)
	for signal_tag in signal_tags:
		make_html_signal_view(clustering_info, signal_tag)
	for peak_tag in peak_tags:
		for signal_tag in signal_tags:
			make_html_clustering_view(clustering_info, peak_tag, signal_tag)
	t1 = time()
	correlations = pickle.load(open(make_correlations_filename(clustering_info.output_id),"r"))
	for peak_tag in peak_tags:
		t2 = time()
		for signal_tag_index1 in range(len(signal_tags)):
			for signal_tag_index2 in range(signal_tag_index1+1, len(signal_tags)):
				signal_tag1 = signal_tags[signal_tag_index1]
				signal_tag2 = signal_tags[signal_tag_index2]
				make_html_cluster_correlation_view(clustering_info, correlations, peak_tag, signal_tag1, signal_tag2)


def make_html_view(clustering_info):
	output_id = clustering_info.output_id
	hpp = "../"
	filename = make_html_view_filename(output_id)
	f = open(filename, "w")

	f.write('<html>')
	f.write('<body>')
	f.write('<h1>Peak tracks:</h1>')
	for peak_tag in peak_tags:
		f.write('<a href="'+\
		make_html_peak_view_filename(peak_tag, output_id, histone_profiles_path=hpp)+\
		'">'+peak_tag+'</a>')
		f.write('<br>')
	f.write('<h1>Signal tracks:</h1>')
	for signal_tag in signal_tags:
		f.write('<a href="'+\
		make_html_signal_view_filename(signal_tag, output_id, histone_profiles_path=hpp)+\
		'">'+signal_tag+'</a>')
		f.write('<br>')
	f.write('</body>')
	f.write('</html>')

def make_html_peak_view(clustering_info, peak_tag):
	output_id = clustering_info.output_id
	hpp = "../"
	filename = make_html_peak_view_filename(peak_tag, output_id)
	f = open(filename, "w")

	f.write('<html>')
	f.write('<body>')
	f.write('<h1>Signal tracks</h1>')
	for signal_tag in signal_tags:
		f.write('<a href="'+\
		make_html_clustering_view_filename(peak_tag, signal_tag, output_id, histone_profiles_path=hpp)+\
		'">'+signal_tag+'</a>')
		f.write('<br>')
		
	f.write('<h1>Correlations</h1>')
	for signal_tag_index1 in range(len(signal_tags)):
		for signal_tag_index2 in range(signal_tag_index1+1, len(signal_tags)):
			signal_tag1 = signal_tags[signal_tag_index1]
			signal_tag2 = signal_tags[signal_tag_index2]
			f.write('<a href="'+\
			make_html_cluster_correlation_view_filename(peak_tag, signal_tag1, signal_tag2, output_id, histone_profiles_path=hpp)+\
			'">Correlation between'+signal_tag1+' and '+signal_tag2+'</a><br>')	
		
		
	
		
	f.write('</body>')
	f.write('</html>')

def make_html_signal_view(clustering_info, signal_tag):
	output_id = clustering_info.output_id
	hpp = "../"
	filename = make_html_signal_view_filename(signal_tag, output_id)
	f = open(filename, "w")

	f.write('<html>')
	f.write('<body>')
	f.write('<h1>Peak tracks:</h1>')
	for peak_tag in peak_tags:
		f.write('<a href="'+\
		make_html_clustering_view_filename(peak_tag, signal_tag, output_id, histone_profiles_path=hpp)+\
		'">'+peak_tag+'</a>')
		f.write('<br>')
	f.write('</body>')
	f.write('</html>')

def make_html_clustering_view(clustering_info, peak_tag, signal_tag):
	if not os.path.isdir(make_aggregation_plots_foldername(peak_tag, signal_tag, clustering_info.output_id)):
		os.mkdir(make_aggregation_plots_foldername(peak_tag, signal_tag, clustering_info.output_id))

	output_id = clustering_info.output_id
	hpp = "../../"
	filename = make_html_clustering_view_filename(peak_tag, signal_tag, output_id)
	f = open(filename, "w")

	f.write('<html>')
	f.write('<body>')
	f.write('<h1>'+signal_tag+' around '+peak_tag+'</h1>')
	f.write('<br>')
	f.write('<h2>All profiles:</h2>')
	f.write('<br>')
	f.write('<image src='+make_all_profiles_boxplot_filename(peak_tag, signal_tag, output_id, hpp)+'>')
	f.write('<br>')
	f.write('<h2>Low signal:</h2>')
	f.write('<br>')
	f.write('<image src='+make_low_signal_boxplot_filename(peak_tag, signal_tag, output_id, hpp)+'>')
	f.write('<br>')
	f.write('<h2>High signal:</h2>')
	f.write('<br>')
	f.write('<image src='+make_high_signal_boxplot_filename(peak_tag, signal_tag, output_id, hpp)+'>')
	f.write('<br>')
	f.write('<h2>Shape clusters:</h2>')
	shape_clusters = list(set(clustering_info.shape_assignments[peak_tag][signal_tag]))
	for shape_cluster in shape_clusters:
		f.write('<image src='+make_shape_boxplot_filename\
		(peak_tag, signal_tag, output_id, shape_cluster, hpp)+'>')
	f.write('<br>')
	f.write('<h2>Magnitude groups:</h2>')
	group_clusters = list(set(clustering_info.group_assignments[peak_tag][signal_tag]))
	for group_cluster in group_clusters:
		f.write('<image src='+make_group_boxplot_filename\
		(peak_tag, signal_tag, output_id, group_cluster, hpp)+'>')
	f.write('<br>')
	f.write('<h2>Shapes grouped by magnitude:</h2>')
	for shape_cluster in shape_clusters:
		for group_cluster in group_clusters:
			f.write('<image src='+make_grouped_shape_boxplot_filename\
			(peak_tag, signal_tag, output_id, shape_cluster, group_cluster, hpp)+'>')
		f.write('<br>')
	f.write('<h2>Shapes before flipping:</h2>')
	unflipped_shape_clusters = list(set(clustering_info.shape_assignments_unflipped[peak_tag][signal_tag]))
	for shape_cluster in unflipped_shape_clusters:
		f.write('<image src='+make_unflipped_shape_boxplot_filename\
		(peak_tag, signal_tag, output_id, shape_cluster, hpp)+'>')
	f.write('<h2>Shapes before merging:</h2>')
	oversegmented_shape_clusters = list(set(clustering_info.shape_assignments_oversegmented[peak_tag][signal_tag]))
	for shape_cluster in oversegmented_shape_clusters:
		f.write('<image src='+make_oversegmented_shape_boxplot_filename\
		(peak_tag, signal_tag, output_id, shape_cluster, hpp)+'>')
		
	f.write('<br>')
	f.write('</body>')
	f.write('</html>')

def make_html_cluster_correlation_view(clustering_info, correlations, peak_tag, signal_tag1, signal_tag2):
	if not os.path.isdir(make_html_cluster_correlation_view_foldername(clustering_info.output_id)):
		os.mkdir(make_html_cluster_correlation_view_foldername(clustering_info.output_id))

	filename = make_html_cluster_correlation_view_filename(peak_tag, signal_tag1, signal_tag2, 
	clustering_info.output_id)
	f = open(filename, "w")
	hpp = "../../"

	f.write("<h1>Correlation between "+signal_tag1+" and "+signal_tag2+" around "+peak_tag+"</h1>")

#	cor = pickle.load(open(make_correlations_filename(clustering_info.output_id),"r"))[peak_tag][signal_tag1][signal_tag2]
	cor = correlations[peak_tag][signal_tag1][signal_tag2]
	
	num_clusters1 = len(list(set(clustering_info.shape_assignments_unflipped[peak_tag][signal_tag1])))
	num_clusters2 = len(list(set(clustering_info.shape_assignments_unflipped[peak_tag][signal_tag2])))
		
	# sort pairs by p-value
	pairs = []
	for c1 in range(len(cor)):
		for c2 in range(len(cor[0])):
#			pairs.append(cor[c1][c2])
			pairs.append([c1,c2,int(cor[c1][c2]['intersection']),\
			float(cor[c1][c2]['p_val']), int(cor[c1][c2]['num_c1']), int(cor[c1][c2]['num_c2'])])
	pairs = sorted(pairs, cmp=lambda p1,p2: cmp(p1[3],p2[3]))
	
	for pair in pairs:
		if pair[3] > .1: break
		
		cluster1_low_signal = pair[0]==num_clusters1
		cluster2_low_signal = pair[1]==num_clusters2
		cluster1_name =  "Low-signal profiles" if cluster1_low_signal else "Cluster "+str(pair[0])
		cluster2_name =  "Low-signal profiles" if cluster2_low_signal else "Cluster "+str(pair[1])

		cluster1_filename = \
		make_low_signal_boxplot_filename(peak_tag, signal_tag1, clustering_info.output_id, hpp)\
		if cluster1_low_signal else\
		make_unflipped_shape_boxplot_filename(peak_tag, signal_tag1, clustering_info.output_id, pair[0], hpp)

		cluster2_filename = \
		make_low_signal_boxplot_filename(peak_tag, signal_tag2, clustering_info.output_id, hpp)\
		if cluster2_low_signal else\
		make_unflipped_shape_boxplot_filename(peak_tag, signal_tag2, clustering_info.output_id, pair[1], hpp)

		f.write("<p>" + cluster1_name + " in "+signal_tag1+" and "+ cluster2_name + "in "+signal_tag2+" are correlated with p="+str(pair[3])+":</p><br>")
		f.write('<image src='+cluster1_filename+'>')
		f.write('<image src='+cluster2_filename+'>')
		f.write('<p>Num c1: '+str(pair[4])+'<br>Num c2:'+str(pair[5])+'<br>Intersection:'+str(pair[2])+'</p>')
		f.write("<hr>")
		
#		f.write(str(pair[0])+"\t"+str(pair[1])+"\t"+str(pair[2])+\
#		"\t"+str(pair[4])+"\t"+str(pair[5])+"\t"+str(pair[3]))
#		cor_file.write("\n")
	f.close()


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
