function [results, params] = clusterSignal(X, params)
%CLUSTERSIGNAL Clusters a signal track
%
%   RESULTS = CLUSTERSIGNAL(X, PARAMS) partitions the rows of X into
%   clusters using k-means (or k-medians) followed by an optional round of
%   hierarchical agglomerative clustering to merge similar clusters. If the
%   signal has been extracted in a region of P bp around each of N loci of
%   interest, then X should be an N-by-P matrix. During agglomerative
%   clustering, signals can be flipped if that leads to a better
%   clustering. This intuitively implies that the directionality of signal
%   can be ignored. PARAMS is a structure with parameters of the
%   clustering.
%
%   PARAMS fields:
%
%      kmeansParams: structure with parameters of the k-means/medians clustering.
%      See simpleKmeans for details.
%
%      hcParams: structure with parameters of the hierarchical
%      agglomerative clustering. See hierarchicalClust for details. If this
%      is omitted from PARAMS, then agglomerative clustering will be
%      skipped.
%
%      distParams: structure specifying the distance metric to use and will
%      be passed to simpleKmeans (and hierarchicalClust).
%
%      nanTreat: how to treat NaN's in X. Possible values:
%         'zero': replace with zeros (default)
%         'interpolate': use linear interpolation to interpolate missing
%         values
%
%      maxNan: rows with more than that number of NaN's will be removed.
%      Set to 0 if you want to keep all rows. Default is ceil(0.5 * P).
%
%      lowSignalCut and lowSignalPrc: Remove rows whose lowSignalPrc-th
%      percentile is less than lowSignalCut. Defaults are 0 for
%      lowSingalCut and 90 for lowSignalPrc.
%
%      lowVarCut: rows with variance less than lowVarCut will be removed.
%      Useful when the distance metric used is correlation-based. Default
%      is 0.
%
%      display: Determines how much information will be output during the
%      clustering. Set to '' to disable all output. See also simpleKmeans
%      and hierarchicalClust.
%
%   RESULTS fields:
%
%      maxNanInd: boolean vector of size N x 1 with indicators of the
%      observations that were excluded from clustering because they
%      contained more than maxNan NaN values.
%
%      lowSignalInd: boolean vector of size N x 1 with indicators of the
%      observationss that were excluded from clustering because they
%      didn't pass the lowSignalCut cutoff.
%
%      lowVarInd: boolean vector of size N x 1 with indicators of the
%      observations that were excluded from clustering because they had
%      variance less than lowVarCut.
%
%      kmeansInputInd: boolean vector of size N x 1 with indicators of the
%      observations that passed all the above filters.
%
%      kmeansResults: structure returned by simpleKmeans.
%
%      hcInputInd (only if agglomeration is performed): boolean vector of
%      size N x 1 with indicators of the observations that were input to
%      agglomerative clustering.
%
%      hcResults (only if agglomeration is performed): structure returned
%      by hierarchicalClust.
%
%   [RESULTS, PARAMS] = CLUSTERSIGNAL(X, PARAMS) also returns the set of
%   all parameters used for clustering (which is the input PARAMS with all
%   default values added).
%
%   Author: Sofia Kyriazopoulou (sofiakp@stanford.edu)

validateReal(X, 'X');
[numInitEx, p] = size(X);

if ~isfield(params, 'kmeansParams')
    error('clusterSignal:MissingArgument', '''params'' must contain a structure ''kmeansParams''.');
end
if ~isfield(params, 'distParams')
    params.distParams = struct([]);
end
distParams = params.distParams;

merge = isfield(params, 'hcParams');

if ~isfield(params, 'nanTreat')
    params.nanTreat = 'zero';
end
nanTreat = params.nanTreat;
validateRange(nanTreat, {'interpolate', 'zero'}, 'nanTreat');

if isfield(params, 'maxNan')
    if ~isint(params.maxNan) || params.maxNan < 0
        error('clusterSignal:InvalidArgument', '''maxNan'' must be a non-negative integer');
    elseif params.maxNan > p
        error('clusterSignal:InvalidArgument', '''maxNan'' cannot be greater than the length of the signal');
    end
else
    params.maxNan = ceil(0.5 * p);
end
maxNan = params.maxNan;

if ~isfield(params, 'lowSignalCut')
    params.lowSignalCut = 0;
end
lowSignalCut = params.lowSignalCut;

if isfield(params, 'lowVarCut')
    if ~isnumeric(params.lowVarCut) || params.lowVarCut < 0 || params.lowVarCut > 1,
        error('clusterSignal:InvalidArgument', '''lowVarCut'' must be between 0 and 1');
    end
else
    params.lowVarCut = 0;
end
lowVarCut = params.lowVarCut;

if isfield(params, 'lowSignalPrc')
    if ~isnumeric(params.lowSignalPrc) || params.lowSignalPrc < 0 || params.lowSignalPrc > 100,
        error('clusterSignal:InvalidArgument', '''lowSignalPrc'' must be between 0 and 100');
    end
else
    params.lowSignalPrc = 90;
end
lowSignalPrc = params.lowSignalPrc;

if ~isfield(params, 'display')
    params.display = '';
end
display = params.display;

if ~isfield(params, 'outlierPrc')
    params.outlierPrc = 75;
end
outlierPrc = params.outlierPrc;

if ~isempty(display)
    fprintf('Number of examples: %d\nSignal length: %d\n', numInitEx, p);
end

%%%%%%%%%%%%%%%%%%%%%%%%% PRE-PROCESSING %%%%%%%%%%%%%%%%%%%%%%%%%

% Find rows with too many nans and remove them.
maxNanInd = sum(isnan(X), 2) > maxNan;

results.maxNanInd = maxNanInd;
kmeansInputInd = ~maxNanInd;
newSignal = X(kmeansInputInd, :);

if ~isempty(display)
    fprintf('Examples with <= %d missing values: %d\n', maxNan, sum(~maxNanInd));
end

if strcmp(nanTreat, 'interpolate')
    if ~isempty(display)
        fprintf('Interpolating missing values...\n');
    end
    % Interpolate missing values
    for i = 1:size(newSignal, 1)
        nanInd = isnan(newSignal(i, :));
        newSignal(i, nanInd) = interp1(find(~nanInd), newSignal(i, ~nanInd), find(nanInd));
    end
end

% Get low signal profiles, after interpolating but before
% replacing NaNs (or normalizing). 
signalPrc = prctile(newSignal, lowSignalPrc, 2);
lowSignalInd = signalPrc < lowSignalCut;
newSignal = newSignal(~lowSignalInd, :);

% Remap the indicators, so that all indicator vectors returned have
% numInitEx elements.
tmpInd = false(numInitEx, 1);
tmpInd(kmeansInputInd) = lowSignalInd;
results.lowSignalInd = tmpInd;
kmeansInputInd = kmeansInputInd & ~tmpInd;

% Get the low variance profiles
lowVarInd = nanstd(newSignal, 0, 2) < sqrt(lowVarCut);
newSignal = newSignal(~lowVarInd, :);
tmpInd = false(numInitEx, 1);
tmpInd(kmeansInputInd) = lowVarInd;
results.lowVarInd = tmpInd;
kmeansInputInd = kmeansInputInd & ~tmpInd;

% Normalize signals that passed cutoff
signalMean = repmat(nanmean(newSignal, 2), 1, p);
signalStd = repmat(nanstd(newSignal, 0, 2), 1, p);
normSignal = (newSignal - signalMean) ./ signalStd;

% There might still be missing values at the beginning or end of the signal. 
% Replace them with 0.
normSignal(isnan(normSignal)) = 0;

results.kmeansInputInd = kmeansInputInd;

if ~isempty(display)
    fprintf('Examples with %d-th prctile value >= %.4f: %d\n', lowSignalPrc, lowSignalCut, sum(~lowSignalInd));
    fprintf('Examples with variance >= %.4f: %d\n', lowVarCut, sum(~lowVarInd));
    fprintf('Examples passing all cutoffs: %d\n', sum(kmeansInputInd));
    fprintf('Starting k-means\n');
    disp(params.kmeansParams);
end

%%%%%%%%%%%%%%%%%%%%%%%%% K-MEANS %%%%%%%%%%%%%%%%%%%%%%%%%

% if strcmp(params.kmeansParams.start, 'plus')
%     normSignal = normSignal - repmat(nanmean(normSignal, 1), size(normSignal, 1), 1);
%     normSignal = normSignal ./ repmat(nanstd(normSignal, 0, 1), size(normSignal, 1), 1);
%     newStart = zeros(params.kmeansParams.k, size(normSignal, 2), params.kmeansParams.replicates);
%     for i = 1:params.kmeansParams.replicates
%         newStart(:, :, i) = kmeansppInit(normSignal, params.kmeansParams.k);
%     end
%     params.kmeansParams.start = newStart;
% end
results.kmeansResults = simpleKmeans(normSignal, params.kmeansParams, distParams);

% if params.adjustIndices
%     % Make sure the arrays and matrices returned have one row per initial
%     % example, for easy mapping between input and output.
%     tmp = results.kmeansResults.idx;
%     results.kmeansResults.idx = zeros(numInitEx, 1);
%     results.kmeansResults.idx(kmeansInputInd) = tmp;
%     tmp = results.kmeansResults.bestLags;
%     results.kmeansResults.bestLags = zeros(numInitEx, 1);
%     results.kmeansResults.bestLags(kmeansInputInd) = tmp; 
% end

%%%%%%%%%%%%%%%%%%%%%%%%% MERGING %%%%%%%%%%%%%%%%%%%%%%%%%

results.hcInputInd = kmeansInputInd;

if merge && (~isfield(params.hcParams, 'k') || params.hcParams.k < size(results.kmeansResults.centroids, 1))
    if ~isempty(display)
        fprintf('Starting merging\n');
        disp(params.hcParams);
    end
    results.hcResults = hierarchicalClust(results.kmeansResults, params.hcParams, distParams);
    finalResults = results.hcResults;
else
    finalResults = results.kmeansResults;
end
end

%%%%%%%%%%%%%%%%%%%%%%%%% HELPER FUNCTIONS %%%%%%%%%%%%%%%%%%%%%%%%%
function b = validateRange(x, range, argName)
if ~ischar(x)
    error('clusterSignal:InvalidArgument', 'Invalid parameter value for ''%s.''', argName);
elseif ~ismember(x, range)
    error('clusterSignal:InvalidArgument', 'Invalid parameter value for ''%s'': %s.', argName, x);
end
b = true;
end

function b = validateReal(x, argName)
if ~(isreal(x) && isnumeric(x))
    error('clusterSignal:InvalidArgument', '''%s'' must be numeric and real.', argName);
end
b = true;
end

function b = isint(x)
b = isscalar(x) && isnumeric(x) && isreal(x) && (round(x) == x);
end

function b = dummyVal(x)
b = true;
end
