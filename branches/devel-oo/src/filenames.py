##############################################
# filenames.py
# -----------------------
# This file is responsible for generating filenames everywhere
# else in CAGT.	 Filenames should never be built elsewhere:
# instead, define a new function here and call it there;
# That makes it much easier to find and refer to files once
# they're written.
##############################################


from time import time
from random import randrange
import os

# Output id
# def make_output_id():
#		return str(randrange(100000))
# def make_output_foldername(output_folder):
#		return histone_profiles_path + "output" + output_folder + "/"

def make_profiles_foldername(profiles_info):
	return os.path.join(profiles_info.output_folder, profiles_info.signal_filename + "_around_" +\
	profiles_info.peak_filename)
	
def make_profiles_pair_foldername(profiles_info_pair):
	return os.path.join(profiles_info_pair.output_folder,
	profiles_info_pair.profiles_info1.signal_filename + "_and_"\
	+ profiles_info_pair.profiles_info2.signal_filename + "_around_"\
	+ profiles_info_pair.peak_filename + "/")

def make_log_filename(output_folder):
	return os.path.join(output_folder, "log.txt")

def make_html_views_foldername(output_folder):
	return os.path.join(output_folder, "html_views")

def make_genes_filename(output_folder):
  if not os.path.isdir(os.path.join(output_folder, 'tmp')):
    os.mkdir(os.path.join(output_folder, 'tmp'))
  return os.path.join(output_folder, "tmp", "genes.pickle")

def make_clustering_info_dump_filename(profiles_info):
	return os.path.join(make_profiles_foldername(profiles_info), 'clustering_info.pickle')

def make_plots_done_filename(profiles_info):
	return os.path.join(make_profiles_foldername(profiles_info), "done_making_plots.txt")

def make_gene_proximity_filename(profiles_info):
  return os.path.join(make_profiles_foldername(profiles_info), "gene_proximity.txt")

def make_filename(profiles_info, file_type, type_of_data,\
shape_number=None, group_number=None):
		
	assert(file_type in ["boxplot", "members", "heatmap", "html_view"])
	assert(type_of_data in ["summary", "all", "high_signal", "low_signal", "magnitude_group",\
	"shape_cluster", "shape_cluster_unflipped","shape_cluster_oversegmented", "grouped_shape",\
	"signal", "peak", "profiles", "flipped"])
	# if file_type == "html_view": assert(type_of_data in ["all","signal","peak","profiles"])
	if file_type != "html_view": assert(type_of_data not in ["summary", "signal","peak","profiles"])

	if file_type == "html_view" and type_of_data == "summary":
		foldername = profiles_info.output_folder
	else:
		foldername = make_profiles_foldername(profiles_info)

	type_of_data_name = type_of_data
	if type_of_data in ["shape_cluster","shape_cluster_unflipped","shape_cluster_oversegmented"]:
		type_of_data_name += "_" + str(shape_number)
	elif type_of_data == "magnitude_group":
		type_of_data_name += "_" + str(group_number)
	elif type_of_data == "grouped_shape":
		type_of_data_name = "shape_" + str(shape_number) + "_group_" + str(group_number)
	elif file_type == "html_view":
		if type_of_data == "peak":
			type_of_data_name += "_" + profiles_info.peak_filename
		elif type_of_data == "signal":
			type_of_data_name += "_" + profiles_info.signal_filename
		elif type_of_data == "profiles":
			type_of_data_name += "_" + profiles_info.signal_filename + "_around_" + profiles_info.peak_filename
		type_of_data_name += "_" + profiles_info.cell_line
			
	if file_type == "html":
		type_of_data_name = ""
	if file_type == "boxplot":
		extension = ".png"
	elif file_type == "members":
		extension = ".txt"
	elif file_type == "html_view":
		extension = ".html"
	
	filename = os.path.join(foldername, file_type + "_" + type_of_data_name + extension)
	return filename


