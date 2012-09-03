function createHtmlFiles(pythonPath, outfile, results, cagtDir, title, makeRel)
if makeRel
    makeRelOpt = ' --relPath ';
else
    makeRelOpt = '';
end
numOverseg = max(results.kmeansResults.idx);
numClusters = max(results.hcResults.idx);
opts = [' --title "', title, '"', makeRelOpt, ' --numOverseg ', num2str(numOverseg), ' --numClusters ', num2str(numClusters)];
command = ['python ', pythonPath, ' ', cagtDir, opts, ' > ', outfile];
system(command);
end