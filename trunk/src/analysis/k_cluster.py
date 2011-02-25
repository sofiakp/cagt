#!/bin/python
#####################################################################
# k_cluster.py
# Max Libbrecht
# Updated 7/10
#####################################################################



import sys
sys.path.append('../../')

from parameters import *

from Pycluster import kcluster
from numpy import corrcoef


# From http://yongsun.me/tag/python/
def kmeansPP(data, k):  
    'init k seeds according to kmeans++'  
    X = data.data
    n = len(data.ids)
    'choose the 1st seed randomly, and store D(x)^2 in D[]'  
    centers = [X[randint(n),:]]  
    D = [corrcoef(x,centers[0]) for x in X]  
    for _ in range(k-1):  
        bestDsum = bestIdx = -1  
        for i in range(n):  
            'Dsum = sum_{x in X} min(D(x)^2,||x-xi||^2)'  
            Dsum = reduce(lambda x,y:x+y,  
                          (min(D[j], corrcoef(X[j,:],X[i,:])) for j in xrange(n)))  
            if bestDsum < 0 or Dsum < bestDsum:  
                bestDsum, bestIdx  = Dsum, i  
        centers.append (X[bestIdx,:])  
        D = [min(D[i], corrcoef(X[i,:],X[bestIdx,:])) for i in xrange(n)]  
        
    # Compute assignments based on the centers
    assignments = None
    def nearest_center(index):
      x = X[index,:]
      return min( map(lambda i: (i, corrcoef(x, centers[i])), range(k)), 
                  cmp=lambda a,b: cmp(a[1],b[1]) )[0]
    
    return map(nearest_center, range(n))


#######################################################################
# k_cluster()
# -----------------------------------------------
# Simple wrapper on the kcluster function
#######################################################################
def k_cluster(data, num_clusters, npass=npass, dist='c'):
	# It doesn't make sense to cluster less than nclusters profiles
	assert(len(data.ids) > 0)
	if len(data.ids) < num_clusters:
		return range(data.shape[0])
	assignments, error, nfound = kcluster(data.data, nclusters=num_clusters, method='m', dist=dist, npass=npass)
	
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
		
	