function [newIdx, sortIdx, sortNumMembers] = sortClusters(inIdx, numMembers)
% [newIdx, sortIdx, sortNumMembers] = sortClusters(inIdx) Sorts clusters
% based on their occupancy.
%
% inIdx is a vector of length N with cluster indices for N objects. The
% cluster indices are assumed to be consecutive positive integers, so if
% there are M clusters, inIdx must be in the range [1,M]. newIdx will be a
% vector of the same size as inIdx with the indices changed, so that
% cluster 1 is the most prevalent cluster, followed by cluster 2 and so on. 
%
% sortIdx is a vector of length M such that cluster i in the new set of
% clusters corresponds to sortIdx(i) in the old set of clusters.
%
% sortNumMembers is a vector of length M so that sortNumMembers(i) is the
% number of members of the i-th cluster in the new set of clusters (i.e.
% the cluster that corresponds to newIdx == i).
%
% [newIdx, sortIdx, sortNumMembers] = sortClusters(inIdx, numMembers) Sorts
% clusters in descending order of numMembers. If there are M clusters, i.e.
% inIdx ranges in [1,M], then numMembers must be a vector of length M.
%
% Author: sofiakp

if any(inIdx <= 0 | round(inIdx) ~= inIdx)
    error('MyErr:InvalidInput', 'indices must be positive integers');
end

numClusters = max(inIdx);
if nargin < 2
    numMembers = zeros(numClusters, 1);
    for i = 1:numClusters
        numMembers(i) = nnz(inIdx == i);
    end
end

if length(numMembers) ~= numClusters
    error('MyErr:IncompatibleArguments', '''numMembers'' must have one element for each cluster');
end

[sortNumMembers, sortIdx] = sort(numMembers, 'descend');
newIdx = zeros(size(inIdx));
for i = 1:numClusters
   newIdx(inIdx == sortIdx(i)) = i;
end
end