import sys
import traceback
from time import time

import numpy as np

import rpy2.robjects as rpy
r = rpy.r


# A DataMatrixMap is a map from integer IDs to vectors of data,
# backed by a numpy matrix.  Numpy matrices have the advantage of
# implementing storage and indexing efficiently -- this class
# just adds a level of indirection between the indices it's passed
# and the indices in the matrix itself. The matrix itself can still
# be accessed with DataMatrixMap.data
class MatrixMap:
    def __init__(self, data, ids):
        self.data = data
        self.ids = ids
        assert(len(ids) == data.shape[0])
        self.id_to_index = {}
        for i in range(len(ids)):
            self.id_to_index[self.ids[i]] = i

    def get_row(self, row_id):
        return self.data[self.id_to_index[row_id]].flat

    def get_rows(self, row_ids):
        indices = map(lambda id: self.id_to_index[id], row_ids)
        return MatrixMap(self.data[indices,:], row_ids)

    def __getattr__(self, name):
        return data.__getattr__[name]

    def set_row(self, row_id, value):
        self.data[self.id_to_index[row_id],:] = value


class logTime(object):
    """A decorator for timing a function"""
    def __init__(self, f):
        self.f = f
        self.name = f.__name__

    def __call__(self, *args, **kwargs):
        t = time()
        f(*args, **kargs)
        logging.debug("Took %s seconds for %s(%s , %s)" %
                      (time() - t, self.name, args, kwargs))


def opposite_ids(ids, all_ids):
    return filter(lambda i: i not in ids, all_ids)


def assignments_to_clusters(assignments, ids):
    assert(len(assignments) == len(ids))
    num_profiles = len(ids)
    clusters = list(set(assignments))
    assignment_indices = map(lambda cluster: filter(lambda i: assignments[i]==cluster, range(num_profiles)), clusters)
    assignment_ids = map(lambda cluster_indices: map(lambda i: ids[i], cluster_indices), assignment_indices)
    return assignment_ids

# def clusters_to_assignments(clusters):
#   num_clusters = range(len(clusters))
#   ids = reduce(lambda x,y: x+y, clusters).sorted()
#   assignments = [-1]*len(ids)
#   for
#
#   return assignments, ids

def quantile(arr, q):
    return sorted(arr)[int(len(arr)*q)]

def find_in_list(list, item):
    for i in range(len(list)):
        if list[i] == item:
            return i
    print "find_in_list: not found!"
    return None

def log_error(name, args, error):
    """Prints (to stderr and logging.error) information about an error.
    Prints the function name, its arguments (as passed to log_error),
    and a stack trace."""
    logging.error("Hit error in function %s" % name)
    logging.error("arguments: %s" % args)
    logging.error("error: %s" % str(error))
    logging.error(traceback.format_exc())


# def map_indices(indices, mapping):
#   return map(lambda i: mapping[i], indices)

# def map_indices_backwards(indices, mapping):
#   return map(lambda i: find_in_list(mapping, i), indices)

# def map_assignments(assignments, mapping, num_peaks):
#   mapped_assignments = [-1]*num_peaks
#   for i in range(len(assignments)):
#       mapped_assignments[mapping[i]] = assignments[i]
#   return mapped_assignments


def transpose(m):
    return map(list,zip(*m))

def get_assignment_indices(assignments):
    clusters = sorted(list(set(assignments)))
#   num_clusters = len(list(set(assignments)))
    num_profiles = len(assignments)
    return map(lambda cluster: \
    np.array(filter(lambda i: assignments[i]==cluster, range(num_profiles))), \
#   range(num_clusters))
    clusters)

def index_r_data(r_data, indices):
    # R is 1-indexed
    r_indices = rpy.IntVector(map(lambda x:x+1, indices))
    rpy.globalenv['indices'] = r_indices
    rpy.globalenv['data'] = r_data
    return r('data[indices,]')


def partition_by_identifier(lst, get_identifier):
    """Takes a list of arbitrary objects, and returns a partition
    (list of lists) that groups the objects that have the
    same output of get_identifier (that is, if
    get_identifier(A) == get_identifier(B), A and B will be
    grouped together)"""
    uniq_identifiers = list(set(map(get_identifier, lst)))
    def same_identifier_gen(id):
        return lambda x: x == id
    map(lambda id: filter(same_identifier_gen(id), lst), uniq_identifiers)

