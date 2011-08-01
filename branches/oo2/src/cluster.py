
import sys
import os
from time import time
from random import randrange
from copy import deepcopy
import logging
import traceback
import traceback
from math import sqrt
from copy import deepcopy
import itertools
import uuid

from Pycluster import kcluster
from numpy import corrcoef
import numpy as np

from src.utils import *
from src.utils import get_assignment_indices
from src.filenames import *
from src.ClusteringInfo import ClusteringInfo, clustering_info_dump, clustering_info_load
from src.boxplot import boxplot_simple

# TODO: Give all ClusteringResults the right priority

class ClusteringResult(object):
    """A generalized result of a clustering"""
    def __init__(self, ids, partition, profiles_info):
        self.ids, self.partition, self.profiles_info = ids, partition, profiles_info
        self.index = {}
        for cluster_id in self.cluster_id_iter():
            for id in self.cluster_members(cluster_id):
                self.index[id] = cluster_id

        # Don't overuse this -- give things real unique names instead
        # (Currently only used for generic ClusteringResults)
        self.uuid = uuid.uuid1()

    def cluster_id_iter(self):
        for i in range(len(self.partition)):
            yield i

    def name(self):
        return "Unnamed Clustering"

    def handle(self):
        """Used in filenames etc"""
        return "unnamed_clustering_%s" % self.uuid

    def cluster_handle(self, cluster_id):
        return str(cluster_id)

    def cluster_name(self, cluster_id):
        return "%s cluster: %s" % (self.name(), cluster_id)

    def cluster_members(self, cluster_id):
        return self.partition[cluster_id]

    def html_view_priority(self):
        """In html views, ClusteringResults are ordered by
        html_view_priority, higher values first"""
        return 0

    def html_view_title(self):
        return self.name()

    def boxplot_title(self, cluster_id):
        num_members = len(self.cluster_members(cluster_id))
        percentage = int(100*float(num_members)/len(self.ids))
        return "%s -- %s members (%s%%)" % \
               (self.cluster_name(cluster_id),
                num_members, percentage)
        return self.cluster_name(cluster_id)

    def boxplot_ylims(self, cluster_id):
        return self.profiles_info.ylims

    def data_for_plotting(self, PD, cluster_id):
        ids_for_plotting = self.cluster_members(cluster_id)
        return PD.data.get_rows(ids_for_plotting)

    def ylab(self, cluster_id):
        return "Normalized signal"

    def boxplot_make_verticle_line_in_middle(self, cluster_id):
        return True

    def boxplot_make_horizontal_line_at_origin(self, cluster_id):
        return True

    def write_assignments(self):
        filename = make_filename('clustering_result', 'assignments', clustering_result=self)
        f = open(filename, 'w')
        for id in self.ids:
            f.write('%s ' % self.cluster_id_handle(index[id]))

    def make_html_view(self):
        filename = make_filename('clustering_result', 'html_view', clustering_result=self)
        f = open(filename, 'w')
        f.write('<html><body>')
        f.write('<h1>%s</h1>' % self.html_view_title())
        f.write('<a href=%s>Assignments...</a>' %
                make_filename('clustering_result', 'assignments',
                              clustering_result=self,
                              relative_to=filename))
        for cluster_id in self.cluster_id_iter():
            f.write('<img src=%s>' %
                    make_filename('cluster', 'boxplot',
                                  clustering_result=self,
                                  cluster_id=cluster_id,
                                  relative_to=filename))
        f.write('</html></body>')

    def make_plots(self, PD):
        for cluster_id in self.cluster_id_iter():
            boxplot_simple(self, PD, cluster_id)



class OversegmentedClusteringResult(ClusteringResult):
    """Result of Oversegmenting Clustering"""
    def __init__(self, partition, ids, profiles_info):
        super(OversegmentedClusteringResult, self).__init__(partition, ids, profiles_info)

    def name(self):
        return "Oversegmented"
    def handle(self):
        return "oversegmented"



class UnflippedClusteringResult(ClusteringResult):
    """Result of Unflipped Cluster-and_Merge"""
    def __init__(self, partition, ids, profiles_info):
        super(UnflippedClusteringResult, self).__init__(partition, ids, profiles_info)

    def name(self):
        return "Unflipped"
    def handle(self):
        return "unflipped"




class FlippedClusteringResult(ClusteringResult):
    """Result of Flipped Cluster-and-Merge"""
    def __init__(self, partition, ids, profiles_info, flipped):
        super(FlippedClusteringResult, self).__init__(partition, ids, profiles_info)
        self.flipped = flipped

    def name(self):
        return "Flipped"
    def handle(self):
        return "flipped"


    # TODO: flip data for plotting

class GroupingResults(ClusteringResult):
    """Result of group-by-magnitude"""
    def __init__(self, partition, ids, profiles_info, ):
        super(FlippedClusteringResult, self).__init__(partition, ids, group_cutoffs)
        self.group_cutoffs = group_cutoffs

    def name(self):
        return "Magnitude groups"
    def handle(self):
        return "grouped"


class ShapeAndGroupResults(ClusteringResult):
    """ClusteringResult for cluster and group intersection"""
    def __init__(self, shape_clustering, group_clustering):
        # TODO
        ids = shape_clustering.ids
        partition = shape_clustering.partition
        super(ShapeAndGroupResults, self).__init__(partition, ids)

    def cluster_handle(self, cluster_id):
        return "group_and_shape_%s" % cluster_id
    def name(self):
        return "Shape and magnitude"





def cluster_then_merge(clustering_info, PD):
    profiles_info = clustering_info.profiles_info
    norm_data = PD.high_signal_norm_data
    args = clustering_info.profiles_info.args
    num_groups = clustering_info.profiles_info.args.num_groups
    ids = norm_data.ids
    if len(norm_data.ids) < 5:
        flipped_clusters = assignments_to_clusters([0]*len(norm_data.ids), norm_data.ids)
        unflipped_clusters = assignments_to_clusters([0]*len(norm_data.ids), norm_data.ids)
        oversegmented_clusters = assignments_to_clusters([0]*len(norm_data.ids), norm_data.ids)
        flipped = []
    else:
        t0 = time()
        oversegmented_assignments = k_cluster(norm_data, num_clusters=args.cluster_then_merge_num_clusters, npass=args.npass, args=args)
        oversegmented_partition = assignments_to_clusters(oversegmented_assignments, norm_data.ids)
        oversegmented_clustering = OversegmentedClusteringResult(ids, oversegmented_partition, profiles_info)

        unflipped_partition, _ = hcluster(norm_data, oversegmented_partition, args, flipping=False)
        unflipped_clustering = UnflippedClusteringResult(ids, unflipped_partition, profiles_info)

        if clustering_info.profiles_info.flip:
            flipped_partition, flipped = hcluster(norm_data, unflipped_partition, args, flipping=True)
        else:
            flipped_partition = unflipped_partition
            flipped = []
        flipped_clustering = FlippedClusteringResult(ids, flipped_partition, profiles_info, flipped)


    clustering_info.shape_clusters = flipped_clustering
    clustering_info.shape_clusters_unflipped = unflipped_clustering
    clustering_info.shape_clusters_oversegmented = oversegmented_clustering
    clustering_info.flipped = flipped
    clustering_info.clusterings += [oversegmented_clustering, unflipped_clustering, flipped_clustering]
    return oversegmented_clustering, unflipped_clustering, flipped_clustering


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


def k_cluster(data, num_clusters, npass, args, dist='c'):
    # It doesn't make sense to cluster less than nclusters profiles
    assert(len(data.ids) > 0)
    if len(data.ids) <= num_clusters:
        return range(len(data.ids))

    if args.use_smoothed_correlation:
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
    if args.use_kmeans_plus_plus:
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


def medians(data):
    return np.apply_along_axis(lambda col: sorted(col)[int(len(col)*0.5)], 0, data.data)


def euc(profile1, profile2):
    dist = 0.0
    for i in range(len(profile1)):
        dist += (profile1[i]-profile2[i])**2
    return sqrt(dist) / len(profile1)

def correlation_with_flipping(profile1, profile2):
    cors = []
    cors.append((False,False,corrcoef(profile1,profile2)[0][1]))
    cors.append((True,False,corrcoef(profile1[::-1],profile2)[0][1]))
    cors = sorted(cors, cmp=lambda x,y: -cmp(x[2],y[2]))
    return cors[0]


def hcluster(norm_data, clusters, args, flipping=False, cluster_merge_correlation_cutoff=None):
    if cluster_merge_correlation_cutoff is None:
        cluster_merge_correlation_cutoff = args.cluster_merge_correlation_cutoff
    t1 = time()
    # clusters = get_assignment_indices(clustering_assignments)
    cluster_medians = map(lambda ids: medians(norm_data.get_rows(ids)), clusters)
    flipped = set()

    clusters = deepcopy(clusters)

    t5 = time()
    # We're going to re-impliment heirarchical clustering here.
    # It's frustrating, but since we want to change all the clusters
    # after each pass, I don't think we can use any of the packages.
    # We won't do it very efficiently, but it doesn't matter since there
    # aren't too many clusters at this point.
    while True:
        if len(clusters) <= 1:
            break
        pairs = []
        for cluster1 in range(len(clusters)):
            for cluster2 in range(cluster1+1, len(clusters)):
                pair = {}
                pair['c1'] = cluster1
                pair['c2'] = cluster2

                if flipping:
                    pair['c1_flipped'], pair['c2_flipped'], pair['cor'] =\
                    correlation_with_flipping(cluster_medians[cluster1],cluster_medians[cluster2])
                else:
                    pair['c1_flipped'] = False
                    pair['c2_flipped'] = False
                    pair['cor'] = corrcoef(cluster_medians[cluster1],cluster_medians[cluster2])[0][1]

                pairs.append(pair)

        pairs = sorted(pairs, cmp=lambda x,y: -cmp(x['cor'],y['cor']))

        if len(pairs) < 1:
            break
        if pairs[0]['cor'] < cluster_merge_correlation_cutoff:
            break

        c1 = pairs[0]['c1']
        c2 = pairs[0]['c2']
        new_cluster = clusters[c1] + clusters[c2]
        new_cluster_medians = medians(norm_data.get_rows(new_cluster))

        if pairs[0]['c1_flipped']:
            for i in clusters[c1]:
                if i in flipped:
                    flipped -= set([i])
                else:
                    flipped |= set([i])
        if pairs[0]['c2_flipped']:
            for i in clusters[c2]:
                if i in flipped:
                    flipped -= set([i])
                else:
                    flipped |= set([i])

        # Since we're deleting out of a list, we have to make sure to delete
        # the higher-index element first
        # Also, after this point, all of our indices into these lists are invalid
        del clusters[c2]
        del clusters[c1]
        del cluster_medians[c2]
        del cluster_medians[c1]


        clusters.append(new_cluster)
        cluster_medians.append(new_cluster_medians)


    # Flip clusters so the higher-magnitude side is on the right
    for i in range(len(clusters)):
        cluster_medians = medians(norm_data.get_rows(clusters[i]))
        midpoint = int(len(cluster_medians)/2)
        left_magnitude = sum(cluster_medians[:midpoint])/len(cluster_medians[:midpoint])
        right_magnitude = sum(cluster_medians[midpoint:])/len(cluster_medians[midpoint:])
        if left_magnitude > right_magnitude:
            flipped = flipped.symmetric_difference(set(clusters[i]))


    # Sort clusters in descending order of size
    clusters = sorted(clusters, cmp=lambda x,y: -cmp(len(x),len(y)))

    return clusters, sorted(list(flipped))


def assign_to_group(val, cutoffs):
    group = 0
    for cutoff in cutoffs:
        if val <= cutoff:
            break
        group += 1
    return group


def group_by_magnitude(clustering_info, PD):
    num_groups = clustering_info.profiles_info.args.num_groups
    group_by_quantile = clustering_info.profiles_info.args.group_by_quantile
    group_quantile_bounds = [clustering_info.profiles_info.args.group_quantile_lower_bound, clustering_info.profiles_info.args.group_quantile_upper_bound]
    group_quantile_lower_bound = clustering_info.profiles_info.args.group_quantile_lower_bound
    group_quantile_upper_bound = clustering_info.profiles_info.args.group_quantile_upper_bound

    data = PD.high_signal_data
    if len(data.ids) < 5:
        clustering_info.group_cutoffs = [0.0]*num_groups
        clustering_info.group_clusters = assignments_to_clusters([0]*len(data.ids), data.ids)
        return

    quantiles = map(lambda id: quantile(np.array(data.get_row(id)), group_by_quantile),\
    data.ids)

    lower_bound = sorted(quantiles)[int(len(quantiles)*group_quantile_bounds[0])]
    upper_bound = sorted(quantiles)[int(len(quantiles)*group_quantile_bounds[1])]

    rng = upper_bound-lower_bound
    cutoffs = map(lambda i: lower_bound+rng*i/(num_groups+1), range(1,num_groups))
    clustering_info.group_cutoffs = cutoffs

    clustering_info.group_clusters =\
    assignments_to_clusters(map(assign_to_group, quantiles,\
    itertools.repeat(cutoffs,len(quantiles))), data.ids)

    return
