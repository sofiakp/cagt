
import scipy.stats
from parameters import *
from src.analysis.mutual_information import *
from src.ProfileInfo.ProfileInfo import *
from src.ClusteringInfo.ClusteringInfo import *




def get_distribution(clusters):
    return map(len, clusters)

def entropy(clusters):
    return scipy.stats.entropy(get_distribution(clusters))


def get_mutual_clusters(clusters1, clusters2):
    mutual_clusters = []
    for cluster1 in clusters1:
        for cluster2 in clusters2:
            new_cluster = list(set(cluster1).intersection(set(cluster2)))
            if len(new_cluster) > 0:
                mutual_clusters.append(new_cluster)
    mutual_clusters = sorted(mutual_clusters, cmp=lambda x,y: -cmp(len(x),len(y)))
    return mutual_clusters


def mutual_entropy(clusters1, clusters2):
    return entropy(get_mutual_clusters(clusters1, clusters2))


def mutual_information(clusters1, clusters2):
    H1 = entropy(clusters1)
    H2 = entropy(clusters2)
    H12 = mutual_entropy(clusters1,clusters2)
    MI = H1 + H2 - H12
    return H1,H2,H12,MI


def find_informative_pairs(profiles_info_list):
    informative_pairs = []
    for profiles_info1 in profiles_info_list:
        clustering_info1 = clustering_info_load(profiles_info1)
        for profiles_info2 in profiles_info_list:
            clustering_info2 = clustering_info_load(profiles_info2)

            entropy1, entropy2, mutual_entropy, mutual_information =\
            mutual_information(clustering_info1.shape_clusters, clustering_info2.shape_clusters)

            if mutual_information > mutual_information_cutoff:
                ProfilesInfoPair(profiles_info1, profiles_info2)
