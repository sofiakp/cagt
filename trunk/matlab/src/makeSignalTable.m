function makeSignalTable(fname, results, signal, params, ...
  otherSignals, otherSignalNames, otherSignalTypes)
%MAKESIGNALTABLE(FNAME, RESULTS, SIGNAL, PARAMS) Writes clustering results in text format.
%
%   MAKESIGNALTABLE(FNAME, RESULTS, SIGNAL, PARAMS) writes a text file with
%   the clusters in the RESULTS structure. FNAME should be the path to the
%   output text file. If field 'merge' of PARAMS is true (see below), then
%   RESULTS should contain a field hcResults with the results of
%   hierarchicalClust and a field hcInputInd with the indices of signals
%   that were used for clustering. If 'merge' is false, then RESULTS should
%   contain a field kmeansResults with the results of simpleKmeans and a
%   field kmeansInputInd. All these fields are created by clusterSignal.
%   SIGNAL is the signal that was used for clustering (i.e. signal input to
%   clusterSignal). PARAMS is a structure with optional additional
%   parameters that determine the format of the output file. If you want to
%   leave these parameters to defaults, just give an empty structure.
%
%   PARAMS fields:
%
%   signalRange: Range of columns of SIGNAL that should be output (default:
%   all columns).
%
%   xrange: Range of values to be output in the Pos field. Default
%   1:length(signalRange).
%
%   prcVals: Percentiles of signal that will be computed at each position.
%   Should be a vector of length 2. Default [10 90].
%   
%   targetType and signalType: Values of the TF and Mark columns of the
%   ouput file. Defaults are 'TARGET' and 'SIGNAL' respectively.
%
%   merged: Boolean determining whether to output the results of the
%   k-means/medians clustering (if false) or the results of the
%   hierarchical clustering (if true). Default is false.
%
%   Author: Sofia Kyriazopoulou (sofiakp@stanford.edu)

if ~isfield(params, 'signalRange')
  signalRange = 1:size(signal, 2);
else
  signalRange = params.signalRange;
end
if ~isfield(params, 'xrange')
    xrange = signalRange;
else
    xrange = params.xrange;
end
if length(signalRange) ~= length(xrange)
    error('MyErr:InconsitentInputs', 'All range vectors must have the same length');
end
if ~isfield(params, 'signalType')
    signalType = 'SIGNAL';
else
    signalType = params.signalType;
end
if ~isfield(params, 'targetType')
    targetType = 'TARGET';
else
    targetType = params.targetType;
end
if ~isfield(params, 'prcVals')
    prcVals = [10 90];
else
    prcVals = params.prcVals;
    if length(prcVals) ~= 2 || any(prcVals) > 100 || any(prcVals) < 0
      error('MyErr:InvalidInput', 'params.prcVals must be a vector of length 2 with values between 0 and 100');
    end
end

if isfield(params, 'merged')
    merged = params.merged;
else
    merged = false;
end

numPeaks = size(signal, 1);

if nargin < 5
  otherSignals = zeros(numPeaks, size(signal, 2), 0);
  otherSignalTypes = {};
  otherSignalNames = {};
end
if size(otherSignals, 1) ~= numPeaks || size(signal, 2) ~= size(otherSignals, 2)
  error('MyErr:InconsitentInputs', 'Inconsistent dimensions for otherSignals and signal');
end
if length(otherSignalNames) ~= size(otherSignals, 3) || length(otherSignalTypes) ~= size(otherSignals, 3)
  error('MyErr:InconsitentInputs', 'The third dimension of otherSignals must be equal to the number of signal names and signal types');
end
allSignals = zeros(numPeaks, length(signalRange), length(otherSignalTypes) + 1, 'single');
allSignals(:, :, 1) = signal(:, signalRange);
allSignals(:, :, 2:size(allSignals, 3)) = otherSignals(:, signalRange, :);
allSignalNames = ['Mark', otherSignalNames];
allSignalTypes = ['SIGNAL', otherSignalTypes];

outfile = fopen(fname, 'w');

normAllSignals = allSignals;
for i = 1:size(allSignals, 3)
    signalMean = nanmean(allSignals(:, :, i), 2);
    signalStd = nanstd(allSignals(:, :, i), 0, 2);
    normAllSignals(:, :, i) = (allSignals(:, :, i) - repmat(signalMean, [1, length(signalRange), 1])) ./ repmat(signalStd, [1, length(signalRange), 1]);
end

if merged
    idx = results.hcResults.idx;
    input = results.hcInputInd;
    flipInd = results.hcResults.flipInd;
else
    idx = results.kmeansResults.idx;
    input = results.kmeansInputInd;
    flipInd = false(size(input));
end

writeHeader(outfile, allSignalNames, allSignalTypes);

writeSignal(outfile, targetType, signalType, 'all', numPeaks, xrange, ...
    prcVals, allSignals, normAllSignals);

if any(~input)
  writeSignal(outfile, targetType, signalType, 'low', ...
      nnz(~input) * 100 / numPeaks, xrange, prcVals, ...
      allSignals(~input, :, :), normAllSignals(~input, :, :));
end
if any(input)
  writeSignal(outfile, targetType, signalType, 'high', ...
    nnz(input) * 100 / numPeaks, xrange, prcVals, ...
    allSignals(input, :, :), normAllSignals(input, :, :));
end
numClust = max(idx);
allSignals = allSignals(input, :, :);
allSignals(flipInd, :, :) = allSignals(flipInd, length(signalRange):-1:1, :);
normAllSignals = normAllSignals(input, :, :);
normAllSignals(flipInd, :, :) = normAllSignals(flipInd, length(signalRange):-1:1, :);

for i = 1:numClust,
    writeSignal(outfile, targetType, signalType, ['shape', num2str(i)], ...
        nnz(idx == i) * 100 / numPeaks, xrange, prcVals, ...
        allSignals(idx == i, :, :), normAllSignals(idx == i, :, :));
end

fclose(outfile);
end

function writeHeader(outfile, signalNames, signalTypes)
headers = sprintf('\t%s', signalNames{:});
fprintf(outfile, '#TF\tMark\tCluster\tPrctile\tPos%s%s%s%s%s%s\n', headers, headers, headers, headers, headers, headers);
headers = sprintf('\t%s', signalTypes{:});
fprintf(outfile, '#TF\tMark\tCluster\tPrctile\tPos%s%s%s%s%s%s\n', headers, headers, headers, headers, headers, headers);
fprintf(outfile, '#TF\tMark\tCluster\tPrctile\tPos%s%s%s%s%s%s\n', ...
  repmat(sprintf('\tMean'), 1, length(signalNames)), repmat(sprintf('\tLowPrc'), 1, length(signalNames)), repmat(sprintf('\tHighPrc'), 1, length(signalNames)), ...
  repmat(sprintf('\tMeanNorm'), 1, length(signalNames)), repmat(sprintf('\tLowPrcNorm'), 1, length(signalNames)), repmat(sprintf('\tHighPrcNorm'), 1, length(signalNames)));
end

function writeSignal(outfile, targetType, signalType, name, numElements, xrange, prcVals, allSignals, allSignalsNorm)

allPrcs = prctile(allSignals, prcVals, 1);
allPrcsNorm = prctile(allSignalsNorm, prcVals, 1);

otherMean = nanmean(allSignals, 1);
otherMeanNorm = nanmean(allSignalsNorm, 1);

for i = 1:length(xrange)
    fprintf(outfile, '%s\t%s\t%s\t%.2f\t%d%s%s%s%s%s%s\n', targetType, signalType, name, numElements, ...
            xrange(i), ...
            sprintf('\t%.4f', otherMean(:, i, :)), sprintf('\t%.4f', allPrcs(1, i, :)), sprintf('\t%.4f', allPrcs(2, i, :)), ...
            sprintf('\t%.4f', otherMeanNorm(:, i, :)), sprintf('\t%.4f', allPrcsNorm(1, i, :)), sprintf('\t%.4f', allPrcsNorm(2, i, :)));
end
end
