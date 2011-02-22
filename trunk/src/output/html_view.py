
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
      write_sets(clustering_info)
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
  filename = make_filename(profiles_info_example, file_type="html_view", type_of_data="summary")
  f = open(filename, "w")

  f.write('<html>')
  f.write('<body>')
  f.write('<h1>Profiles:</h1>')
  for profiles_info in profiles_info_list:
    f.write("<a href=")
    profiles_info_copy = deepcopy(profiles_info)
    profiles_info_copy.output_folder = "./"
    link = make_filename(profiles_info_copy, file_type="html_view", type_of_data="profiles")
    f.write(link)
    f.write(">")
    f.write(profiles_info.signal_tag + " around " + profiles_info.peak_tag + " (" + profiles_info.cell_line + ")")
    f.write("</a><br>")
  f.write('</body>')
  f.write('</html>')


def make_html_clustering_view(clustering_info):
  
  profiles_info = deepcopy(clustering_info.profiles_info)
  profiles_info.output_folder = "../"
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
  f.write('<a href='+make_filename(profiles_info, file_type="html_view", type_of_data="all")+'>')
  f.write('<image src='+make_filename(profiles_info, file_type="boxplot", type_of_data="all")+'>')
  f.write('</a>')
  f.write('<br>')
  f.write('<h2>Low signal:</h2>')
  f.write('<br>')
  f.write('<a href='+make_filename(profiles_info, file_type="html_view", type_of_data="low_signal")+'>')
  f.write('<image src='+make_filename(profiles_info, file_type="boxplot", type_of_data="low_signal")+'>')
  f.write('</a>')
  f.write('<br>')
  f.write('<h2>High signal:</h2>')
  f.write('<br>')
  f.write('<a href='+make_filename(profiles_info, file_type="html_view", type_of_data="high_signal")+'>')
  f.write('<image src='+make_filename(profiles_info, file_type="boxplot", type_of_data="high_signal")+'>')
  f.write('</a>')
  f.write('<br>')
  f.write('<h2>Shape clusters:</h2>')
  shape_clusters = range(len(clustering_info.shape_clusters))
  for shape_cluster in shape_clusters:
    f.write('<a href='+make_filename(profiles_info, file_type="html_view", type_of_data="shape_cluster", shape_number=shape_cluster)+'>')
    f.write('<image src='+make_filename(profiles_info, file_type="boxplot", type_of_data="shape_cluster", shape_number=shape_cluster)+'>')
    f.write('</a>')
  f.write('<br>')
  f.write('<h2>Magnitude groups:</h2>')
  group_clusters = range(len(clustering_info.group_clusters))
  for group_cluster in group_clusters:
    f.write('<a href='+make_filename(profiles_info, file_type="html_view", type_of_data="magnitude_group", group_number=group_cluster)+'>')
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
      f.write('<a href='+make_filename(profiles_info, file_type="html_view", type_of_data="shape_cluster_unflipped", shape_number=shape_cluster)+'>')
      f.write('<image src='+make_filename(profiles_info, file_type="boxplot", type_of_data="shape_cluster_unflipped", shape_number=shape_cluster)+'>')
      f.write('</a>')
  f.write('<h2>Shapes before merging:</h2>')
  oversegmented_shape_clusters = range(len(clustering_info.shape_clusters_oversegmented))
  for shape_cluster in oversegmented_shape_clusters:
    f.write('<image src='+make_filename(profiles_info, file_type="boxplot", type_of_data="shape_cluster_oversegmented", shape_number=shape_cluster)+'>')
    
  f.write('<br>')
  f.write('</body>')
  f.write('</html>')


def make_html_set_view(clustering_info, members, type_of_data, shape_number=None, group_number=None):
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
    members_list = "<a href=%s>Click here for a list of members...<br>" % \
    make_filename(profiles_info_relative, "members", type_of_data, shape_number, group_number)
    f.write(members_list)
  
  

def write_sets(clustering_info):
  def write_members_list_to_file(assignments, filename):
    f = open(filename,"w")
    f.write(reduce(lambda x,y: x+"\n"+y,map(str, assignments),""))
    f.close()

  profiles_info = clustering_info.profiles_info
  peak_tag = profiles_info.peak_tag
  signal_tag = profiles_info.signal_tag


  make_html_set_view(clustering_info, members=clustering_info.ids, type_of_data="all")
  write_members_list_to_file(clustering_info.ids,\
  make_filename(profiles_info, file_type="members", type_of_data="all"))
  
  make_html_set_view(clustering_info, members=clustering_info.high_signal, type_of_data="high_signal")
  write_members_list_to_file(clustering_info.high_signal,\
  make_filename(profiles_info, file_type="members", type_of_data="high_signal"))
  
  make_html_set_view(clustering_info, members=clustering_info.low_signal, type_of_data="low_signal")
  write_members_list_to_file(clustering_info.low_signal,\
  make_filename(profiles_info, file_type="members", type_of_data="low_signal"))
  
  for number in range(len(clustering_info.shape_clusters)):
    make_html_set_view(clustering_info, members=clustering_info.shape_clusters[number], type_of_data="shape_cluster", shape_number=number)
    write_members_list_to_file(clustering_info.shape_clusters[number],\
    make_filename(profiles_info, file_type="members", type_of_data="shape_cluster",shape_number=number))
  
  for number in range(len(clustering_info.shape_clusters_unflipped)):
    make_html_set_view(clustering_info, members=clustering_info.shape_clusters_unflipped[number], type_of_data="shape_cluster_unflipped", shape_number=number)
    write_members_list_to_file(clustering_info.shape_clusters_unflipped[number],\
    make_filename(profiles_info, file_type="members", type_of_data="shape_cluster_unflipped",shape_number=number))
  
  for number in range(len(clustering_info.group_clusters)):
    make_html_set_view(clustering_info, members=clustering_info.group_clusters[number], type_of_data="magnitude_group", group_number=number)
    write_members_list_to_file(clustering_info.group_clusters[number],\
    make_filename(profiles_info, file_type="members", type_of_data="magnitude_group",group_number=number))
    
  
