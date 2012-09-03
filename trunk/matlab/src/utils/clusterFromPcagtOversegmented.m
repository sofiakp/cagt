function [results, params] = clusterFromPcagtOversegmented(signal, params, cagtDir)

[numInitEx, signalLen] = size(signal);

if ~isfield(params, 'distParams')
    params.distParams = struct([]);
end
if isfield(params.distParams, 'distance')
    distance = params.distParams.distance;
else
    distance = 'sqeuclidean';
    params.distParams.distance = distance;
end
if isfield(params.distParams, 'avgFun')
    avgFun = params.distParams.avgFun;
else
    avgFun = 'mean';
    params.distParams.avgFun = avgFun;
end
if isfield(params.distParams, 'maxlag') && params.distParams.maxlag > 0
    error('MyErr:clusterFromPcagtOversegmented', 'maxlag unsupported')
end
merge = isfield(params, 'hcParams');

if ~isfield(params, 'nanTreat')
    params.nanTreat = 'zero';
end
nanTreat = params.nanTreat;
validateRange(nanTreat, {'interpolate', 'zero'}, 'nanTreat');

if isfield(params, 'maxNan')
    if ~isint(params.maxNan) || params.maxNan < 0
        error('clusterSignal:InvalidArgument', '''maxNan'' must be a non-negative integer');
    elseif params.maxNan > signalLen
        error('clusterSignal:InvalidArgument', '''maxNan'' cannot be greater than the length of the signal');
    end
else
    params.maxNan = ceil(0.5 * signalLen);
end
maxNan = params.maxNan;

if isfield(params, 'lowVarCut')
    if ~isnumeric(params.lowVarCut) || params.lowVarCut < 0 || params.lowVarCut > 1,
        error('clusterSignal:InvalidArgument', '''lowVarCut'' must be between 0 and 1');
    end
else
    params.lowVarCut = 0;
end
lowVarCut = params.lowVarCut;

if ~isfield(params, 'display')
    params.display = '';
end
display = params.display;

if ~isfield(params, 'outlierPrc')
    params.outlierPrc = 75;
end
outlierPrc = params.outlierPrc;

validateRange(distance, {'sqeuclidean', 'correlation'}, 'distance');
validateRange(avgFun, {'mean', 'median'}, 'avgFun');

recenterCentroids = ismember(distance, {'correlation'});

% The order of the filters (low signal/max nan etc) is a bit different from
% the original mCAGT code
results = struct();
results.lowSignalInd = false(numInitEx, 1);
filename = fullfile(cagtDir, 'members_low_signal.txt');
if exist(filename, 'file') && ~isdir(filename)
    results.lowSignalInd(importdata(filename) + 1) = true;
end

results.maxNanInd = sum(isnan(signal), 2) > maxNan;
kmeansInputInd = ~results.lowSignalInd & ~results.maxNanInd;

newSignal = signal(kmeansInputInd, :);

if ~isempty(display)
    fprintf('Number of examples: %d\nSignal length: %d\n', numInitEx, signalLen);
    fprintf('Examples with <= %d missing values: %d\n', maxNan, sum(~results.maxNanInd));
    fprintf('High signal examples: %d\n', sum(~results.lowSignalInd));
end

if strcmp(params.nanTreat, 'interpolate')
    if ~isempty(params.display)
        fprintf('Interpolating missing values...\n');
    end
    % Interpolate missing values
    for i = 1:size(newSignal, 1)
        nanInd = isnan(newSignal(i, :));
        newSignal(i, nanInd) = interp1(find(~nanInd), newSignal(i, ~nanInd), find(nanInd));
    end
end

% Get the low variance profiles
lowVarInd = nanstd(newSignal, 0, 2) < sqrt(lowVarCut);
newSignal = newSignal(~lowVarInd, :);
tmpInd = false(numInitEx, 1);
tmpInd(kmeansInputInd) = lowVarInd;
results.lowVarInd = tmpInd;
kmeansInputInd = kmeansInputInd & ~tmpInd;

% Normalize signals that passed cutoff
signalMean = repmat(nanmean(newSignal, 2), 1, signalLen);
signalStd = repmat(nanstd(newSignal, 0, 2), 1, signalLen);
normSignal = (newSignal - signalMean) ./ signalStd;

% There might still be missing values at the beginning or end of the signal. 
% Replace them with 0.
normSignal(isnan(normSignal)) = 0;

results.kmeansInputInd = kmeansInputInd;

if ~isempty(display)
    fprintf('Examples with variance >= %.4f: %d\n', lowVarCut, sum(~lowVarInd));
    fprintf('Examples passing all cutoffs: %d\n', sum(kmeansInputInd));
    % Check if pCAGT missed too many problematic examples
    if sum(results.lowVarInd & ~results.lowSignalInd) / sum(~results.lowSignalInd) > 0.01
        warning('MyWarn:LowVarianceInput', 'Too many examples with low variance missed by pCAGT');
    end
    if sum(results.maxNanInd & ~results.lowSignalInd) / sum(~results.lowSignalInd) > 0.01
        warning('MyWarn:LowVarianceInput', 'Too many examples with many NaNs missed by pCAGT');
    end
end

% Find of each cluster, removing non-empty clusters
cagtCont = dir(cagtDir);
selFiles = ~cellfun(@isempty, regexp({cagtCont.name}, 'members_shape_cluster_oversegmented_[0-9]*.txt', 'once'));
numClusters = nnz(selFiles);
numKmeansEx = nnz(results.kmeansInputInd);
% pCAGT files have indices in the original space of examples, while mCAGT
% assumes low signal are already removed
indMap = zeros(size(results.kmeansInputInd));
indMap(results.kmeansInputInd) = 1:numKmeansEx;
results.kmeansResults.data = normSignal;
results.kmeansResults.idx = zeros(numKmeansEx, 1);
% The actual number of clusters might change if some of them turn out to be
% empty.
results.kmeansResults.centroids = zeros(numClusters, signalLen);
numNonEmptyClust = 0;
for i = 1:numClusters
    mem = false(numInitEx, 1);
    mem(importdata(fullfile(cagtDir, ['members_shape_cluster_oversegmented_', num2str(i - 1), '.txt'])) + 1) = true;
    mem = indMap(mem & results.kmeansInputInd);
    if isempty(mem)
        warning('MyWarn:EmptyCluster', ['Empty cluster ', fullfile(cagtDir, ['members_shape_cluster_oversegmented_', num2str(i - 1), '.txt'])]);
    else
        numNonEmptyClust = numNonEmptyClust + 1;
        results.kmeansResults.idx(mem) = numNonEmptyClust;
        results.kmeansResults.centroids(numNonEmptyClust, :) = gcentroids(normSignal, results.kmeansResults.idx, numNonEmptyClust, avgFun, recenterCentroids, 0);
    end
    
end

results.kmeansResults.centroids = results.kmeansResults.centroids(1:numNonEmptyClust, :);

% Return the best solution after rearranging the clusters based on
% occupancy.
[newIdx, sortIdx] = sortClusters(results.kmeansResults.idx);
results.kmeansResults.idx = newIdx;
results.kmeansResults.centroids = results.kmeansResults.centroids(sortIdx, :);
results.kmeansResults.lags = zeros(numKmeansEx, numClusters);
results.kmeansResults.bestLags = zeros(numKmeansEx, 1);
results.kmeansResults.dataToCentroidDist = distfun(params.distParams, results.kmeansResults.data, results.kmeansResults.centroids);
results.kmeansResults.bestDist = results.kmeansResults.dataToCentroidDist((results.kmeansResults.idx-1)*numKmeansEx + (1:numKmeansEx)');
results.kmeansResults.centroidDist = distfun(params.distParams, results.kmeansResults.centroids);

%%%%%%%%%%%%%%%%%%%%%%%%% MERGING %%%%%%%%%%%%%%%%%%%%%%%%%

results.hcInputInd = results.kmeansInputInd;

if merge && (~isfield(params.hcParams, 'k') || params.hcParams.k < size(results.kmeansResults.centroids, 1))
    if ~isempty(display)
        fprintf('Starting merging...\n');
    end
    results.hcResults = hierarchicalClust(results.kmeansResults, params.hcParams, params.distParams);
    finalResults = results.hcResults;
else
    finalResults = results.kmeansResults;
end

%%%%%%%%%%%%%%%%%%%%%%%%% OUTLIER DETECTION %%%%%%%%%%%%%%%%%%%%%%%%%

% outliers are detected but not removed from results
% outlier detection based on median absolute deviation
outlierInd = false(size(finalResults.data, 1), 1);
for i = 1:size(finalResults.centroids, 1)
    members = finalResults.idx == i;
    if ~isempty(members)
        dev = abs(finalResults.data(members, :) - repmat(finalResults.centroids(i, :), sum(members), 1));
        dev = dev ./ (1.4826 * repmat(nanmedian(dev), sum(members), 1));
        outlierInd(members) = prctile(dev, outlierPrc, 2) > 3;
    end
end

results.outlierInd = false(numInitEx, 1);
results.outlierInd(results.hcInputInd) = outlierInd;
end

function b = validateRange(x, range, argName)
if ~ischar(x)
    error('clusterFromPcagtOversegmented:InvalidArgument', 'Invalid parameter value for ''%s.''', argName);
elseif ~ismember(x, range)
    error('clusterFromPcagtOversegmented:InvalidArgument', 'Invalid parameter value for ''%s'': %s.', argName, x);
end
b = true;
end

function b = isint(x)
b = isscalar(x) && isnumeric(x) && isreal(x) && (round(x) == x);
end