% Extends the narrowPeak files with the results of clustering
clearvars
close all

cagtDir = '/media/SeagateStanford/ENCODE/myfiles/cagt/jan2011/matlabRuns/fromPcagt/cagt_run3';
[targetName, signalName, ~, targetType, signalType] = textread('/media/SeagateStanford/ENCODE/myfiles/cagt/jan2011/matlabRuns/rerunList.txt', '%s%s%s%s%s');
peakDir = '/media/SeagateStanford/ENCODE/peaks/jan2011/spp/optimal/';
peakDirCont = dir(peakDir);

for s = 1:length(targetName)
   peakFileInd = find(~cellfun(@isempty, regexp({peakDirCont.name}, targetName{s}, 'once')));
   peakFile = fopen(fullfile(peakDir, peakDirCont(peakFileInd).name), 'r');
   peakData = textscan(peakFile, '%s%s%s%s%s%s%s%s%s%s');
   fclose(peakFile);
   
   dirPref = [signalName{s}, '_around_', targetName{s}];
   disp(dirPref);
   results = load(fullfile(cagtDir, dirPref, 'results.mat'));
   finalInd = results.hcInputInd;
   oversegIdx = zeros(size(finalInd));
   oversegIdx(finalInd) = results.kmeansResults.idx;
   clusterIdx = zeros(size(finalInd));
   clusterIdx(finalInd) = results.hcResults.idx;
   flippedInd = false(size(finalInd));
   flippedInd(finalInd) = results.hcResults.flipInd;
   numPeaks = length(finalInd);
   
   names = strcat(dirPref, '_', arrayfun(@(x) {num2str(x)}, 1:numPeaks));
   peakData{4} = names;
   
   f = fopen(fullfile(cagtDir, dirPref, [dirPref, '_CAGTclusters.narrowPeak']), 'w');
   for i = 1:length(finalInd)
       np = sprintf('%s\t', char(peakData{1}(i)), char(peakData{2}(i)), char(peakData{3}(i)), char(peakData{4}(i)), ...
           char(peakData{5}(i)), char(peakData{6}(i)), char(peakData{7}(i)), char(peakData{8}(i)), char(peakData{9}(i)), char(peakData{10}(i)));
       fprintf(f, '%s\t%d\t%d\t%d\n', np, flippedInd(i), oversegIdx(i), clusterIdx(i));
   end
   fclose(f);
end