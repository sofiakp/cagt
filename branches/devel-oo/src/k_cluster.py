#!/bin/python
#####################################################################
# k_cluster.py
# Max Libbrecht
# Updated 7/10
#####################################################################



import sys
sys.path.append('../../')
from random import randrange
from copy import deepcopy
import logging
import traceback

from Pycluster import kcluster
from numpy import corrcoef
import numpy as np

from parameters import *

# def corr_dist(x,y):
#   ret = corrcoef(x,y)[0,1]
#   return float(ret)


# From http://yongsun.me/tag/python/
def kmeansPP(data, k):  
    'init k seeds according to kmeans++'  
    X = data.data
    n = len(data.ids)
    'choose the 1st seed randomly, and store D(x)^2 in D[]'  
    centers = [randrange(n)]  
    distance_matrix = corrcoef(X)+1
    D = distance_matrix[centers[0],:]
    for _ in range(k-1):
        bestDsum = bestIdx = -1  
        for i in range(n):  
            Dsum = np.sum( np.minimum(D, distance_matrix[i,:]) )  
            if bestIdx < 0 or Dsum < bestDsum:
              bestDsum, bestIdx = Dsum, i  
        centers.append(bestIdx)  
        D = np.minimum(D, distance_matrix[bestIdx,:])
        
    # Compute assignments based on the centers
    assignments = np.argmin( distance_matrix[:,centers], axis=1)
    for i in range(len(centers)):
      assignments[centers[i]] = i
      
    return deepcopy(list(assignments.flat))
    

#######################################################################
# k_cluster()
# -----------------------------------------------
# Simple wrapper on the kcluster function
#######################################################################
def k_cluster(data, num_clusters, npass=npass, dist='c'):
  # It doesn't make sense to cluster less than nclusters profiles
  assert(len(data.ids) > 0)
  if len(data.ids) <= num_clusters:
    return range(data.shape[0])
  
  if use_smoothed_correlation:
    try:
      # 5-value averaging
      smoothed = np.zeros(shape=data.data.shape)
      smoothed[:-2] += .15*data.data[2:]
      smoothed[:-1] += .2*data.data[1:]
      smoothed += .3*data.data
      smoothed[1:] += .2*data.data[:-1]
      smoothed[2:] += .15*data.data[:-2]
      data.data = smoothed
    except:
      print "Error when smoothing data; continuing without smoothing"
      logging.error("Error when smoothing data; continuing without smoothing")
      logging.error(str(error))
      logging.error(traceback.format_exc())
      traceback.print_exc()
      
  
  if use_kmeans_plus_plus:
    kmeanspp_assignment = kmeansPP(data, num_clusters)
    assignments, error, nfound = kcluster(data.data, nclusters=num_clusters, 
    method='m', dist=dist, npass=npass, initialid=kmeanspp_assignment)
  else:
    assignments, error, nfound = kcluster(data.data, nclusters=num_clusters, 
    method='m', dist=dist, npass=npass)
  
  # It happens occasionally that one of the clusters is empty
  # In that case, we'll remap the assignments so that there aren't
  # any gaps in the cluster numbers
  if len(list(set(assignments))) < num_clusters:
    allocated_numbers = list(set(assignments))
    reverse_map = {}
    for i in range(len(allocated_numbers)):
      reverse_map[allocated_numbers[i]] = i
    assignments = map(lambda x: reverse_map[x], allocated_numbers)
  
  return assignments
    
  