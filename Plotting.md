## Plotting ##

`plot.cagt.multivariate.figs.R` takes as input a [clusterData](OutputFormats#clusterData.md) file and produces highly customizable plots of the clusters. These are the input parameters:
  * cagt.table.filename : name of CAGT table file (can be gzipped).
  * output.dir: name of output directory. If left NULL, the directory of the input file will be used.
  * output.file: prefix output file (without extension). If set to NULL, the file will be <prefix of input file>.<partner.marks>.<mag.shape>. Default: NULL.
  * output.format: format of figures, png or pdf (default).
  * support.thresh: remove shapes whose support is < support.thresh\*fraction of peaks in high signal component. Default: 0 (everything is plotted).
  * orient.shapes: If set to T then for the shape clusters, if required invert shapes to make them Low (left) to High (right). Default: T.
  * replace.flag: If set to F then if output files exist the function returns without plotting anything. Default: T
  * partner.marks: The partner mark(s) that you want to plot alongside the target mark. You can specify multiple eg. c("GC","DNase"). Regular expressions are also allowed for matching. Set to "all" (default) to print all marks. Set this to "SIGNAL" if you don't want to print any partner marks.
  * zscore: whether to plot standardized plots or original scale. Default: F.
  * common.scale: Set to T if you want to put all magnitude plots on a common scale. Default: F.
  * plot.over: If T, all signals will be in one set of plots (using facet\_wrap). Otherwise, each partner mark will go to a different row (with facet\_grid). Default: F
  * whiskers: Whether to plot percentile whiskers or just the mean signal. Default: F
  * mag.shape: "shape" plots just the clusters. "mag" plots the aggregation plot over all clusters and the "high" and "low" signal components. "all" plots clusters and signal components. Default: "all"

## Examples ##
The following two figures correspond to the same set of clusters. With default parameters, the function will plot both the discovered clusters (first row) and all partner marks (in this example, just one) averaged in the same clusters.
![http://cagt.googlecode.com/svn/wiki/nucleo_around_ctcf_multi_clusterData.all.all.png](http://cagt.googlecode.com/svn/wiki/nucleo_around_ctcf_multi_clusterData.all.all.png)

In the plot below, we disable plotting of partner marks by setting partner.marks = "SIGNAL". We also change the following parameters:
```
common.scale = T
plot.over = T
whiskers = T
```

![http://cagt.googlecode.com/svn/wiki/nucleo_around_ctcf_multi_clusterData.SIGNAL.all.png](http://cagt.googlecode.com/svn/wiki/nucleo_around_ctcf_multi_clusterData.SIGNAL.all.png)

The panels named `P_#` show the mean signal (bold line) and signal percentiles (shaded area) in the discovered clusters. The panel labeled "all" is an aggregation over all elements. The panel "high" shows the elements that passed all filtering criteria and participated in clustering. In this case, all elements passed the filtering. Otherwise, there would also be an extra panel "low".