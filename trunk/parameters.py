# todo: switch dimnames to np.array everywhere

#####################################################################
# Parameters
#####################################################################
# Set this to the location of the data. The file should have the following 
# format:
# value<TAB>value<TAB>...<TAB>value<NEWLINE>
# value<TAB>value<TAB>...<TAB>value<NEWLINE>
filename = "/Users/max/Code/histone_clustering/data/k562_H3k27ac_BroadCtcf.tab"

# CAGT runs in one of two modes, "normalize" and "group".  
#
# In normalize mode, CAGT considers only profiles with significant signal 
# (as defined by  cutoff_quantile and cutoff_value), and for each 
# profile, subtracts the mean and divides by the standard deviation.
# The resulting normalized clusters are clustered into
# normalize_num_clusters clusters. 
#
# In group mode, the profiles are not normalized in any way.  Instead,
# they are first divided into group_num_groups groups based on median
# signal.  Then each group is further clustered into group_num_clusters
# clusters.  
# 
# Below, all parameters are prefixed with the mode they apply to. 
#mode = "normalize"
mode = "group"


# Most profiles have no significant signal.  Since correlation
# is sensitive to noise, we want to throw out the low-signal 
# profiles and just cluster the rest. The code throws out all 
# profiles with cutoff_quantile-th quantile less than cutoff_value.
# For example, if cutoff_quantile is 0.5 and cutoff_value is 1,
# it throws out profiles with median signal less than 1.  
# I usually use cutoff_quantile=0.75, cutoff_value=2.0.
# Set cutoff_value=0 if you want to use all the profiles
normalize_cutoff_quantile = 0.75
normalize_cutoff_value = 2.0

# These parameters are passed to the k-medians algorithm.
# num_clusters determines the number of clusters the data is
# divided into (the "k" in k-medians).  
normalize_num_clusters = 5

# Graphical parameters.  These determine the limits of the plots
# produced.  For boxplots, points outside the range will be cut
# off.  For heatmaps, points outsie the range will appear as white.
# Good values for the boxplot limits are the 1% and 99% quantiles 
# of the signal.  The heatmap limits can generally be much more 
# restrictive, such as the 10% and 90% quantiles.
normalize_boxplot_lims = [-3,3]
normalize_heatmap_lims = [-2,2]

# These parameters guide the grouping in group mode.  The profiles
# are divided into group_num_groups by their group_by_quantile. 
group_num_groups = 3
group_by_quantile = .75

# See normalize_num_clusters above.
group_clusters_per_group = 3

# Graphical parameters.  These determine the limits of the plots
# produced.  For boxplots, points outside the range will be cut
# off.  For heatmaps, points outsie the range will appear as white.
# Good values for the boxplot limits are the 1% and 99% quantiles 
# of the signal.  The heatmap limits can generally be much more 
# restrictive, such as the 10% and 90% quantiles.
group_boxplot_lims = [0,15]
group_heatmap_lims = [0,5]

# Since k-medians is vulnerable to initial conditions, 
# the algorithm runs k-medians multiple times and reports the 
# solution with the best objective.  num_passes determines the 
# number of times k-medians is run.
num_passes = 3

