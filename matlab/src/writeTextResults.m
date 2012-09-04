function writeTextResults(outfile, results, intervalData, names, adj)
%WRITETEXTRESULTS Creates BED-like output of clustering results.
%
%   WRITETEXTRESULTS(OUTFILE, RESULTS, INTERVALDATA, NAMES) creates a BED
%   file OUTFILE with clustering results for the regions in INTERVALDATA.
%   OUTFILE is the path of the output file. RESULTS is a structure returned
%   from CLUSTERSIGNAL. INTERVALDATA is a stucture with fields 'chr',
%   'start', 'stop', and 'strand'. NAMES is a cell array with names for the
%   regions. If missing, then the names in the output BED will be '.'
%
%   The output file contains all the fields in the BED-6 format (chrom,
%   start, end, name, score, strand, where score is always '.') followed by
%   the following fields:
%      - flipping indicator: 1 if the region was flipped during agglomerative
%      clustering, 0 otherwise
%      - k-means/medians cluster index
%      - index of agglomerated cluster
%
%   Author: Sofia Kyriazopoulou (sofiakp@stanford.edu)

finalInd = results.hcInputInd;
oversegIdx = zeros(size(finalInd));
oversegIdx(finalInd) = results.kmeansResults.idx;
clusterIdx = zeros(size(finalInd));
clusterIdx(finalInd) = results.hcResults.idx;
flippedInd = false(size(finalInd));
flippedInd(finalInd) = results.hcResults.flipInd;

if ~isempty(intervalData) && size(intervalData, 1) ~= length(finalInd)
    error('MyErr:IncompatibleArguments', 'Sizes on intervalData and results are incompatible');
end
if ~isempty(names) && length(names) ~= length(finalInd)
    error('MyErr:IncompatibleArguments', 'Sizes of names and results are incompatible');
end
if nargin < 5
    adj = 0;
end
f = fopen(outfile, 'w');
for i = 1:length(finalInd)
    if exist('names', 'var')
        name = char(names{i});
    else
        name = '.';
    end
    if ~isempty(intervalData)
        s = sprintf('%s\t%d\t%d\t%s\t.\t%s\t', char(intervalData.chr(i)), intervalData.start(i) - 1 + adj, intervalData.stop(i) - adj, name, char(intervalData.strand(i)));
    else
        s = ['.\t.\t.\t', name, '.\t.\t'];
    end
    
    fprintf(f, '%s\t%d\t%d\t%d\n', s, flippedInd(i), oversegIdx(i), clusterIdx(i));
end
fclose(f);
end