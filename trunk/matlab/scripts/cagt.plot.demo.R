rm(list=ls())
source('./plot.cagt.multivariate.figs.R')
input.dir <- '../data/test/'
output.dir <- input.dir
all.cagt.table.filenames <- list.files(path=input.dir, pattern="nucleo_around_ctcf_multi_clusterData.txt", full.names=T) # Get names of cagt plot names

# This code assumes you are in <CAGT root>/matlab/scripts and you have already generated the 
# test data with cagtDemo.m.

for (i in all.cagt.table.filenames) {
  cat(i,"\n")
  plot.cagt.multivariate.figs(cagt.table.filename = i,
                              output.dir = output.dir,
                              output.file = NULL, # Let it name the figures
                              output.format = "png",
                              support.thresh = 0.02, # remove shapes whose support is < .02 * fraction of peaks in high signal component
                              orient.shapes = T, # If required invert shapes to make them Low (left) to High (right)                                        
                              replace.flag = T, 
                              partner.marks = 'SIGNAL', # Only plot the signal used for clustering without partner marks
                              zscore = F, # Use the original scale and not the standardized signal.
                              common.scale = T, # All plots on a common scale
                              plot.over = T, # plot them all on the same plot or one below the other
                              whiskers = T, # Plot percentile whiskers around the cluster signal.
                              mag.shape = "all" # Plot both the clusters and the averaged aggregation plots. 
                              )
  plot.cagt.multivariate.figs(cagt.table.filename = i,
                              output.dir = output.dir,
                              output.format = "png",
                              output.file = NULL,
                              support.thresh = 0.02,
                              orient.shapes = T, 
                              replace.flag = T,
                              partner.marks = 'all', 
                              zscore = F,
                              common.scale = F, 
                              plot.over = F,
                              whiskers = F,
                              mag.shape = "all"
                              )
}