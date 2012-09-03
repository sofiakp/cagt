function makeSignalTable(fname, selTf, datasetsFile, cagtDir, signalDir, gcDir, params)
% Creates text tables with the signal in a set of cluasters and matching
% signals for other marks in the same set of peaks.
% Input arguments:
% fname: path of output file
% datasetsFile: lists the available datasets in the usual format of
% run lists. It will be used to find the matching signals for the input
% target.
% selTf: structure with fields signalName, targetName, signalType,
% targetType for the dataset whose clusters we'll output. For each cluster
% of this dataset, we will output the signal of the peaks in the cluster
% as well as the signal of these peaks in all other datasets.
% gcDir: directory of gc files
% params: has signalRange, xRange, gcRange to restrict the read signals

[targetName, signalName, ~, ~, signalType] = textread(datasetsFile, '%s%s%s%s%s');

signalRange = params.signalRange;
if ~isfield(params, 'xrange')
    xrange = signalRange;
else
    xrange = params.xrange;
end
if ~isfield(params, 'gcRange')
    gcRange = signalRange;
else
    gcRange = params.gcRange;
end

if length(signalRange) ~= length(gcRange) || length(signalRange) ~= length(xrange)
    error('MyErr:InconsitentInputs', 'All range vectors must have the same length');
end
selSignalName = selTf.signalName;
selTargetName = selTf.targetName;
selSignalType = selTf.signalType;
selTargetType = selTf.targetType;

if isfield(params, 'merged')
    merged = params.merged;
else
    merged = false;
end
if isfield(params, 'writeIds')
    writeIds = params.writeIds;
else
    writeIds = false;
end

if isfield(params, 'gerpDir')
    writeGerp = true;
    gerpDir = params.gerpDir;
    gerpRange = params.gerpRange;
else
    writeGerp = false;
end

if isstruct(cagtDir)
    results = cagtDir;
else
    cagtSubdir = [selSignalName, '_around_', selTargetName];
    infile = fullfile(cagtDir, cagtSubdir, 'results.mat');
    if ~exist(infile, 'file')
        warning('MyWarn:MissingFile', ['Results file missing: ', infile]);
        return;
    end
    results = load(infile);
end
load(fullfile(signalDir, selTargetName, [selTargetName, '_AT_', selSignalName, '.mat']), 'signal');
signal = signal(:, signalRange);
numPeaks = size(signal, 1);

selLines = find(strcmp(targetName, selTargetName)  & ~strcmp(signalName, selSignalName));
allSignals = nan(numPeaks, length(signalRange), length(selLines) + 1 + writeGerp, 'single');
for i = 1:length(selLines)
    signalStruct = load(fullfile(signalDir, selTargetName, [selTargetName, '_AT_', signalName{selLines(i)}, '.mat']), 'signal');
    if size(signalStruct.signal, 1) ~= numPeaks
        warning('MyWarn:IncompatibleInputs', ['Incompatible numbers of peaks for ', cagtSubdir, ' and ', selTargetName, '_AT_', signalName{selLines(i)}, '.mat']);
        return;
    end
    allSignals(:, :, i) = signalStruct.signal(:, signalRange);
end

gcFile = fullfile(gcDir, [selTargetName, '_gc.mat']);
if ~exist(gcFile, 'file')
    warning('MyWarn:MissingFile', ['GC file missing for: ', selTargetName]);
else
    load(gcFile);
    if size(gc, 1) ~= numPeaks
        warning('MyWarn:IncompatibleInputs', ['Incompatible numbers of peaks for ', cagtSubdir, ' and ', selTargetName, '_gc.mat']);
        return;
    end
    allSignals(:, :, end - writeGerp) = gc(:, gcRange);
end

if writeGerp
    gerpFile = fullfile(gerpDir, [selTargetName, '_gerp.mat']);
    if ~exist(gerpFile, 'file')
        warning('MyWarn:MissingFile', ['GERP file missing for: ', selTargetName]);
    else
        gerpStruct = load(gerpFile, 'signal');
        if size(gerpStruct.signal, 1) ~= numPeaks
            warning('MyWarn:IncompatibleInputs', ['Incompatible numbers of peaks for ', cagtSubdir, ' and ', selTargetName, '_gerp.mat']);
            return;
        end
        allSignals(:, :, end) = gerpStruct.signal(:, gerpRange);
    end
end

outfile = fopen(fname, 'w');

signalMean = nanmean(signal, 2);
signalStd = nanstd(signal, 0, 2);
normSignal = (signal - repmat(signalMean, 1, length(signalRange))) ./ repmat(signalStd, 1, length(signalRange));

normAllSignals = allSignals;
for i = 1:length(selLines) + 1
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

if writeGerp
    writeHeader(outfile, [signalName(selLines); 'GC'; 'GERP'], [signalType(selLines); 'GC'; 'GERP'], writeIds);
else
    writeHeader(outfile, [signalName(selLines); 'GC'], [signalType(selLines); 'GC'], writeIds);
end
writeSignal(outfile, selTargetType, selSignalType, 'all', numPeaks, xrange, ...
    signal, normSignal, allSignals, normAllSignals, writeIds, 0, 0);

writeSignal(outfile, selTargetType, selSignalType, 'low', ...
    nnz(~input) * 100 / numPeaks, xrange, ...
    signal(~input, :), normSignal(~input, :), ...
    allSignals(~input, :, :), normAllSignals(~input, :, :), writeIds, 0, 0);

writeSignal(outfile, selTargetType, selSignalType, 'high', ...
    nnz(input) * 100 / numPeaks, xrange, ...
    signal(input, :), normSignal(input, :), ...
    allSignals(input, :, :), normAllSignals(input, :, :), writeIds, 0, 0);

numClust = max(idx);
signal = signal(input, :);
signal(flipInd, :) = signal(flipInd, end:-1:1);
normSignal = normSignal(input, :);
normSignal(flipInd, :) = normSignal(flipInd, end:-1:1);

allSignals = allSignals(input, :, :);
allSignals(flipInd, :, :) = allSignals(flipInd, length(signalRange):-1:1, :);
normAllSignals = normAllSignals(input, :, :);
normAllSignals(flipInd, :, :) = normAllSignals(flipInd, length(signalRange):-1:1, :);

if isfield(params, 'writeIds')
    colIds = params.colIds;
    rowIds = params.rowIds;
else
    colIds = 1:numClust;
    rowIds = ones(numClust, 1);
end
for i = 1:numClust,
    writeSignal(outfile, selTargetType, selSignalType, ['shape', num2str(i)], ...
        nnz(idx == i) * 100 / numPeaks, xrange, ...
        signal(idx == i, :), normSignal(idx == i, :), ...
        allSignals(idx == i, :, :), normAllSignals(idx == i, :, :), writeIds, colIds(i), rowIds(i));
end

fclose(outfile);
end

function writeHeader(outfile, signalNames, signalTypes, writeIds)
if writeIds
    extraCols = sprintf('\t%s\t%s', 'ColId', 'RowId');
else
    extraCols = '';
end
if isempty(signalNames)
    fprintf(outfile, '#TF\tMark\tCluster\tPrctile\tPos\tMark\tMark\tMark\tMark\tMark\tMark%s\n', extraCols);
    fprintf(outfile, '#TF\tMark\tCluster\tPrctile\tPos\tSIGNAL\tSIGNAL\tSIGNAL\tSIGNAL\tSIGNAL\tSIGNAL%s\n', extraCols);
    fprintf(outfile, '#TF\tMark\tCluster\tPrctile\tPos\tMedian\tLowPrc\tHighPrc\tMedianNorm\tLowPrcNorm\tHighPrcNorm%s\n', extraCols);
else
    headers = sprintf('\t%s', signalNames{:});
    fprintf(outfile, '#TF\tMark\tCluster\tPrctile\tPos\tMark\tMark\tMark%s%s%s\tMark\tMark\tMark%s%s%s%s\n', headers, headers, headers, headers, headers, headers, extraCols);
    headers = sprintf('\t%s', signalTypes{:});
    fprintf(outfile, '#TF\tMark\tCluster\tPrctile\tPos\tSIGNAL\tSIGNAL\tSIGNAL%s%s%s\tSIGNAL\tSIGNAL\tSIGNAL%s%s%s%s\n', headers, headers, headers, headers, headers, headers, extraCols);
    fprintf(outfile, '#TF\tMark\tCluster\tPrctile\tPos\tMedian\tLowPrc\tHighPrc%s%s%s\tMedianNorm\tLowPrcNorm\tHighPrcNorm%s%s%s%s\n', ...
        repmat(sprintf('\tMedian'), 1, length(signalNames)), repmat(sprintf('\tLowPrc'), 1, length(signalNames)), repmat(sprintf('\tHighPrc'), 1, length(signalNames)), ...
        repmat(sprintf('\tMedianNorm'), 1, length(signalNames)), repmat(sprintf('\tLowPrcNorm'), 1, length(signalNames)), repmat(sprintf('\tHighPrcNorm'), 1, length(signalNames)), extraCols);
end
end

function writeSignal(outfile, targetType, signalType, name, prc, xrange, signal, signalNorm, allSignals, allSignalsNorm, writeIds, colId, rowId)
if ~writeIds
    extraCols = '';
else
    extraCols = sprintf('\t%d\t%d', colId, rowId);
end
prcs = prctile(signal, [10 90], 1);
prcsNorm = prctile(signalNorm, [10 90], 1);
allPrcs = prctile(allSignals, [10 90], 1);
allPrcsNorm = prctile(allSignalsNorm, [10 90], 1);

signalMean = nanmean(signal, 1);
signalMeanNorm = nanmean(signalNorm, 1);
otherMean = nanmean(allSignals, 1);
otherMeanNorm = nanmean(allSignalsNorm, 1);
numOtherSignals = size(allSignals, 3);

for i = 1:length(xrange)
    if numOtherSignals == 0
        fprintf(outfile, '%s\t%s\t%s\t%.2f\t%d\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f%s\n', targetType, signalType, name, prc, ...
            xrange(i), signalMean(i), prcs(1, i), prcs(2, i), signalMeanNorm(i), prcsNorm(1, i), prcsNorm(2, i), extraCols);
    else
       fprintf(outfile, '%s\t%s\t%s\t%.2f\t%d\t%.4f\t%.4f\t%.4f%s%s%s\t%.4f\t%.4f\t%.4f%s%s%s%s\n', targetType, signalType, name, prc, ...
            xrange(i), signalMean(i), prcs(1, i), prcs(2, i), ...
            sprintf('\t%.4f', otherMean(:, i, :)), sprintf('\t%.4f', allPrcs(1, i, :)), sprintf('\t%.4f', allPrcs(2, i, :)), ...
            signalMeanNorm(i), prcsNorm(1, i), prcsNorm(2, i), ...
            sprintf('\t%.4f', otherMeanNorm(:, i, :)), sprintf('\t%.4f', allPrcsNorm(1, i, :)), sprintf('\t%.4f', allPrcsNorm(2, i, :)), extraCols);
    end
end
end
