##############################################
# filenames.py
# -----------------------
# This file is responsible for generating filenames everywhere
# else in CAGT.  Filenames should never be built elsewhere:
# instead, define a new function here and call it there;
# That makes it much easier to find and refer to files once
# they're written.
##############################################

import pdb

from time import time
from random import randrange
import os
from os.path import join




def make_filename(type, file_type, relative_to=None,
                  output_folder=None, profiles_info=None,
                  clustering_result=None, cluster_id=None):
    assert(type in ['all', 'profile', 'clustering_result', 'cluster'])
    if not relative_to is None:
        #pdb.set_trace()
        pass

    if type == 'all':
        assert(not output_folder is None)
        foldername = output_folder
        assert(file_type in ['html_view_summary'])
        if file_type == 'html_view_summary':
            filename = 'html_view_summary.html'

    elif type == 'profile':
        assert(not profiles_info is None)
        assert(file_type in ['folder', 'plots_done', 'html_view'])
        if file_type == 'folder':
            foldername = profiles_info.output_folder
            filename = profiles_info.handle()
        else:
            foldername = make_filename('profile', 'folder',
                                       profiles_info=profiles_info,
                                       output_folder=profiles_info.output_folder)
            if file_type == 'html_view':
                filename = 'html_view.html'
            elif file_type == 'plots_done':
                filename = 'plots_done'

    elif type == 'clustering_result':
        assert(not clustering_result is None)
        profiles_info = clustering_result.profiles_info
        assert(file_type in ['folder', 'assignments', 'html_view'])
        if file_type == 'folder':
            foldername = make_filename('profile', 'folder', profiles_info=profiles_info)
            filename = clustering_result.handle()
        else:
            foldername = make_filename('clustering_result', 'folder',
                                       profiles_info=profiles_info, clustering_result=clustering_result)
            if file_type == 'assignments':
                filename = '%s_assignments.txt' % clustering_result.handle()
            elif file_type == 'html_view':
                filename = '%s_html_view.html' % clustering_result.handle()

    elif type == 'cluster':
        assert(not cluster_id is None)
        assert(not clustering_result is None)
        assert(file_type in ['boxplot'])
        foldername = make_filename('clustering_result', 'folder',
                                   clustering_result=clustering_result)
        cr_handle = clustering_result.handle()
        oi_handle = clustering_result.cluster_handle(cluster_id)
        if file_type == 'boxplot':
            identifier = 'boxplot'
            extension = 'png'

        filename = "%s_%s.%s" % (identifier, oi_handle, extension)

    if (relative_to is None) and (not os.path.isdir(foldername)):
        os.makedirs(foldername)

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
    filename = "%s_members.txt" % clustering_result.cluster_handle(cluster_id)
    return join(make_profiles_foldername(clustering_result.profiles_info), filename)



