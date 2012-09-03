function X = shiftMat(Xin, lags)
% X = SHIFTMAT(XIN, LAGS) Shifts the i-th row of XIN by LAGS(i).
% 
% Author: sofiakp

X = ones(size(Xin)) * NaN;
for i = 1:size(X, 1)
    if lags(i) >= 0
        X(i, 1:end - lags(i)) = Xin(i, 1 + lags(i):end);
    else
        X(i, 1 - lags(i):end) = Xin(i, 1:end + lags(i));
    end
end
end