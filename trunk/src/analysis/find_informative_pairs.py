
from src.analysis.mutual_information import *
from src.ProfileInfo.ProfileInfo import *
from src.ClusteringInfo.ClusteringInfo import *


def find_informative_pairs(profiles_info_list):
	informative_pairs = []
	for profiles_info1 in profiles_info_list:
		clustering_info1 = clustering_info_load(profiles_info1)
		for profiles_info2 in profiles_info_list:
			clustering_info2 = clustering_info_load(profiles_info2)

			entropy1, entropy2, mutual_entropy, mutual_information =\
			mutual_information(clustering_info1.shape_clusters, clustering_info2.shape_clusters)

			if mutual_information > profiles_info_list.args.mutual_information_cutoff:
				ProfilesInfoPair(profiles_info1, profiles_info2)
