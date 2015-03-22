## Code structure ##
Currently the code consits of MATLAB functions for CAGT clustering and R scripts for plotting the results. This section gives a very brief summary of the code, for a detailed description of the input parameters, see [Running cagt](Manual#Running_cagt.md). All the code is thoroughly commented, so if you're experienced with MATLAB, feel free to browse it. You can also access documentation using (in MATLAB) `help function_name`.

  * `clusterSignal` runs CAGT clustering and writes the results in `mat` files.
  * `cagt` is a wrapper function around `clusterSignal` that can also produce text output (including the output required to use the R plotting code). If you're not very experienced with MATLAB, it is recommended to use `cagt` instead of calling `clusterSignal` directly.
  * `simpleKmeans` runs k-means or k-medians on a matrix.
  * `hierarchicalClust` gets a set of existing clusters and merges them using hierarchical agglomerative clustering, with optional "flipping" of mirrored clusters.
  * `writeTextResults` writes the clustering results in a BED-like format.
makeSignalTable writes a text file with the mean signal and the signal percentiles in all clusters. It can also compute the mean signal of other datasets (i.e. not the one on which clustering was done) in the same set of clusters. This is useful for studying the associations between different types of signals.
  * `plot.cagt.multivariate.figs.R`: Code for plotting the clustering results with many customization options. See also [Plotting](Plotting.md).

## CAGT input ##

`cagt` runs CAGT clustering on the signal around a set of loci of interest. It reads data from a file in MATLAB's `mat` format. The input file must contain the following variables:
  1. intervalData: dataset array with fields:
    * chr (nominal) : chromosome names
    * start (double): start positions (1-based)
    * stop (double): stop positions (1-based)
    * strand (nominal): +/-
  1. signal: N-by-P matrix where N is the number of intervals. The i-th row should contain the signal (e.g. (normalized) intensity of a histone modification, TF binding, nucleosome positioning) in the corresponding interval. Clustering will therefore be applied on the rows of the signal matrix.

You can create the MATLAB structures any way you like. Assuming that you have a set of genomic intervals in BED format (or something equivalent) and mapped reads in BAM or tagAlign format, you can create the input files for CAGT as follows:
  1. Compute (normalized, smoothed etc) read counts along the genome using [align2rawsignal](http://code.google.com/p/align2rawsignal/).
  1. Extract the signal aroung the genomic intervals using [extractSignal](http://code.google.com/p/extractsignal/). `extractSignal` produces exactly the structures expected by `cagt`. **Remember to use the parameter `-ov=signal` in order to obtain a .mat file that is compatible with CAGT**

## Running cagt ##

`cagt(INFILE)` runs CAGT clustering on the data read from INFILE and writes the results in the current directories. INFILE should be a mat file containing the structures described above. CAGT writes the following output files:
  1. cagt\_params.mat: Calling parameters
  1. cagt\_results.mat: Results of clusterSignal.
  1. cagt\_clusters.bed: BED file with the assignments of elements to clusters. The format of this file is described [here](OuputFormats#BED_files.md).
  1. cagt\_clusterData.txt: Cluster signal. The format of this file is described [here](OuputFormats#clusterData.md).

You can specify additional parameter-value pairs using a syntax `cagt(INFILE, 'param1', value1, 'param2', value2, ...)`. The accepted parameter-value pairs are described below.

### Output parameters ###
  * **od**: output directory. Default: working directory.
  * **op**: prefix of output files. Default: 'cagt`_`'. Output files will be `<op>params.mat, <op>results.mat, <op>clusterData.txt, <op>clusters.bed`.
  * **tt**: target type. Used for labeling the results in the clusterData output file. Default: 'TARGET'.
  * **st**: signal type. Used for labeling the results in the clusterData output file. Default: 'SIGNAL'.
  * **bed**: Write BED output. Default: true.
  * **txt**: Write clusterData.txt output. Default: true.
  * **overwrite**: If set to false, then CAGT won't overwrite any output files (result, BED, or clusterData), if files with the same name already exist in the output directory. Default false.
  * **display**: Determines how much output will be printed. Choices are:
    * 0 - No output.
    * 1 - Output only after the last iteration (default).
    * 2 - Output at each iteration.

### Signal filtering parameters ###
  * **maxNan**: rows with more than that number of NaN's will be removed. Set to 0 if you want to keep all rows. Default: ceil(.5 `*` size(signal, 2)).
  * **lowSignalCut/lowSignalPrc**: Remove rows whose lowSignalPrc-th percentile is less than lowSignalCut. Defaults are 0 for lowSingalCut and 90 for lowSignalPrc.
  * **lowVarCut**: rows with variance less than lowVarCut will be removed. Useful when the distance metric used is correlation-based. Default: 0.
  * **nanTreat**: how to treat NaN's in the signal. Possible values:
    * 'zero': replace with zeros.
    * 'interpolate': use linear interpolation to interpolate missing values (default).

### Distance metric parameters (apply to both clustering stages) ###

  * **distance**: Distance function, that K-means should minimize with respect to.  Choices are:
    * 'sqeuclidean'  - Squared Euclidean distance (default)
    * 'correlation'  - One minus the sample correlation between points (treated as sequences of values)
    * 'xcorr'        - One minus the maximum sample cross-correlation over all possible lags (see the option 'maxlag')
  * **avgFun**: Method for computing cluster centroids. Choices are 'mean', 'median'. Default: mean.
  * **maxlag**: Maximum lag when xcorr is used as the distance measure. Otherwise maxlag will be set to 0 and the value passed will be ignored.

### k-means/medians parameters ###
  * **k**: number of clusters for k-means/medians. Default: 40.
  * **start**: Method used to choose initial cluster centroid positions, sometimes known as "seeds".  Choices are:
    * 'plus'   -  k-means++ initialization (default).
    * 'sample' -  Select k observations from X at random.
    * matrix   -  A k-by-P matrix of starting locations.  In this case, the k parameter can be omitted, and K will be inferred from the first dimension of the matrix. You can also supply a 3D array, implying a value for replicates from the array's third dimension.
  * **replicates**: Number of times to repeat the clustering, each with new set of initial centroids.  Default is 1.
  * **emptyaction**: Action to take if a cluster loses all of its member observations.  Choices are:
    * 'error'     - Treat an empty cluster as an error (default)
    * 'drop'      - Remove any clusters that become empty, and set the corresponding values in C and D to NaN.
    * 'singleton' - Create a new cluster consisting of the one observation furthest from its centroid.
  * **maxiter**: Maximum number of iterations. Default: 100.
  * **online**: Flag indicating whether an "on-line update phase should be performed in addition to a "batch update" phase.  The on-line phase can be time consuming for large data sets, but guarantees a solution that is a local minimum of the distance criterion, i.e., a partition of the data where moving any single point to a different cluster increases the total sum of distances. **NOT SUPPORTED YET**. Default: false.

### Hierarchical clustering parameters ###
  * **merge**: Set to false if you do not want to apply hierarchical agglomerative clustering. Default:true.
  * **mergeK**: final number of clusters after hierarchical agglomerative clustering. Default is 1 so merging will continue until there's only 1 cluster. k cannot be greater than m, the number of input clusters.
  * **mergeDist**: maximum distance for merging. Merging will stop if the distance between the two closest centroids is greater than maxDist, or if the number of clusters reaches k. Default Inf.
  * **flip**: Whether flipping will be allowed or not. If flipping is allowed both an observation and its reversed (i.e. taking the P features from end to start) will be considered when looking for the closest cluster. Default: true (flipping allowed).