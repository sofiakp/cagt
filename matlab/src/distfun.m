function [D, bestLags] = distfun(params, X, Y)
%DISTFUN Calculate point to cluster centroid distances.
%
%   D = DISTFUN(PARAMS, X, Y) computes the distance between each row of X
%   and each row of Y. If X is an n-by-p matrix and Y is an m-by-p matrix,
%   then D will be n-by-m. PARAMS is a structure with parameters
%   determining how the distance will be computed.
%
%   PARAMS fields:
%      distance: Distance function, in P-dimensional space, that KMEANS
%      should minimize with respect to.  Choices are:
%          'sqeuclidean'  - Squared Euclidean distance (the default)
%          'correlation'  - One minus the sample correlation between points
%                           (treated as sequences of values)
%          'xcorr'        - One minus the maximum sample cross-correlation
%                           over all possible lags (see the option
%                           'maxlag')
%
%      maxlag: Maximum lag when xcorr is used as the distance measure.
%      Otherwise maxlag will be set to 0 and the value passed will be
%      ignored.
%
%      normalize: boolean indicating whether X and Y should be centered to
%      zero mean and unit standard deviation (so that the correlation
%      between each pair of rows of and Y is just their product). This
%      should be set to true if correlation or xcorr is used, unless the
%      matrices are already centered.
% 
%   [D, BESTLAGS] = DISTFUN(...) also returns an n-by-m matrix with the lag
%   that maximizes the cross correlation for each pair of rows of X and Y.
%   If DIST is not xcorr, this will be all zeros.
%
%   Author: Sofia Kyriazopoulou (sofiakp@stanford.edu)

if ~isfield(params, 'distance')
    distance = 'sqeuclidean';
else
    distance = params.distance;
end
if ~isfield(params, 'maxlag')
    maxlag = 0;
else
    maxlag = params.maxlag;
end
if ~isfield(params, 'normalize')
    normalize = true;
else
    normalize = params.normalize;
end

if nargin < 3
    self = true;
    Y = X;
else
    self = false;
end
[n, p] = size(X);
m = size(Y, 1);
if nargout > 1
    bestLags = zeros(n, m);
end

if normalize && ismember(distance, {'correlation', 'xcorr'})
    X = X - repmat(nanmean(X, 2), 1, p);
    Xnorm = nanstd(X, 0, 2);
    if any(min(Xnorm) <= eps(max(Xnorm)))
        error('distfun:ConstantDataForCorr', ...
            ['Some points have small relative standard deviations, making them ', ...
            'effectively constant.\nEither remove those points, or choose a ', ...
            'distance other than ''correlation''.']);
    end
    X = X ./ Xnorm(:, ones(1, p));
    if ~self
        Y = Y - repmat(nanmean(Y, 2), 1, p);
        Ynorm = nanstd(Y, 0, 2);
        if any(min(Ynorm) <= eps(max(Ynorm)))
            error('distfun:ConstantDataForCorr', ...
                ['Some points have small relative standard deviations, making them ', ...
                'effectively constant.\nEither remove those points, or choose a ', ...
                'distance other than ''correlation''.']);
        end
        Y = Y ./ Ynorm(:, ones(1, p));
    end
end

switch distance
    case 'sqeuclidean'
        prod = dot(Y, Y, 2);
        D = bsxfun(@plus, -2 * X * Y', prod');
        if self
            D = bsxfun(@plus, -2 * X * Y', prod);
        else
            D = bsxfun(@plus, D, dot(X, X, 2));
        end
    case 'correlation'
        D = zeros(n, m);
        if self
            for i = 1:m
                D(1:i, i) = max(1 - (X(1:i, :) * X(i, :)' / (p - 1)), 0);
            end
            D = D + tril(D', -1);
        else
            for i = 1:m
                D(:, i) = max(1 - (X * Y(i,:)' / (p - 1)), 0);
            end
        end
    case 'xcorr'
        D = zeros(n, m);
        if self
            for j = 1:n
                for i = j + 1:m
                    [xc, lags] = xcorr(X(j, :), Y(i, :), maxlag, 'coeff');
                    [maxC, maxInd] = max(xc);
                    maxLag = lags(maxInd);
                    D(j, i) = max(1 - maxC, 0);
                    bestLags(j, i) = maxLag;
                end
            end
            D = D + tril(D', -1);
        else
            for j = 1:n
                for i = 1:m
                    [xc, lags] = xcorr(X(j, :), Y(i, :), maxlag, 'coeff');
                    [maxC, maxInd] = max(xc);
                    maxLag = lags(maxInd);
                    D(j, i) = max(1 - maxC, 0);
                    bestLags(j, i) = maxLag;
                end
            end
        end
end
end