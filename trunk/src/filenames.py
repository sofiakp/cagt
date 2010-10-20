##############################################
# filenames.py
# -----------------------
# This file is responsible for generating filenames everywhere
# else in CAGT.  Filenames should never be built elsewhere:
# instead, define a new function here and call it there;
# That makes it much easier to find and refer to files once
# they're written.
##############################################


from time import time
from random import randrange

from parameters import histone_profiles_path as histone_profiles_path_absolute
from parameters import cell_line

# Raw files
def make_peak_files_list_filename():
	return "data/peak_files_"+cell_line+".txt"
def make_signal_files_list_filename():
	return "data/signal_files_"+cell_line+".txt"
def make_profiles_filename(peak_tag, signal_tag):
	return histone_profiles_path_absolute + "data/profiles_"+cell_line+"/" + signal_tag + "_around_" + peak_tag + ".bed3"
def make_file_map_filename(tag):
	return histone_profiles_path_absolute + "tmp/" + tag + "_map.pickle"
def make_gencode_filename():
	return histone_profiles_path_absolute + "data/wgEncodeGencodeManualV3.gtf.gz"
	
	
# Output id
def make_output_id():
	return str(randrange(100000))
def make_output_foldername(output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return histone_profiles_path + "output" + output_id + "/"

# ProfileData
def make_assignments_filename(signal_tag, peak_tag, output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_aggregation_plots_foldername(peak_tag, signal_tag, output_id)\
	 + "cluster_assignments"


# boxplots
def make_aggregation_plots_foldername(peak_tag, signal_tag, output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_output_foldername(output_id, histone_profiles_path) +\
	signal_tag + "_around_" + peak_tag + "/"
def make_shape_boxplot_filename(peak_tag, signal_tag, output_id, cluster_number,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_aggregation_plots_foldername(peak_tag, signal_tag, output_id, histone_profiles_path) +\
	signal_tag + "_around_" + peak_tag + "_boxplot_shape_"+str(cluster_number)+".png"
def make_oversegmented_shape_boxplot_filename(peak_tag, signal_tag, output_id, cluster_number,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_aggregation_plots_foldername(peak_tag, signal_tag, output_id, histone_profiles_path) +\
	signal_tag + "_around_" + peak_tag + "_boxplot_oversgemented_shape_"+str(cluster_number)+".png"
def make_unflipped_shape_boxplot_filename(peak_tag, signal_tag, output_id, cluster_number,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_aggregation_plots_foldername(peak_tag, signal_tag, output_id, histone_profiles_path) +\
	signal_tag + "_around_" + peak_tag + "_boxplot_unflipped_shape_"+str(cluster_number)+".png"
def make_group_boxplot_filename(peak_tag, signal_tag, output_id, group_number,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_aggregation_plots_foldername(peak_tag, signal_tag, output_id, histone_profiles_path) +\
	signal_tag + "_around_" + peak_tag + "_boxplot_group_"+str(group_number)+".png"
def make_grouped_shape_boxplot_filename(peak_tag, signal_tag,\
output_id, shape_number, group_number,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_aggregation_plots_foldername(peak_tag, signal_tag, output_id, histone_profiles_path) +\
	signal_tag + "_around_" + peak_tag + "_boxplot_shape_"+str(shape_number)\
	+"_group_"+str(group_number)+".png"
def make_all_profiles_boxplot_filename(peak_tag, signal_tag, output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_aggregation_plots_foldername(peak_tag, signal_tag, output_id, histone_profiles_path) +\
	signal_tag + "_around_" + peak_tag + "_all_profiles.png"
def make_low_signal_boxplot_filename(peak_tag, signal_tag, output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_aggregation_plots_foldername(peak_tag, signal_tag, output_id, histone_profiles_path) +\
	signal_tag + "_around_" + peak_tag + "_low_signal.png"
def make_high_signal_boxplot_filename(peak_tag, signal_tag, output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_aggregation_plots_foldername(peak_tag, signal_tag, output_id, histone_profiles_path) +\
	signal_tag + "_around_" + peak_tag + "_high_signal.png"

def make_cor_filename(peak_tag, signal_tag1, signal_tag2,  output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_aggregation_plots_foldername(signal_tag1, peak_tag, output_id, histone_profiles_path) +\
	"correlation_between_" + signal_tag1 + "_and_" + signal_tag2 +\
	"_around_" + peak_tag + ".txt"
	

def make_html_view_filename(output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_output_foldername(output_id, histone_profiles_path) + 'html_view.html'
def make_html_peak_view_filename(peak_tag, output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_output_foldername(output_id, histone_profiles_path) + 'html_view_peak_'+peak_tag+'.html'
def make_html_signal_view_filename(signal_tag, output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_output_foldername(output_id, histone_profiles_path) + 'html_view_signal_'+signal_tag+'.html'
def make_html_clustering_view_filename(peak_tag, signal_tag, output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_aggregation_plots_foldername(peak_tag, signal_tag, output_id, histone_profiles_path) +\
	'html_view_'+signal_tag+'_around_'+peak_tag+'.html'
#def make_html_correlation_view_filename(peak_tag, signal_tag1, signal_tag2, output_id,\
#histone_profiles_path=histone_profiles_path_absolute):
#	return make_output_foldername(output_id, histone_profiles_path) +\
#	'html_view_correlation_between_'+signal_tag1+'_and_'+signal_tag2+'_around_'+peak_tag+'.html'
def make_html_cluster_correlation_view_foldername(output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_output_foldername(output_id, histone_profiles_path) +\
	'correlation_html_views/'
def make_html_cluster_correlation_view_filename(peak_tag, signal_tag1, signal_tag2, output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_html_cluster_correlation_view_foldername(output_id, histone_profiles_path) +\
	'html_view_cluster_correlation_between_'+signal_tag1+'_and_'+signal_tag2+'_around_'+peak_tag+'.html'


def make_clustering_info_dump_filename(output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_output_foldername(output_id, histone_profiles_path) +\
	'clustering_info_dump.pickle'
def make_pairwise_clustering_info_dump_filename(output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_output_foldername(output_id, histone_profiles_path) +\
	'pairwise_clustering_info_dump.pickle'

def make_correlations_filename(output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_output_foldername(output_id, histone_profiles_path) +\
	'correlations.pickle'

def make_proximity_assignments_filename(output_id,\
histone_profiles_path=histone_profiles_path_absolute):
	return make_output_foldername(output_id, histone_profiles_path) +\
	'proximity_assignments.pickle'


