
import sys
import pickle
import os
from copy import deepcopy
import logging
import traceback
from os.path import dirname

from src.filenames import *
from src.ClusteringInfo import *
from src.gene_proximity_cluster import *

def write_members_list_to_file(assignments, filename):
    f = open(filename,"w")
    f.write(reduce(lambda x,y: x+"\n"+y,map(str, assignments),""))
    f.close()

#def make_all_html_views(profiles_info_list, do_gene_proximity=False):
    #t0 = time()
    #if not os.path.isdir(make_html_views_foldername(profiles_info_list[0].output_folder)):
        #os.mkdir(make_html_views_foldername(profiles_info_list[0].output_folder))
    #make_html_view(profiles_info_list)
    #for profiles_info in profiles_info_list:
        #try:
            #clustering_info = clustering_info_load(profiles_info)
            #make_html_clustering_view(clustering_info)
            #write_sets(clustering_info, do_gene_proximity)
        #except Exception,error:
            #logging.error("Hit error while making html")
            #logging.error("profiles_info: %s", str(profiles_info))
            #logging.error(traceback.format_exc())
            #print "HIT ERROR WHILE MAKING HTML"
            #traceback.print_exc()
            #print "Skipping this html file"
            #print "See logs for details"





def make_html_view_summary(profiles_info_list, output_folder):
    filename = make_filename('all', 'html_view_summary', output_folder=output_folder)
    f = open(filename, "w")
    header = "<html><body><h1>Profiles:</h1>"
    f.write(header)

    for profiles_info in profiles_info_list:
        f.write("<a href=%s>%s</a><br>" %
               (make_filename('profile', 'html_view',
                              relative_to=dirname(filename),
                              profiles_info=profiles_info),
                profiles_info))
        make_html_profile_view(clustering_info_load(profiles_info))


    footer = "</html></body>"
    f.write(footer)


def make_html_profile_view(clustering_info):
    profiles_info = clustering_info.profiles_info
    peak_tag = profiles_info.peak_tag
    signal_tag = profiles_info.signal_tag
    cell_line = profiles_info.cell_line
    this_filename = make_filename('profile', 'html_view', profiles_info=profiles_info)
    f = open(this_filename, "w")

    header = """<html><body>
    <h1>%s around %s</h1><br>
    Peak filename: %s<br>
    Signal filename: %s<br>
    Cell line: %s<br>""" % \
    (signal_tag, peak_tag, profiles_info.peak_filename,
     profiles_info.signal_filename, profiles_info.cell_line)
    f.write(header)

    clustering_cmp = lambda c1,c2: -cmp(c1.html_view_priority, c2.html_view_priority)
    clusterings_by_priority = sorted(clustering_info.clusterings, clustering_cmp)
    for clustering_result in clusterings_by_priority:
        f.write('<h1>%s</h1>' % clustering_result.html_view_title())
        clustering_result.make_html_view()
        f.write('<a href=%s>More information on this clustering result...<a><br>'
                % make_filename('clustering_result', 'html_view',
                                clustering_result=clustering_result,
                                relative_to=dirname(this_filename)))
        for cluster_id in clustering_result.cluster_id_iter():
            f.write('<img src=%s>' %
                    make_filename('cluster', 'boxplot',
                                  clustering_result=clustering_result,
                                  cluster_id=cluster_id,
                                  relative_to=dirname(this_filename)))
        f.write('<br>')

    footer = "</body></html>"
    f.write(footer)

def _make_html_set_view(clustering_info, members, type_of_data, shape_number=None, group_number=None, do_gene_proximity=False):
    profiles_info = clustering_info.profiles_info
    filename = make_filename(profiles_info, "html_view", type_of_data, shape_number, group_number)
    f = open(filename, "w")

    profiles_info_relative = deepcopy(profiles_info)
    profiles_info_relative.output_folder = "../"

    type_of_data_name = type_of_data
    if shape_number is not None:
        type_of_data_name += " shape %i" % shape_number
    if group_number is not None:
        type_of_data_name += " group %i" % group_number

    title = "<h2>%s around %s in %s ; cluster type: %s</h2><br>" % (profiles_info.signal_tag,
    profiles_info.peak_tag, profiles_info.cell_line, type_of_data_name)
    f.write(title)

    image = "<image src=%s><br>" % \
    make_filename(profiles_info_relative, file_type="boxplot", type_of_data=type_of_data,
    shape_number=shape_number, group_number=group_number)
    f.write(image)

    if type_of_data in ["shape_cluster", "shape_cluster_unflipped", "magnitude_group", "high_signal", "low_signal"]:
        members_list = "<a href=%s>Click here for a list of members...</a><br>" % \
        make_filename(profiles_info_relative, "members", type_of_data, shape_number, group_number)
        f.write(members_list)

    if do_gene_proximity:
        members_proximity_assignments = map(lambda m: clustering_info.gene_proximity_assignments[m], members)
        counts = {GENE_DISTAL: 0, INSIDE_GENE: 0, UPSTREAM_POS: 0, UPSTREAM_NEG: 0}
        for a in members_proximity_assignments:
            counts[a] += 1

        expected = clustering_info.expected_gene_proximity
        f.write('<br>')
        f.write("Total members: %i<br>" % len(members))
        f.write("Gene distal: %i    (expected: %i) <br>" % (counts[GENE_DISTAL], expected[GENE_DISTAL]*len(members)))
        f.write("Within %ibp of promoter: %i    (expected: %i) <br>" % \
        (gene_proximity_distance, counts[UPSTREAM_POS]+counts[UPSTREAM_NEG], expected[UPSTREAM_POS]*len(members)+expected[UPSTREAM_NEG]*len(members)))





def _write_sets(clustering_info, do_gene_proximity=False):

    profiles_info = clustering_info.profiles_info
    peak_tag = profiles_info.peak_tag
    signal_tag = profiles_info.signal_tag


    make_html_set_view(clustering_info, members=clustering_info.ids, type_of_data="all", do_gene_proximity=do_gene_proximity)
    write_members_list_to_file(clustering_info.ids,\
    make_filename(profiles_info, file_type="members", type_of_data="all"))

    make_html_set_view(clustering_info, members=clustering_info.high_signal, type_of_data="high_signal", do_gene_proximity=do_gene_proximity)
    write_members_list_to_file(clustering_info.high_signal,\
    make_filename(profiles_info, file_type="members", type_of_data="high_signal"))

    make_html_set_view(clustering_info, members=clustering_info.low_signal, type_of_data="low_signal", do_gene_proximity=do_gene_proximity)
    write_members_list_to_file(clustering_info.low_signal,\
    make_filename(profiles_info, file_type="members", type_of_data="low_signal"))

    for number in range(len(clustering_info.shape_clusters)):
        make_html_set_view(clustering_info, members=clustering_info.shape_clusters[number], type_of_data="shape_cluster", shape_number=number, do_gene_proximity=do_gene_proximity)
        write_members_list_to_file(clustering_info.shape_clusters[number],\
        make_filename(profiles_info, file_type="members", type_of_data="shape_cluster",shape_number=number))

    for number in range(len(clustering_info.shape_clusters_unflipped)):
        make_html_set_view(clustering_info, members=clustering_info.shape_clusters_unflipped[number], type_of_data="shape_cluster_unflipped", shape_number=number, do_gene_proximity=do_gene_proximity)
        write_members_list_to_file(clustering_info.shape_clusters_unflipped[number],\
        make_filename(profiles_info, file_type="members", type_of_data="shape_cluster_unflipped",shape_number=number))

    for number in range(len(clustering_info.group_clusters)):
        make_html_set_view(clustering_info, members=clustering_info.group_clusters[number], type_of_data="magnitude_group", group_number=number, do_gene_proximity=do_gene_proximity)
        write_members_list_to_file(clustering_info.group_clusters[number],\
        make_filename(profiles_info, file_type="members", type_of_data="magnitude_group",group_number=number))


