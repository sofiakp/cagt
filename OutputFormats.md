### mat files ###
`cagt` writes all the clustering results in a `.mat` file. See the documentation of `clusterSignal` for a description of the contents of this file. `cagt` also writes all input parameters (including those that were set automatically to default values) in a separate `.mat` file for future reference.

### Text files ###
`cagt` also writes the clustering results in two text files: a [BED-like](OutputFormats#BED_files.md) file with the assignment of signals to clusters; and a [clusterData](OutputFormats#clusterData.md) file which gives the mean signal in each cluster.

If you don't plan to use the the text files you can skip writing them, using the `bed` and `txt` [parameters](Manual#Output_parameters.md) of `cagt`. This will save time and storage space.

#### BED files ####
The first 6 columns of this file follow the standard [BED](http://genome.ucsc.edu/FAQ/FAQformat.html#format1) format. Columns 7-9 contain respectively:
  * **flip indicator**: is 1 if the signal belongs to a cluster that was flipped during hierarchical agglomerative clustering and 0 otherwise.
  * **k-means/medians index**: index of the cluster to which the signal was assigned during k-means/medians clustering. The first cluster is 1. A cluster index of 0 means that this element was filtered out prior to clustering. (See the [filtering](Manual#Signal_filtering_parameters.md) options of `cagt`).
  * **Hierarchical clustering index**: index of the cluster to which the signal was assigned during hierarchical agglomerative clustering. The first cluster is 1. A cluster index of 0 means that this element was filtered out prior to clustering.

#### clusterData ####
This file contains the discovered shapes. The first three lines comprise the header. The first line has "long" names of signals and the second line "shorter" versions (although this is not enforced in any way).

There is one line for each position of the signal in each cluster. Therefore, if CAGT discovered 10 clusters, and the length of the clustered intervals is 100bp (that is, the input matrix had 100 columns), there would be 10\*100 = 1000 lines in the file describing the signal (plus some extra lines for the aggregation over all clusters, see below).

  * The first two columns, **TF** and **Mark**, are identical in all rows. These are descriptive names of the input signal and the input set of intervals. These correspond to the `tt` and `ts` [options](Manual#Output_parameters.md) of `cagt`. Right now, the TF name isn't used anywhere in the code. The MARK name can be used by the [plotting code](Plotting.md) for labeling the plots.
  * **Pos**: The index inside the interval. For example, if your input intervals have length 100bp, this should be a number from 1 to 100. (Although it doesn't have to be: for example, using `makeSignalTable` you can set this range to be, say, -50,-49,...,0,1,...49, if you want your plots to be centered around 0).
  * **Cluster**: The name of the cluster. For example, if CAGT discovered 10 cluster, this should take values shape1, shape2,..., shape10. "all" refers to the signal aggregated over all input elements. "high" is the signal aggregated over all elements that passed the filtering cutoffs, and "low" is the signal over the elements that did not pass the cutoffs (see also [Plotting](Plotting.md)).
  * **Prctile**: For the "all" cluster, this is the number of elements clustered (number of rows in the input matrix). For the other clusters, this is the size of the cluster, as a percentage of the total number of elements.
  * The columns corresponding to headers Mark (in the second row) and SIGNAL (in the third row) give the mean and percentiles (third rows Mean, **LowPrc**, and **HighPrc**) of the signal in the position specified in the Pos column. The columns **MeanNorm**, **LowPrcNorm**, and **HighPrcNorm**, refer to the standardized signal. By default, the percentiles reported are the 10-th and 90-th percentiles of the signal. However, you can control this behavior if you make the table by calling `makeSignalTable` directly.
  * All other columns are optional and refer to the aggregation of some other signal in the same clusters.

For example, consider the table below that shows the (partial) results of clustering the nucleosome positioning signal around CTCF binding sites:

| #TF | Mark | Cluster | Prctile | Pos | Mark | BroadInstituteH3K9AC | Mark | BroadInstituteH3K9AC | Mark | BroadInstituteH3K9AC |
|:----|:-----|:--------|:--------|:----|:-----|:---------------------|:-----|:---------------------|:-----|:---------------------|
| #TF | Mark | Cluster | Prctile | Pos | SIGNAL | H3K9AC | SIGNAL | H3K9AC | SIGNAL | H3K9AC|
| #TF | Mark | Cluster | Prctile | Pos | Mean | Mean | LowPrc | LowPrc | HighPrc | HighPrc |
| CTCF | NUCLEOSOME | shape4 | 2.10 | 82 | 0.5421 | 20.9714 | 0.0000 | 0.4600 | 1.4600 | 64.2400 |
| CTCF | NUCLEOSOME | shape4 | 2.10 | 83 | 0.4789 | 21.1952 | 0.0000 | 0.4200 | 1.3400 | 65.8600 |

Cluster 4 contains 2.1% of all input genomic regions. The average signal at position 82 of cluster 4 is 0.5421, and the 90-th percentile is 1.46. If we consider the H3K9AC signal across the same set of genomic regions in cluster 4, the average signal at position 82 is 20.9714.