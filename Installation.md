### MATLAB version ###
The code consists of a set of MATLAB scripts, you will therefore need an installation of MATLAB. If you want to use our R code for plotting the clustering results, you will also need to have R installed.

The MATLAB code was developed using MATLAB R2011b. The R plotting code was developed using R versions 2.13-2.15 and requires the ggplot2 and reshape libraries.
All the code was developed on 64-bit Linux.

The code should be compatible with older (but reasonably new) vesions
of MATLAB and R and with other platforms, but we have only tested it in the settings mentioned above. Please email us if you run the code in other platforms, so we can update the requirements.

### Other distributions ###
In the near future, we plan to create MATLAB compiled code which you can run with the MATLAB compiler (i.e. without a full MATLAB installation). We're also developing a Python version of CAGT.

### Recommended software ###
The following code is not required, but you might find it useful for creating the input files for CAGT:
  * [align2rawsignal](http://code.google.com/p/align2rawsignal/): Reads files with mapped reads (eg. BAM) and creates tracks of read counts along the genome. It can apply smoothing, normalization, or other filters.
  * [extractSignal](http://code.google.com/p/extractsignal/): Starting from a genomewide signal and a set of loci of interest, it extracts the signal around the loci.

### Testing the code ###
You can download some test data from [here](http://www.broadinstitute.org/~anshul/projects/encode/rawdata/cagt/jun2012/data/testData/).

`cagtDemo.m`, which is distributed with the rest of the code, demonstrates how:
  * Extract the signal around a set of loci of interest to create the input structures for `cagt`.
  * Call `cagt` to cluster the loci based on their signal.
  * Make a multi-signal text file with the discovered clusters and the signal of another marks aggregated in each cluster.

`plot.cagt.demo.R` demonstrates how to plot the results using the output of `cagtDemo.m`.

See [OutputFormats](OutputFormats.md) for an explanation of the output formats and [Plotting](Plotting.md) for details on how to make and interpret the plots.