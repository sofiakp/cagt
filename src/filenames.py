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
import os
from os.path import join




def make_filename(type, file_type, relative_to=None,
                  output_folder=None, profiles_info=None, clustering_info=None,
                  cluster_id=None):
    assert(type in ['all', 'profile', 'clustering_result', 'cluster'])

    if type == 'all':
        assert(not output_folder is None)
        foldername = output_folder
        assert(file_type in ['html_view_summary'])

    elif type == 'profile':
        assert(file_type in ['folder', 'plots_done', 'html_view'])
        if file_type == 'folder':
            foldername = profiles_info.output_folder
            filename = profiles_info.handle()
        else:
            foldername = make_filename('profile', 'folder', relative_to)
            if type == 'html_view':
                filename = 'html_view.html'
            elif type == 'plots_done':
                filename = 'plots_done'

    elif type == 'clustering_result':
        assert(file_type in ['assignments', 'html_view'])
        pass

    elif type == 'cluster':
        pass

    path = join(foldername, filename)

    if not relative_to is None:
        return os.path.relpath(path, relative_to)
    else:
        return path



def make_profile_filename(profiles_info, type, relative_to=None):
    assert(type in ['folder', 'html_view', 'plots_done'])
    if type == 'folder':
        filename = profiles_info.handle()
        foldername = profiles_info.output_folder
    else:
        foldername = make_profile_filename(profiles_info, 'folder', relative_to=relative_to)
        if type == 'html_view':
            filename = 'profile_html_view.html'
        elif type == 'plots_done'
            filename = 'plots_done'

    path = join(foldername, filename)

    if not relative_to is None:
        return os.path.relpath(path, relative_to)
    else:
        return path

def make_clustering_result_filename(clustering_result, type, relative_to=None):
    foldername = make_profile_filename(clustering_result.profiles_info,
                                       'folder', relative_to=relative_to)

    cr_handle = clustering_result.handle()

    assert(type in ['html_view', 'assignments'])
    if type == 'html_view':
        identifier = 'html_view'
        extension = '.png'
    elif type == 'assignments'
        identifier = 'assignments'
        extension = '.txt'


def make_cluster_filename(clustering_result, type, cluster_id, relative_to=None):
    foldername = make_profile_filename(clustering_result.profiles_info,
                                       'folder', relative_to=relative_to)

    cr_handle = clustering_result.handle()
    oi_handle = clustering_result.cluster_id_handle(cluster_id)

    assert(type in ['boxplot'])
    if type == 'boxplot':
        identifier = 'boxplot'
        extension = '.png'

    filename = "%s_%s_%s%s" % (identifier, cr_handle, oi_handle, extension)

    path = join(foldername, filename)
    if not relative_to is None:
        return os.path.relpath(path, relative_to)
    else:
        return path


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

def make_members_filename(clustering_result, cluster_id):
    filename = "%s_members.txt" % clustering_result.filename_handle(cluster_id)
    return join(make_profiles_foldername(clustering_result.profiles_info), filename)

def make_boxplot_filename(clustering_result, cluster_id):
    filename = "%s_boxplot.png" % clustering_result.filename_handle(cluster_id)
    return join(make_profiles_foldername(clustering_result.profiles_info), filename)

def make_html_view_summary_filename():
    """......................"""
    return ""

def make_clustering_result_filename(clustering_result, relative_to=None):
    """..."""
    return ""

def make_filename(profiles_info, file_type, type_of_data,\
shape_number=None, group_number=None):

    if file_type == "html_view" and type_of_data == "summary":
        foldername = profiles_info.output_folder
    else:
        foldername = make_profiles_foldername(profiles_info)

    type_of_data_name = type_of_data
    extension = ".png"

    filename = os.path.join(foldername, file_type + "_" + type_of_data_name + extension)
    return filename


