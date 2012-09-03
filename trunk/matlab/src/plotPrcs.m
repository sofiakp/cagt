function plotPrcs(data, plotParams, titleStr, ylims)
if ~isfield(plotParams, 'xrange')
    xrange = plotParams.xlim(1):plotParams.step:plotParams.xlim(2);
else
    xrange = plotParams.xrange;
end
prcPoints = [90, 75, 25, 10];
prcs = prctile(data, prcPoints, 1);
if nargin < 4
    ylims = [min(prcs(:)) max(prcs(:))];
end

for j = 1:size(prcs, 1)
    if plotParams.fill
        if prcPoints(j) == 90 || prcPoints(j) == 25;
            p = plotParams.largeQParams;
        elseif prcPoints(j) == 75
            p = plotParams.smallQParams;
        else
            p.color = [1 1 1];
        end
        
        area(xrange, prcs(j, :), ylims(1), 'FaceColor', p.color, 'EdgeColor', p.color); hold on;
    else
        if prcPoints(j) == 90 || prcPoints(j) == 10
            p = plotParams.largeQParams;
        else
            p = plotParams.smallQParams;
        end
        plot(xrange, prcs(j, :), 'LineWidth', p.lineWidth, 'Color', p.color); hold on;
    end
end
plot(xrange, nanmedian(data, 1), 'LineWidth', plotParams.medianParams.lineWidth, 'Color', plotParams.medianParams.color); hold on;
plot([0 0], [ylims(1) ylims(2)], 'k--'); hold on;
plot([plotParams.xlim(1) plotParams.xlim(2)], [0 0], 'k--'); hold on;
ylim(ylims);
xlim(plotParams.xlim);
hold off;
title(titleStr);
end