
import scipy.stats 

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
