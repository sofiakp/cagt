function saveStructFields(outfile, inStruct)
% SAVESTRUCTFIELDS(OUTFILE, INSTRUCT)
% Saves all the fields of inStruct in outfile as separate variables.

names = fieldnames(inStruct);
for i = 1:length(names),
    name = names{i};
    if i == 1,
        eval([name, '= inStruct.(names{i});']);
        save(outfile, name);
    else
        eval([name, '= inStruct.(names{i});']);
        save(outfile, name, '-append');
    end
end
end