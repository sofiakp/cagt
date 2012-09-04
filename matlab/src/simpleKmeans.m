function results = simpleKmeans(X, params, distParams)
%SIMPLEKMEANS k-means or k-medians clustering.
%
%   RESULTS = SIMPLEKMEANS(X, PARAMS, DISTPARAMS) partitions the rows of
%   an N-by-P data matrix X into clusters.  This partition minimizes the
%   sum, over all clusters, of the within-cluster sums of
%   point-to-cluster-centroid distances. PARAMS is a struct with the parameters
%   for the clustering. DISTPARAMS is a structure with the parameters that
%   determine the distance function that will be used for clustering. Most
%   the input parameters were chosen to match the parameters of the
%   standard kmeans function of MATLAB.
%   RESULTS is a structure with information about the resulting clusters.
% 
%   PARAMS fields:
%
%      k: number of clusters
%
%      start: Method used to choose initial cluster centroid positions,
%      sometimes known as "seeds".  Choices are:
%          'plus'    - k-means++ initialization (default). 
%          'sample'  - Select k observations from X at random.
%           matrix   - A k-by-P matrix of starting locations.  In this case,
%                      the k parameter can be omitted, and K will be inferred from
%                      the first dimension of the matrix.  You can also
%                      supply a 3D array, implying a value for replicates
%                      from the array's third dimension.
%
%      replicates: Number of times to repeat the clustering, each with a
%      new set of initial centroids.  A positive integer, default is 1.
%
%      emptyaction: Action to take if a cluster loses all of its member
%      observations.  Choices are:
%          'error'     - Treat an empty cluster as an error (the default)
%          'drop'      - Remove any clusters that become empty, and set
%                        the corresponding values in C and D to NaN.
%          'singleton' - Create a new cluster consisting of the one
%                        observation furthest from its centroid.
%
%      maxiter: Maximum number of iterations. Default is 100.
%
%      display: Determines how much output will be printed. Choices are:
%          '' (empty string) - No output (default)
%          'iter'            - Output at each iteration
%          'final'           - Output only after the last iteration.
%
%      online: Flag indicating whether an "on-line update phase should be
%      performed in addition to a "batch update" phase.  The on-line phase
%      can be time consuming for large data sets, but guarantees a solution
%      that is a local minimum of the distance criterion, i.e., a partition
%      of the data where moving any single point to a different cluster
%      increases the total sum of distances.  NOT SUPPORTED YET. Logical,
%      default is false.
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
%      idx: N x 1 vector with the cluster indices for the N datapoints. 
% 
%      centroids: k x P matrix of the cluster centroids.
%
%      dataToCentroidDist: N x k matrix with the distance between each
%      datapoint and each centroid.
%
%      centroidDist: k x k matrix with the distances between all centroids.
%
%      data: the data used for the clustering (after whatever normalization
%      took place). 
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
%   See also kmeans.
%
%   Author: Sofia Kyriazopoulou (sofiakp@stanford.edu)

if isfield(params, 'k')
    k = params.k; 
else
    k = 0;
end
if isfield(params, 'start')
    start = params.start;
else
    start = 'plus';
end
if isfield(params, 'replicates')
    reps = params.replicates;
else
    reps = [];
end
if isfield(params, 'emptyaction')
    emptyact = params.emptyaction;
else
    emptyact = 'error';
end
if isfield(params, 'maxiter')
    maxit = params.maxiter;
else
    maxit = 100;
end
if isfield(params, 'display')
    display = params.display;
else
    display = '';
end

if isfield(distParams, 'distance')
    distance = distParams.distance;
else
    distance = 'sqeuclidean';
    distParams.distance = distance;
end
if isfield(distParams, 'maxlag')
    maxlag = distParams.maxlag;
else
    maxlag = 0;
end
if isfield(distParams, 'avgFun')
    avgFun = distParams.avgFun;
else
    avgFun = 'mean';
    distParams.avgFun = avgFun;
end
if isfield(params, 'online')
    online = params.online;
    if strcmp(distParams.avgFun, 'median') && online
        warning('simplekmeans:IgnoredArgument', 'online updates are only supported when the avgFun is ''mean''');
        online = false;
    end
else
    online = false;
end

validateReal(X, 'X');
validateRange(distance, {'sqeuclidean', 'correlation', 'xcorr'}, 'distance');
validateRange(avgFun, {'mean', 'median'}, 'avgFun');
validateReal(reps, 'replicates');
validateRange(emptyact, {'error', 'drop', 'singleton'}, 'emptyaction');
validateRange(display, {'', 'iter', 'final'}, 'display');

% Remove rows with missing data
nanRowInd = any(isnan(X), 2);
if any(nanRowInd)
    X = X(~nanRowInd, :);
    warning('simplekmeans:MissingData', 'Ignoring %d row(s) of X with missing data.', sum(nanRowInd));
end

% n points in p dimensional space
[n, p] = size(X);

if ~isint(maxit) || maxit < 1
    error('simplekmeans:InvalidArgument', '''maxiter'' must be a positive integer');
end

if ~isint(maxlag) || maxlag < 0,
    error('simplekmeans:InvalidArgument', '''maxlag'' must be a non-negative integer');
elseif maxlag > 0 && ~strcmp(distance, 'xcorr')
    warning('simplekmeans:IgnoredArgument', '''maxlag'' only applies to xcorr. Input value will be replaced by 0.');
    maxlag = 0;
    distParams.maxlag = 0;
end

% For correlation, we subtract the mean to make the computation of the
% correlation faster. (This is not really needed for xcorr).
if strcmp(distance, 'correlation') || strcmp(distance, 'xcorr')
    X = X - repmat(mean(X, 2), 1, p);
    Xnorm = std(X, 0, 2);
    if any(Xnorm <= eps(class(Xnorm)))
        error('simplekmeans:ConstantDataForCorr', ...
            ['Some points have small relative standard deviations, making them ', ...
            'effectively constant.\nEither remove those points, or choose a ', ...
            'distance other than ''correlation''.']);
    end
    X = X ./ repmat(Xnorm, 1, p);
end

if ischar(start)
    validateRange(start, {'sample', 'plus'}, 'start');
    if k <= 0
        error('simplekmeans:MissingK', ...
            'The number of clusters,''k'', must be a positive integer. You must specify ''k'' either explicitly or by specifying a start matrix.');
    end
elseif isnumeric(start)
    CC = start;
    start = 'numeric';
    if k <= 0
        k = size(CC, 1);
    elseif k ~= size(CC, 1);
        error('simplekmeans:MisshapedStart', ...
            'The ''start'' matrix must have k rows.');
    elseif size(CC, 2) ~= p
        error('simplekmeans:MisshapedStart', ...
            'The ''start'' matrix must have the same number of columns as X.');
    end
    if isempty(reps)
        reps = size(CC, 3);
    elseif reps ~= size(CC,3);
        error('simplekmeans:MisshapedStart', ...
            'The third dimension of the ''start'' array must match the ''replicates'' parameter value.');
    end
    
    % Need to center explicit starting points for 'correlation'. (Re)normalization
    % for 'cosine'/'correlation' is done at each iteration.
    if ismember(distance, {'correlation', 'xcorr'})
        CC = CC - repmat(mean(CC, 2),[1,p,1]);
        % Renormalize centroids
        s = std(CC, 0, 2);
        if any(s(:) < eps(class(s(:)))) % small relative to unit-length data points
            error('simplekmeans:ZeroCentroid', ...
                'Initial centroids contain a zero centroid.');
        end
        CC = CC ./ repmat(s, [1, p, 1]);
    end
else
    error('simplekmeans:InvalidArgument', ...
          'The ''start'' parameter value must be a string or a numeric matrix or array.');
end

if ~isint(k) || k <= 0
    error('simplekmeans:InvalidK', ...
          'The number of clusters ''k'' must be a positive integer value.');
elseif n < k
    warning('simplekmeans:TooManyClusters', ...
        'Value of ''k'' is larger than the number of data-points. Setting to the number of data-points.');
    k = n;
end

% Assume one replicate
if isempty(reps)
    reps = 1;
end

% Done with input argument processing, begin clustering
dispfmt = '%6d\t%6d\t%8d\t%12g\n';
if online, Del = NaN(n,k); end % reassignment criterion

totsumDBest = Inf;
emptyErrCnt = 0;
bestLags = zeros(n, 1);
recenterCentroids = ismember(distance, {'correlation', 'xcorr'});

distParams.normalize = false;

for rep = 1:reps
    switch start
    case 'sample'
        C = X(randsample(n,k), :);
        if ~isfloat(C)      % X may be logical
            C = double(C);
        end
    case 'plus'
        C = kmeansppInit(X, k);
    case 'numeric'
        C = CC(:, :, rep);
    end
    
    % catch empty cluster errors and zero centroid errors and move on to
    % next replicate. Initial kmeans implementation doesn't catch zero
    % centroid errors (not sure why).
    try 
        % Compute the distance from every point to each cluster centroid and the
        % initial assignment of points to clusters
        [D, lags] = distfun(distParams, X, C);
        [d, idx] = min(D, [], 2);
        % optimal lags for optimal cluster assignment
        if strcmp(distance, 'xcorr')
            bestLags = lags((idx-1)*n + (1:n)');
        end
        % Number of points for each cluster index
        m = accumarray(idx,1,[k,1]);
        
        % Begin phase one:  batch reassignments
        converged = batchUpdate();
        
        % Begin phase two:  single reassignments
        if online
            converged = onlineUpdate();
        end
        
        if ~converged
            warning('simplekmeans:FailedToConverge', ...
                'Failed to converge in %d iterations%s.', maxit, repsMsg(rep,reps));
        end
        
        % Calculate cluster-wise sums of distances
        nonempties = find(m > 0);
        % Distance from all points to all centroids of non-empty clusters.
        [D(:,nonempties), lags(:, nonempties)] = distfun(distParams, X, C(nonempties,:));
        d = D((idx-1)*n + (1:n)');
        if strcmp(distance, 'xcorr')
            bestLags = lags((idx-1)*n + (1:n)');
        end
        sumD = accumarray(idx,d,[k,1]);
        totsumD = sum(sumD);
        
        if strcmp(display, 'iter') || strcmp(display, 'final')
            fprintf('%d iterations, total sum of distances = %g\n', iter, totsumD);
        end
        
        % Save the best solution so far
        if totsumD < totsumDBest
            totsumDBest = totsumD;
            idxBest = idx;
            Cbest = C;
            sumDBest = sumD;
            Dbest = D;
            Lbest = lags;
        end
    catch ME
        % If an empty cluster error occurred in one of multiple replicates, catch
        % it, warn, and move on to next replicate.  Error only when all replicates
        % fail.  Rethrow an other kind of error.
        if reps == 1 || ~ismember(ME.identifier, {'simplekmeans:EmptyCluster', 'gcentroids:ZeroCentroid', 'gcentroids:NaNCentroid'})
            rethrow(ME);
        else
            emptyErrCnt = emptyErrCnt + 1;
            switch ME.identifier
                case 'simplekmeans:EmptyCluster'
                    warning('simplekmeans:EmptyCluster', ...
                        'Replicate %d terminated: empty cluster created at iteration %d.',rep,iter);
                case 'simplekmeans:ZeroCentroid'
                    warning('simplekmeans:ZeroCentroid', ...
                        'Replicate %d terminated: zero centroid created at iteration %d.',rep,iter);
                case 'simplekmeans:NaNCentroid'
                    warning('simplekmeans:NaNCentroid', ...
                        'Replicate %d terminated: NaN centroid created at iteration %d.',rep,iter);
            end
            if emptyErrCnt == reps
                error('simplekmeans:ErrAllReps', ...
                    'An empty cluster or zero/NaN centroid error occurred in every replicate.');
            end
        end
    end % catch    
end % replicates

% Return the best solution after rearranging the clusters based on
% occupancy.
[newIdx, sortIdx] = sortClusters(idxBest);
results.idx = newIdx;
results.centroids = Cbest(sortIdx, :);
results.lags = Lbest(:, sortIdx);
results.bestLags = results.lags((results.idx-1)*n + (1:n)');
results.dataToCentroidDist = Dbest(:, sortIdx);
results.bestDist = results.dataToCentroidDist((results.idx-1)*n + (1:n)');
distParams.maxlag = 0;
results.centroidDist = distfun(distParams, results.centroids);
results.data = X;

% I DON'T put back rows that had NaNs. Original kmeans only does it for the
% idx vector which seems inconsistent to me.
%if any(nanRowInd)
%    newIdx = zeros(size(idx));
%    idx = statinsertnan(wasnan, idx);
%end

%------------------------------------------------------------------

function converged = batchUpdate

% Every point moved, every cluster will need an update
moved = 1:n;
changed = 1:k;
previdx = zeros(n,1);
prevtotsumD = Inf;

if strcmp(display, 'iter')
    fprintf('  iter\t phase\t     num\t         sum\n');
end

% Begin phase one:  batch reassignments
iter = 0;
converged = false;
while true
    iter = iter + 1;

    % Calculate the new cluster centroids and counts, and update the
    % distance from every point to those new cluster centroids
    [C(changed,:), m(changed)] = gcentroids(X, idx, changed, avgFun, recenterCentroids, bestLags);
    [D(:,changed), lags(:, changed)] = distfun(distParams, X, C(changed,:));

    % Deal with clusters that have just lost all their members
    empties = changed(m(changed) == 0);
    if ~isempty(empties)
        switch emptyact
            case 'error'
                error('simplekmeans:EmptyCluster', ...
                    'Empty cluster created at iteration %d%s.', iter, repsMsg(rep,reps));
            case 'drop'
                % Remove the empty cluster from any further processing
                D(:, empties) = NaN;
                lags(:, empties) = NaN; 
                changed = changed(m(changed) > 0);
                warning('simplekmeans:EmptyCluster', ...
                    'Empty cluster created at iteration %d%s.', iter, repsMsg(rep,reps));
            case 'singleton'
                warning('simplekmeans:EmptyCluster', ...
                    'Empty cluster created at iteration %d%s.', iter, repsMsg(rep,reps));
                
                for i = empties
                    % Get distance from each point to closest cluster
                    d = D((idx-1)*n + (1:n)'); % use newly updated distances
                    
                    % Find the point furthest away from its current cluster.
                    % Take that point out of its cluster and use it to create
                    % a new singleton cluster to replace the empty one.
                    [~, lonely] = max(d);
                    from = idx(lonely); % taking from this cluster
                    if m(from) < 2
                        % In the very unusual event that the cluster had only
                        % one member, pick any other non-singleton point.
                        from = find(m > 1, 1, 'first');
                        lonely = find(idx == from, 1, 'first');
                    end
                    C(i, :) = X(lonely, :);
                    m(i) = 1;
                    idx(lonely) = i;
                    [D(:, i), lags(:, i)] = distfun(distParams, X, C(i,:));
                    
                    % Update clusters from which points are taken
                    [C(from,:), m(from)] = gcentroids(X, idx, from, avgFun, recenterCentroids, bestLags);
                    [D(:,from), lags(:, from)] = distfun(distParams, X, C(from,:));
                    changed = unique([changed from]);
                end
        end
    end

    % Compute the total sum of distances for the current configuration.
    totsumD = sum(D((idx-1)*n + (1:n)'));
    % Test for a cycle: if objective is not decreased, back out
    % the last step and move on to the single update phase
    if prevtotsumD <= totsumD
        idx = previdx;
        [C(changed,:), m(changed)] = gcentroids(X, idx, changed, avgFun, recenterCentroids, bestLags);
        iter = iter - 1;
        break;
    end
    if strcmp(display, 'iter')
        fprintf(dispfmt,iter,1,length(moved),totsumD);
    end
    if iter >= maxit
        break;
    end

    % Determine closest cluster for each point and reassign points to clusters
    previdx = idx;
    prevtotsumD = totsumD;
    [d, nidx] = min(D, [], 2);
    
    % Determine which points moved
    moved = find(nidx ~= previdx);
    if ~isempty(moved)
        % Resolve ties in favor of not moving
        moved = moved(D((previdx(moved)-1)*n + moved) > d(moved));
    end
    if isempty(moved)
        converged = true;
        break;
    end
    % Update the optimal assignments and lags for the points that actually
    % moved.
    idx(moved) = nidx(moved);
    if strcmp(distance, 'xcorr')
        bestLags = lags((idx - 1) * n + (1:n)');
    end

    % Find clusters that gained or lost members
    changed = unique([idx(moved); previdx(moved)])';

end % phase one
end % nested function

%------------------------------------------------------------------

function converged = onlineUpdate

% Begin phase two:  single reassignments
changed = find(m' > 0);
lastmoved = 0;
nummoved = 0;
iter1 = iter;
converged = false;
while iter < maxit
    % Calculate distances to each cluster from each point, and the
    % potential change in total sum of errors for adding or removing
    % each point from each cluster.  Clusters that have not changed
    % membership need not be updated.
    %
    % Singleton clusters are a special case for the sum of dists
    % calculation.  Removing their only point is never best, so the
    % reassignment criterion had better guarantee that a singleton
    % point will stay in its own cluster.  Happily, we get
    % Del(i,idx(i)) == 0 automatically for them.
    if strcmp(avgFun, 'mean')
        switch distance
            case 'sqeuclidean'
                for i = changed
                    mbrs = (idx == i);
                    sgn = 1 - 2*mbrs; % -1 for members, 1 for nonmembers
                    if m(i) == 1
                        sgn(mbrs) = 0; % prevent divide-by-zero for singleton mbrs
                    end
                    % I think this is wrong...
                    Del(:,i) = (m(i) ./ (m(i) + sgn)) .* sum((X - C(repmat(i,n,1),:)).^2, 2);
                    % This is my version
                    % Del(:,i) = (m(i) ./ (m(i) + sgn)).^2 .* sum((X - C(repmat(i,n,1),:)).^2, 2);
                end
            case 'correlation'
                % This can be done without a loop, but the loop saves memory allocations
                for i = changed
                    XCi = X * C(i,:)';
                    mbrs = (idx == i);
                    sgn = 1 - 2*mbrs; % -1 for members, 1 for nonmembers
                    Del(:,i) = 1 + sgn .*...
                        (m(i).*C(i) - sqrt((m(i).*normC(i)).^2 + 2.*sgn.*m(i).*XCi + 1));
                end
        end
    end

    % Determine best possible move, if any, for each point.  Next we
    % will pick one from those that actually did move.
    previdx = idx;
    prevtotsumD = totsumD;
    [minDel, nidx] = min(Del, [], 2);
    moved = find(previdx ~= nidx);
    if ~isempty(moved)
        % Resolve ties in favor of not moving
        moved = moved(Del((previdx(moved)-1)*n + moved) > minDel(moved));
    end
    if isempty(moved)
        % Count an iteration if phase 2 did nothing at all, or if we're
        % in the middle of a pass through all the points
        if (iter == iter1) || nummoved > 0
            iter = iter + 1;
            if display > 2 % 'iter'
                fprintf(dispfmt,iter,2,nummoved,totsumD);
            end
        end
        converged = true;
        break;
    end

    % Pick the next move in cyclic order
    moved = mod(min(mod(moved - lastmoved - 1, n) + lastmoved), n) + 1;

    % If we've gone once through all the points, that's an iteration
    if moved <= lastmoved
        iter = iter + 1;
        if display > 2 % 'iter'
            fprintf(dispfmt,iter,2,nummoved,totsumD);
        end
        if iter >= maxit, break; end
        nummoved = 0;
    end
    nummoved = nummoved + 1;
    lastmoved = moved;

    oidx = idx(moved);
    nidx = nidx(moved);
    totsumD = totsumD + Del(moved,nidx) - Del(moved,oidx);

    % Update the cluster index vector, and the old and new cluster
    % counts and centroids
    idx(moved) = nidx;
    m(nidx) = m(nidx) + 1;
    m(oidx) = m(oidx) - 1;
    % This does not properly deal with NaNs!!!!!!!
    switch avgFun
        case 'mean'
            C(nidx,:) = C(nidx,:) + (X(moved,:) - C(nidx,:)) / m(nidx);
            C(oidx,:) = C(oidx,:) - (X(moved,:) - C(oidx,:)) / m(oidx);
    end
    changed = sort([oidx nidx]);
    %if recenterCentroids
    %     
    %end
end % phase two
end % nested function

end % main function

function s = repsMsg(rep,reps)
% Utility for warning and error messages.
if reps == 1
    s = '';
else
    s = sprintf(' during replicate %d',rep);
end
end % function

function b = validateRange(x, range, argName)
if ~ischar(x)
    error('simplekmeans:InvalidArgument', 'Invalid parameter value for ''%s.''', argName);
elseif ~ismember(x, range)
    error('simplekmeans:InvalidArgument', 'Invalid parameter value for ''%s'': %s.', argName, x);
end
b = true;
end

function b = validateReal(x, argName)
if ~(isreal(x) && isnumeric(x))
    error('simplekmeans:InvalidArgument', '''%s'' must be numeric and real.', argName);
end
b = true;
end

function b = isint(x)
b = isscalar(x) && isnumeric(x) && isreal(x) && (round(x) == x);
end

function b = dummyVal(x)
b = true;
end