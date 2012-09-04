function [centroids, counts] = gcentroids(X, index, clusts, avgFun, recenter, lags)
%GCENTROIDS Centroids and counts stratified by cluster.
%
%   [CENTROIDS, COUNTS] = GCENTROIDS(X, INDEX, CLUSTS, AVGFUN, RECENTER]
%   returns the centroids for the specified clusters using the method
%   specified by AVGFUN. X should be an n-by-p matrix with n examples and p
%   features. INDEX should be a vector of size n with the cluster index for
%   each example. CLUSTS are the indices of the clusters for which the
%   centroids will be computed (we might not want to recompute all the
%   centroids). If RECENTER is true, then the centroids will be recentered
%   (i.e. mean subtracted) and divided by the sum of squared differences
%   from the mean (which is (N - 1) * std. CENTROIDS is an m-by-p matrix
%   where m is the number of elements in CLUSTS. COUNTS is a vector of size
%   m with the number of elements in each cluster.
%
%   Supported option for AVGFUN: 'mean', 'median'. nanmean and nanmedian
%   are used respectively.
% 
%   [CENTROIDS, COUNTS] = GCENTROIDS(X, INDEX, CLUSTS, AVGFUN, RECENTER,
%   LAGS]. X is shifted according to LAGS before the centroids are
%   computed. LAGS should be a vector of size n.
%
%   Author: Sofia Kyriazopoulou (sofiakp@stanford.edu)

% number of features
p = size(X, 2);
numClust = length(clusts);
centroids = NaN(numClust, p);
% number of members for each cluster
counts = zeros(numClust, 1);

for i = 1:numClust
    % Find cluster members
    members = (index == clusts(i));
    if any(members)
        counts(i) = sum(members);
        if nargin > 5 && any(lags) > 0
            X(members, :) = shiftMat(X(members, :), lags(members));
        end
        switch avgFun
            case 'mean'
                centroids(i,:) = nanmean(X(members, :), 1);
            case 'median'
                centroids(i,:) = nanmedian(X(members, :), 1);
        end
    end
end

if recenter
    centroids = centroids - repmat(nanmean(centroids, 2), 1, p);
    % Renormalize centroids
		   s = nanstd(centroids, 0, 2);
    if any(s < eps(class(s))) % small relative to unit-length data points
        error('gcentroids:ZeroCentroid', 'Zero cluster centroid');
    elseif any(isnan(s))
        error('gcentroids:NaNCentroid', 'Cluster centroid containing NaNs');
    end
    centroids = centroids ./ repmat(s, 1, p);
end
end
