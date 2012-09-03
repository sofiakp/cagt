function saveResults(outdir, params, signalFile, signal, results)
save(fullfile(outdir, 'params.mat'), 'params', 'signalFile', 'signal');
saveStructFields(fullfile(outdir, 'results.mat'), results);
end