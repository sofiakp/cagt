#####################################################################
# Parameters
#####################################################################

from time import time

# Absolute path to the folder that contains the cagt/ folder.
histone_profiles_path = "/abighd/mlibbrecht/histone_profiles/"

# CAGT will look in cagt/data/profiles_<cell_line> for the data.
cell_line = "K562"

# CAGT 
peak_tags = ["TSS_all","TSS_high_confidence","TSS_high_medium_confidence","Pol2"]
#peak_tags = ["CTCF","Nrsf","P300","Nfkb","Pol2","Max","Cfos"]
#peak_tags = ["Nrsf","P300"]
signal_tags = ["DNase_Crawford","DNase_Stam"]
#peak_tags = ["Cfos","P300","Cmyc","Nrsf","Pol2","CTCF"]
#signal_tags = ["H3K4me1","H3K4me2","H3K4me3","H3K9ac","H3K9me1",\
#"H3K27ac","H3K27me3","H3K36me3","H4K20me1","DNAase","FAIRE","CTCF"]
#peak_tags = ["P300","Nrsf"]
#signal_tags = ["H3K4me2","H3K4me1"]


####################################################
# Clustering parameters
# --------------------------------------------

# Most profiles have no significant signal.  Since correlation
# is sensitive to noise, we want to throw out the low-signal 
# profiles and just cluster the rest. The code throws out all 
# profiles with cutoff_quantile-th quantile less than cutoff_value.
# For example, if cutoff_quantile is 0.5 and cutoff_value is 1,
# it throws out profiles with median signal less than 1.  
# I usually use cutoff_quantile=0.75, cutoff_value=2.0.
# Set cutoff_value=0 if you want to use all the profiles
low_signal_cutoff_quantile = 0.9
low_signal_cutoff_value = 5.0

# These parameters guide the cluster merging.  k-means will cluster
# the profiles into cluster_then_merge_num_clusters, then merge all
# clusters with correlation greater than cluster_merge_correlation_cutoff.
cluster_then_merge_num_clusters = 40
cluster_merge_correlation_cutoff = .6

# These parameters guide the grouping.  Each cluster is
# are divided into group_num_groups by their group_by_quantile for 
# magnitude-grouped plotting.
num_groups = 4
group_by_quantile = 0.9
group_quantile_bounds = [.1,.9]

# K-means clustering will run for npass iterations and pick 
# the best (optimal objective value) clustering from those runs.
# High values of npass make CAGT run slower, but produce slightly
# better clustering.  
npass = 1


####################################################
# Graphical parameters
# --------------------------------------------

# Y-axis limits of the boxplots.  CAGT plots all boxplots on the same y limits
# so that they're easily comparable. 
ylims = [0,50]

# Y-axis limits for normalized profiles.  
normalize_ylims = [-4,4]

####################################################
# make-html parameters
# --------------------------------------------

# On the correlations page, all correlations will be shown with significance
# greater than correlation_significance_cutoff
correlation_significance_cutoff = 0.1


####################################################
# Deprecated parameters
# --------------------------------------------

#gene_proximity_distance = 10000
#shape_num_clusters = 7

profile_window_size = 1255
profile_bin_size = 10

# For make_bed_file_map
bed_file_map_resolution = 10000


normalize_heatmap_ylims = [-2,2]



