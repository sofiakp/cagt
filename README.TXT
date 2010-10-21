##########################################################
# CAGT: Cluster AGgregation Tool
# written by Max Libbrecht
# last updated 10/20/10
##########################################################

CAGT is a tool for visualizing and analyzing large set of signal profiles. It was developed to view the histone profile neighborhoods around transcription factors. It uses a clustering algorithm to split the data into similar sets, then uses an assortment of graphical tools to visualize them. 

See PROCEDURE.TXT for a detailed explanation of exactly what CAGT does.  See EXAMPLE.TXT for a detailed of example of how to run CAGT.

Some terminology:
--------------------------------
CAGT uses two basic types of data:  peak data (i.e. transcription factor binding sites) and signal data (i.e. histone mark ChIP-seq fold change signal).  

To simplify display, each peak and signal track respectively is referred to with a unique "tag".  parameters.py includes a set of peak tags and set of signal tags.  CAGT will perform analysis on every peak_tag-signal_tag pair. 

We call the signal around a peak a "profile".  


Instructions for using CAGT:
--------------------------------
0) Install the necessary libraries (see the Libraries section below)

1) Put all the profile data in cagt/data/profiles_<cell line>/.  The files should be named and formatted as in the "Profiles file format" section.

2) Specify parameters in cagt/parameters.py:
i) CAGT will look in cagt/data/profiles_<cell_line>/ for the data.  Make sure the cell_line parameter in parameters.py agrees with where you want CAGT to look.
ii) Set peak_tags and signal_tags.  Each variable respectively should be a list of tags.  CAGT will cluster every peak_tag-signal_tag pair represented in these lists.  (That means that for every peak_tag-signal_tag pair, there must be a corresponding file in cagt/data/profiles_<cell line>/.)
iii) You can set other parameters in parameters.py, or use the defaults.

3) Run CAGT from the command line with 
> python cagt.py <output_id> <mode>

output_id: output_id should be a number; CAGT will put all its output into cagt/output<output_id>/.  

mode: CAGT has four modes: "--cluster", "--correlate", "--make-plots" and "--make-html".  You can specify one or many modes; if you specify many modes, they run sequentially.

They must be run in the following order: cluster > correlate > make-plots > make-html, but you can run one mode, let it finish, then run another mode; all the relevant data is saved after each mode completes.

- In "cluster" mode, CAGT clusters each set of profiles and puts the results in output<output_id>/clustering_info.pickle.
- In "correlate" mode, CAGT finds correlations between pairs of signal tracks around a single set of peaks, and puts the results in output<output_id>/correlations.pickle
- In "make-plots" mode, CAGT makes aggregation plots for each peak_tag-signal_tag pair, and puts them in their own folder in output<output_id>/
- In "make-html" mode, CAGT makes an html view of the plots, and puts a file called "html_view.html" in output<output_id>/ (and also produces a number of supporting html pages).  Viewing html_view.html in a browser is an easy way to view the results.

Run >python cagt.py without any arguments for a help message describing the modes.

4) The results of the run are placed in cagt/output<output_id>. Open html_view.html in a browser for an easy-to-navigate view of the results.

Libraries:
--------------------------------
CAGT requires these libraries:
scipy - http://www.scipy.org/
Pycluster - http://bonsai.hgc.jp/~mdehoon/software/cluster/software.htm
rpy2 - http://rpy.sourceforge.net/rpy2.html


Profiles file format:
--------------------------------
The profiles files should be named <signal_tag>_around_<peak_tag>.bed3, and they should have the following format:
chr1<tab>start<tab>stop<tab><data>
The start and stop locations aren't currently used by CAGT.  The <data> field should be a comma-delimited list of float values:
chr1<tab>start<tab>stop<tab>val1,val2,...,val251
Currently it is required that the data field be exactly of length 251, and the figure-generation code assumes that each data position represents 10bp (this will be generalized soon).

A sample profiles file can be found at:
http://cagt.googlecode.com/files/H3K4me3_around_P300.bed3

