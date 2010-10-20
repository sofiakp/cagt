
import scipy.stats 


def get_distribution(assignments):
	return map(lambda c:\
	len(filter(lambda a: a==c, assignments)),\
	sorted(list(set(assignments))))

def entropy(assignments):
	return scipy.stats.entropy(get_distribution(assignments))	

def get_mutual_assignments(assignments1, assignments2):
	num_clusters1 = len(list(set(assignments1)))
	def make_new_cluster_number(cluster1, cluster2):
		return cluster1 + num_clusters1*cluster2
	return map(\
	lambda i: make_new_cluster_number(assignments1[i], assignments2[i]),\
	range(len(assignments1)))

def mutual_entropy(assignments1, assignments2):
	return entropy(get_mutual_assignments(assignments1, assignments2))

def mutual_information(assignments1, assignments2):
	H1 = entropy(assignments1)
	H2 = entropy(assignments2)
	H12 = mutual_entropy(assignments1,assignments2)
	MI = H1 + H2 - H12
	return H1,H2,H12,MI
#	return entropy(get_distribution(assignments1)) +\
#	entropy(get_distribution(assignments1)) -\
#	entropy(get_distribution(get_mutual_assignments(assignments1,assignments2)))