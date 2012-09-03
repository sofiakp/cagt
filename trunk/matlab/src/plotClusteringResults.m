function plotParams = plotClusteringResults(X, results, plotParams, plotDir, closeFigs)
%PLOTCLUSTERINGRESULTS Make plots from the output of clusterSignal.
%   PLOTPARAMS = PLOTCLUSTERINGRESULTS(X, RESULTS, PLOTPARAMS, PLOTDIR)
%
% Author: sofiakp

if ~isfield(plotParams, 'medianParams') || ~isfield(plotParams.medianParams, 'lineWidth')
    plotParams.medianParams.lineWidth = 0.8;
end
if ~isfield(plotParams, 'medianParams') || ~isfield(plotParams.medianParams, 'color')
    plotParams.medianParams.color = [0 0 0];
end
if ~isfield(plotParams, 'smallQParams') || ~isfield(plotParams.smallQParams, 'lineWidth')
    plotParams.smallQParams.lineWidth = 0.5;
end
if ~isfield(plotParams, 'smallQParams') || ~isfield(plotParams.smallQParams, 'color')
    plotParams.smallQParams.color = [0.5 0.5 0.5];
end
if ~isfield(plotParams, 'largeQParams') || ~isfield(plotParams.largeQParams, 'lineWidth')
    plotParams.largeQParams.lineWidth = 0.5;
end
if ~isfield(plotParams, 'largeQParams') || ~isfield(plotParams.largeQParams, 'color')
    plotParams.largeQParams.color = [0.8 0.8 0.8];
end

if ~isfield(plotParams, 'step')
    plotParams.step = 1;
end
if ~isfield(plotParams, 'xlim')
    xmax = floor(size(X, 2) / 2) * plotParams.step;
    plotParams.xlim = [-xmax xmax];
end
if ~isfield(plotParams, 'ylim')
    plotParams.ylim = [-4 4];
end
if ~isfield(plotParams, 'magYlim')
    plotParams.magYlim = plotParams.ylim;
end
if ~isfield(plotParams, 'fill')
    plotParams.fill = false;
end
if ~isfield(plotParams, 'plotFiltered')
    plotParams.plotFiltered = true;
end
if ~isfield(plotParams, 'xlabel')
    plotParams.xlabel = 'Relative position';
end
if ~isfield(plotParams, 'ylabel')
    plotParams.ylabel = 'Normalized signal intensity';
end
if ~isfield(plotParams, 'magYlabel')
    plotParams.magYlabel = 'Signal intensity';
end
if ~exist('closeFigs', 'var')
    closeFigs = false;
end
scrsz = get(0,'ScreenSize');
smallFigPos = [1 1 100 100];
smallFont = 3;

figure('Position', smallFigPos);
set(gcf, 'Visible', 'off');
set(gca, 'FontSize', smallFont);
if isfield(results.kmeansResults, 'numMembers')
    totalMem = sum(results.kmeansResults.numMembers);
else
    totalMem = size(X, 1);
end
plotPrcs(X, plotParams, ['All profiles ', num2str(totalMem), ' profiles']);
xlabel(plotParams.xlabel);
ylabel(plotParams.magYlabel);
saveFigure(gcf, fullfile(plotDir, 'all_profiles.png'));
if plotParams.plotFiltered
    numHigh = sum(results.hcInputInd);
    numLow = length(results.hcInputInd) - numHigh;
    if numLow > 0
        figure('Position', smallFigPos);
        set(gcf, 'Visible', 'off');
        set(gca, 'FontSize', smallFont);
        titleStr = ['Low signal: ', num2str(numLow), ' (', num2str(numLow * 100 / length(results.hcInputInd)), '%)'];
        plotPrcs(X(~results.hcInputInd, :), plotParams, titleStr);
        xlabel(plotParams.xlabel);
        ylabel(plotParams.magYlabel);
        saveFigure(gcf, fullfile(plotDir, 'low_signal.png'));
    end
    if numHigh > 0
        figure('Position', smallFigPos);
        set(gcf, 'Visible', 'off');
        set(gca, 'FontSize', smallFont);
        titleStr = ['High signal: ', num2str(numHigh), ' (', num2str(numHigh * 100 / length(results.hcInputInd)), '%)'];
        plotPrcs(X(results.hcInputInd, :), plotParams, titleStr);
        xlabel(plotParams.xlabel);
        ylabel(plotParams.magYlabel);
        saveFigure(gcf, fullfile(plotDir, 'high_signal.png'));
    end
end
if closeFigs
    close all hidden
end

numClust = max(results.kmeansResults.idx);
numRows = ceil(sqrt(numClust));
numCols = ceil(numClust / numRows);
hSub = figure('Position', scrsz);
set(hSub, 'Visible', 'off');
for i = 1:numClust
    figure(hSub);
    set(hSub, 'Visible', 'off');
    subplot(numRows, numCols, i);
    set(gca, 'FontSize', 11);
    if isfield(results.kmeansResults, 'numMembers')
        numMem = results.kmeansResults.numMembers(i);
    else
        numMem = sum(results.kmeansResults.idx == i);
    end
    titleStr = ['Shape ', num2str(i), ': ', num2str(numMem), ...
        ' profiles (', num2str(numMem * 100 / totalMem), '%)'];
    plotPrcs(results.kmeansResults.data(results.kmeansResults.idx == i, :), plotParams, titleStr, plotParams.ylim);
    if mod(i - 1, numCols) == 0
        ylabel(plotParams.ylabel);
    end
    if i + numCols > numClust
        xlabel(plotParams.xlabel);
    end    
    hLone = figure('Position', smallFigPos);
    set(hLone, 'Visible', 'off');
    set(gca, 'FontSize', smallFont);
    plotPrcs(results.kmeansResults.data(results.kmeansResults.idx == i, :), plotParams, titleStr, plotParams.ylim);
    xlabel(plotParams.xlabel);
    ylabel(plotParams.ylabel);
    saveFigure(hLone, fullfile(plotDir, ['oversegmented_shape_cluster_', num2str(i), '.png']));
end
saveFigure(hSub, fullfile(plotDir, 'oversegmented_shape_clusters.png'));
if closeFigs
    close all hidden
end

numClust = max(results.hcResults.idx);
numRows = ceil(sqrt(numClust));
numCols = ceil(numClust / numRows);
hSub = figure('Position', scrsz);
set(hSub, 'Visible', 'off');
for i = 1:numClust
    figure(hSub);
    set(hSub, 'Visible', 'off');
    subplot(numRows, numCols, i); 
    set(gca, 'FontSize', 11);
    if isfield(results.hcResults, 'numMembers')
        numMem = results.hcResults.numMembers(i);
    else
        numMem = sum(results.hcResults.idx == i);
    end
    titleStr = ['Shape ', num2str(i), ': ', num2str(numMem), ...
        ' profiles (', num2str(numMem * 100 / totalMem), '%)'];
    plotPrcs(results.hcResults.data(results.hcResults.idx == i, :), plotParams, titleStr, plotParams.ylim);
    if mod(i - 1, numCols) == 0
        ylabel(plotParams.ylabel);
    end
    if i + numCols > numClust
        xlabel(plotParams.xlabel);
    end    
    hLone = figure('Position', smallFigPos);
    set(hLone, 'Visible', 'off'); 
    set(gca, 'FontSize', smallFont);
    plotPrcs(results.hcResults.data(results.hcResults.idx == i, :), plotParams, titleStr, plotParams.ylim);
    xlabel(plotParams.xlabel);
    ylabel(plotParams.ylabel);
    saveFigure(hLone, fullfile(plotDir, ['shape_cluster_', num2str(i), '.png']));
end
saveFigure(hSub, fullfile(plotDir, 'shape_clusters.png'));
if closeFigs
    close all hidden
end
end

function saveFigure(h, name)
set(h,'PaperPositionMode','auto');
print(h, name, '-dpng', '-r450');
end