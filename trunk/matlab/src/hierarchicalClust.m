function results = hierarchicalClust(clustResults, params, distParams)
%HIERARCHICALCLUST Hierarchical clustering of clusters with flipping.
%
%   RESULTS = HIERARCHICALCLUST(CLUSTRESULTS, PARAMS, DISTPARAMS) Performs
%   hierarchical clustering of a pre-computed set of clusters given in the
%   struct CLUSTRESULTS. PARAMS is a struct with parameters for the hierarchical
%   clustering. DISTPARAMS is a struct with parameters of the distance
%   function used for clustering.
%
%   CLUSTRESULTS fields:
%   
%      data: N-by-P matrix with N observations and P variables/features
%
%      idx: vector of length N with assignment of the N observations to
%      clusters. All observations with the same value of idx are assumed to
%      be pre-assigned to the same cluster.
%
%      centroids: m x P matrix of the cluster centroids, where m is the
%      number of clusters in idx.
%
%   PARAMS fields:
%
%      k: final number of clusters. Default is 1 so merging will continue
%      until there's only 1 cluster. k cannot be greater than m, the number
%      of input clusters.
%
%      maxDist: maximum distance for merging. Merging will stop if the
%      distance between the two closest centroids is greater than maxDist,
%      or if the number of clusters reaches k.
%
%      flip: Logical. Whether flipping will be allowed (default) or not. If
%      flipping is allowed both an observation and its reversed (i.e.
%      taking the P features from end to start) will be considered when
%      looking for the closest cluster.
%
%      distance: Distance function used for merging clusters:
%          'sqeuclidean'  - Squared Euclidean distance (the default)
%          'correlation'  - One minus the sample correlation between points
%                           (treated as sequences of values)
%          'xcorr'        - One minus the maximum sample cross-correlation
%                           over all possible lags (see the option
%                           'maxlag')
%
%      display: Determines how much output will be printed. Choices are:
%           0 - No output.
%           1 - Output only after the last iteration (default).
%           2 - Output at each iteration.
%
%      lags: Initial optimal lags.
%
%   DISTPARAMS fields:
%
%      distance: Distance function, in P-dimensional space, that KMEANS
%      should minimize with respect to.  Choices are:
%          'sqeuclidean'  - Squared Euclidean distance (the default)
%          'correlation'  - One minus the sample correlation between points
%                           (treated as sequences of values)
%          'xcorr'        - One minus the maximum sample cross-correlation
%                           over all possible lags (see the option
%                           'maxlag')
%
%      avgFun: Method for computing cluster centroids. Choices are 'mean',
%     'median'. Default is mean.
%
%      maxlag: Maximum lag when xcorr is used as the distance measure.
%      Otherwise maxlag will be set to 0 and the value passed will be
%      ignored.
%
%   RESULTS fields:
%   
%      idx: vector of length N with the assignments of the N observations
%      into the agglomerated clusters 
% 
%      centroids: k x P matrix of the cluster centroids, where k is the
%      number of agglomerated clusters.
%
%      dataToCentroidDist: N x k matrix with the distance between each
%      observation and each centroid.
%
%      centroidDist: k x k matrix with the distances between all centroids.
%
%      lags: N x k matix with the lag that achieves the best distance
%      between each observation and each cluster centroid. Will be 0 for
%      distance functions other than xcorr.
%
%      bestLags: N x 1 vector with the lag that achieved the best distance
%      to the closest centroid for each observation. Will be 0 for distance
%      functions other than xcorr.
%
%      bestDist: N x 1 vector with the distance of each observation from
%      the closest centroid
%
%      flipInd: binary vector of length N. If flipInd is true then the N-th
%      observation was flipped (from end to start) to achieve the minimum
%      distance to the assigned cluster centroid.
%
%      data: the data used for the clustering (after whatever normalization
%      took place). Values for flipped observations will be flipped
%      accordingly.
%
%      Z: (k-1) x 4 matrix with the agglomeration steps. At step i of the
%      agglomeration, we merge clusters Z(i, 1) and Z(i, 2) to make a new
%      cluster that will replace the Z(i, 1)-th cluster. Z(i, 3) gives the
%      distance between the merged clusters. Z(i, 4) is 1 if the Z(i, 2)-th
%      cluster was flipped during the merge, and 0 otherwise.
%
%   NOTE about the order of flipping/merging and finding optimal lags: All
%   the merging and flipping is done on the shifted signal with the optimal
%   lags given in the 'lags' parameter. That is, the optimal lags remain
%   unchanged during the merging/flipping, and the centroids of the merged
%   clusters are computed based on the pre-shifted signal. Once the merging
%   and flipping is over, the new distances and optimal lags are
%   recomputed.
%
%   Author: Sofia Kyriazopoulou (sofiakp@stanford.edu)

if ~all(isfield(clustResults, {'data', 'idx', 'centroids'}))
    error('hierarchicalClust:InvalidArgument', ...
        '''clustResults'' must contain the fields ''data'', ''idx'', and ''centroids''');
end
X = clustResults.data;
validateReal(X, 'X');
[n, p] = size(X);
idx = clustResults.idx;
centroids = clustResults.centroids;

if isfield(params, 'k')
    numClust = params.k; 
else
    numClust = 1;
end
if isfield(params, 'maxDist')
    maxDist = params.maxDist;
else
    maxDist = Inf;
end
if isfield(params, 'lags')
    lags = params.lags;
else
    lags = [];
end
if isfield(params, 'flip')
    if ~islogical(params.flip)
        error('hierarchicalClust:InvalidArgument', '''flip'' must be logical')
    end
    allowFlip = params.flip;
else
    allowFlip = true;
end
if isfield(params, 'display')
    display = params.display;
else
    display = 1;
end

if isfield(distParams, 'distance')
    distance = distParams.distance;
else
    distance = 'sqeuclidean';
    distParams.distance = distance;
end
if isfield(distParams, 'avgFun')
    avgFun = distParams.avgFun;
else
    avgFun = 'mean';
    distParams.avgFun = avgFun;
end

validateRange(distance, {'sqeuclidean', 'correlation', 'xcorr'}, 'distance');
validateRange(avgFun, {'mean', 'median'}, 'avgFun');
validateattributes(display,  {'numeric'}, {'integer', 'scalar', 'nonnegative', '<=', 2}, 'hierarchicalClust', 'display');
validateReal(lags, 'lags');
validateReal(centroids, 'centroids');
validateReal(idx, 'idx');

% initial number of clusters
K = size(centroids, 1);

if ~isint(numClust) || numClust <= 0,
    error('hierarchicalClust:InvalidArgument', ...
          '''numClust'' must be a positive integer value.');
elseif n < numClust
    error('hierarchicalClust:TooManyClusters', ...
          '''X'' must have more rows than the number of clusters.');
elseif numClust > K,
    error('hierarchicalClust:InvalidArgument', ...
          '''numClust'' cannot be larger than the number of input clusters.');
end

% Initialize new assignment of examples to clusters with the existing
% assignment.
newIdx = idx;
newCentroids = centroids;
% indicators of whether each example was flipped or not
flipInd = false(size(idx));
% These clusters have been merged already, so we shouldn't consider them
% any more.
badIdx = false(K, 1);

Z = zeros(K - 1, 4);
dir = [1:p; p:-1:1];

% For correlation, make sure you renormalize the input points and centroids.
if ismember(distance, {'correlation', 'xcorr'})
    X = X - repmat(mean(X, 2), 1, p);
    Xnorm = std(X, 0, 2);
    if any(Xnorm <= eps(class(Xnorm)))
        error('hierarchicalClust:ConstantDataForCorr', ...
            ['Some points have small relative standard deviations, making them ', ...
            'effectively constant.\nEither remove those points, or choose a ', ...
            'distance other than ''correlation''.']);
    end
    X = X ./ repmat(Xnorm, 1, p);
    
    newCentroids = newCentroids - repmat(mean(newCentroids, 2), 1, p);
    Cnorm = std(newCentroids, 0, 2);
    if any(Cnorm < eps(class(Cnorm))) % small relative to unit-length data points
        error('hierarchicalClust:ZeroCentroid', ...
            'Some of the initial centroids have small relative standard deviation, making them effectively constant.');
    end
    newCentroids = newCentroids ./ repmat(Cnorm, 1, p);
end
% whether the centroids should be renormalized after each merging step
recenterCentroids = ismember(distance, {'correlation', 'xcorr'});

% Shift the input
if ~isempty(lags)
    if length(lags) ~= n
        error('hierarchicalClust:InvalidArgument', ...
            '''lags'' must be empty or have the same number of elements as examples in ''X''.');
    end
    shiftedX = shiftMat(X, lags);
else
    shiftedX = X;
end

% Disallow lag while merging centroids.
originalDistParams = distParams;
distParams.maxlag = 0;

dist = zeros(K, K, allowFlip + 1);
% No lag allowed between centroids.
dist(:, :, 1) = triu(distfun(distParams, newCentroids), 1);
if allowFlip
    dist(:, :, 2) = triu(distfun(distParams, newCentroids, newCentroids(:, dir(2, :))), 1);
end

% At most K - numClust merging steps
for k = 1:K-numClust,
    % Get minimum distance and corresponding cluster indices.
    minDist = min(dist(dist > 0));
    if minDist > maxDist
        break;
    end
    flatInd = find(dist == minDist);
    if length(flatInd) > 1
        flatInd = flatInd(randsample(length(flatInd), 1));
    end
    % We will be merging clusters i and j. If d == 2, then cluster j should
    % be flipped. The new cluster will replace cluster i.
    [i, j, d] = ind2sub(size(dist), flatInd);
    
    newCluster = [shiftedX(newIdx == i, dir(1, :)); shiftedX(newIdx == j, dir(d, :))];
    tempIdx = ones(size(newCluster, 1), 1);
    newCentroids(i, :) = gcentroids(newCluster, tempIdx, 1, avgFun, recenterCentroids, 0);
    
    % Invalidate cluster j
    badIdx(j) = true;
    dist(j, j + 1:end, :) = 0;
    dist(1:j - 1, j, :) = 0;
    
    % Compute the distance between the new centroid and all other valid
    % centroids.
    newDist = zeros(K, 1);
    newDist(~badIdx) = distfun(distParams, newCentroids(i, :), newCentroids(~badIdx, :));      
    dist(i, i + 1:end, 1) = newDist(i + 1:end);
    dist(1:i - 1, i, 1) = newDist(1:i - 1);
    
    if allowFlip
        % Compute the distance between the new centroid and the flipped
        % version of all other centroids.
        newDist = zeros(K, 1);
        newDist(~badIdx) = distfun(distParams, newCentroids(i, :), newCentroids(~badIdx, dir(2, :)));
        dist(i, i + 1:end, 2) = newDist(i + 1:end);
        dist(1:i - 1, i, 2) = newDist(1:i - 1);
    end
    
    if d == 2
        flipInd(newIdx == j) = ~flipInd(newIdx == j);
        shiftedX(newIdx == j, :) = shiftedX(newIdx == j, dir(2, :));
    end
    newIdx(newIdx == j) = i;
    Z(k, :) = [i, j, minDist, d - 1];
end

Z = Z(1:k - 1, :);
results.Z = Z;

% Remove clusters that were merged into other clusters and change indices
% to be 1:num_clusters
idxMap = zeros(size(badIdx));
idxMap(~badIdx) = 1:sum(~badIdx);
results.idx = idxMap(newIdx);
results.centroids = newCentroids(~badIdx, :);
% Now reorder based on occupancy
[results.idx, sortIdx] = sortClusters(results.idx);
results.centroids = results.centroids(sortIdx, :);

% Merging and flipping was done without changing the input lags. To
% recompute the distances to the new centroids, we keep the flipping fixed
% and allow changes to the lags.
results.data = X;
results.data(flipInd, :) = X(flipInd, end:-1:1);

results.centroidDist = distfun(distParams, results.centroids);
results.flipInd = flipInd;

% Recompute distances to new clusters
[results.dataToCentroidDist, newLags] = distfun(originalDistParams, results.data, results.centroids);
results.lags = newLags;
results.bestLags = results.lags((results.idx-1)*n + (1:n)');
results.bestDist = results.dataToCentroidDist((results.idx-1)*n + (1:n)');

end

function b = validateRange(x, range, argName)
if ~ischar(x)
    error('hierarchicalClust:InvalidArgument', 'Invalid parameter value for ''%s.''', argName);
elseif ~ismember(x, range)
    error('hierarchicalClust:InvalidArgument', 'Invalid parameter value for ''%s'': %s.', argName, x);
end
b = true;
end

function b = validateReal(x, argName)
if ~(isreal(x) && isnumeric(x))
    error('hierarchicalClust:InvalidArgument', '''%s'' must be numeric and real.', argName);
end
b = true;
end

function b = isint(x)
b = isscalar(x) && isnumeric(x) && isreal(x) && (round(x) == x);
end

function b = dummyVal(x)
b = true;
end