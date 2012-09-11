%% Creating input files for CAGT
clearvars

%%%%%%% This code assumes you are in <CAGT root>/matlab/src %%%%%%%

% If you have a .mat file with genomewide signal created by align2rawsignal
% (e.g. nucleosome positioning signal along the genome) and a narrowpeak
% (or bed/mat/summit/gff/gtf) file with regions of interest (e.g. CTCF
% peaks), you can extract the signal in a window +/-500bp around the
% regions to create the input for cagt like this:
extractSignal('../data/ctcf_peaks.narrowPeak', '../data/nucleo_signal.mat', 'if', 'narrowpeak', ...
  'us', 'peak', 'sl', 500, 'sr', 500, 'fw', true, ... % extract signal in a window of +/-500bp
  'o', '../data/nucleo_around_ctcf.mat', ...
  'ov', 'signal', ... % name the output matrix 'signal'
  'mf', 'samplerate', 'mp', 10) % sample every 10 bp
% '../data/h3k9ac_around_ctcf.mat' was created similarly

%% Finding clusters of nucleosome positioning signal around CTCF sites
clearvars
cagt('../data/nucleo_around_ctcf.mat', 'od', '../data/test', 'op', 'nucleo_around_ctcf_', 'tt', 'CTCF', 'st', 'NUCLEOSOME', ...
  'merge', true, 'bed', true, 'txt', true, 'maxiter', 100, 'replicates', 2, 'start', 'plus', ...
  'overwrite', true, 'flip', true, 'mergeDist', 0.8, 'mergeK', 1, 'distance', 'correlation')
% Now you can use the R code to make nice customizable plots

%% Creating "multivariate" tables
% The following code will create a cluster table with the nucleosome signal
% in the clusters created by the code snippet above AND the average H3K9AC
% signal in the same clusters.
% Again, you can use the R code to plot both the clusters and the
% associated signal.

clearvars
% Load the cagt results and the signal that was used for clustering
results = load('../data/test/nucleo_around_ctcf_results.mat');
load('../data/nucleo_around_ctcf.mat', 'signal');

% Plotting parameters
params = struct();
params.signalRange = 1:101;
params.merged = true;
params.signalType = 'NUCLEOSOME';
params.targetType = 'CTCF';

% Load the "partner" signal(s).
other = load('../data/h3k9ac_around_ctcf.mat', 'signal');
otherSignals = other.signal;
makeSignalTable('../data/test/nucleo_around_ctcf_multi_clusterData.txt', results, signal, params, ....
  otherSignals, {'BroadInstituteH3K9AC'}, {'H3K9AC'});
  