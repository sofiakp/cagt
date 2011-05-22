#!/bin/bash

# batchCagt.sh [pairFile] [cagtDir] [oDir] [combProfileList]
# profiles_file FORMAT (tab delimited)
#  profiles_file_absolute_path
#  peak_tag
#  signal_tag
#  cell_line
#  peak_original_filename
#  signal_original_filename
#  ylim_lower,ylim_upper 0,60
#  allow_profile_flipping? True/False
#  number_of_bases_per_value 10
#  low_signal_cutoff_value 3

if [[ "$#" -lt 3 ]]
    then
    echo $(basename $0) 1>&2
    echo "Run cagt in batch on multiple pairs of peak files and signal files" 1>&2
    echo "USAGE:" 1>&2
    echo "$(basename $0) [pairFile] [cagtDir] [oDir]" 1>&2
    echo " [pairFile]: Col1/2: prefix for peakFile/signalFile Col3/4:Cell-lines Col5/6:Target Col7/8:Lab Col9/10:Treatment Col11/12:Protocol" 1>&2
    echo " [cagtDir]: Parent directory containing cagt (gz) files in subdirectories named after peakFilePrefix, cagt files are named peakPrefix_AT_signalPrefix.cagt.gz" 1>&2
    echo " [oDir]: Output directory for cagt output" 1>&2
    echo " [combProfileList]: OPTIONAL: Output file for combined profile list parameters" 1>&2
    exit 1 
fi

PAIRFILE=$1
if [[ ! -e ${PAIRFILE} ]]; then echo "PairFile: ${PAIRFILE} does not exist" 1>&2 ; exit 1 ; fi

CAGTDIR=$2
if [[ ! -d ${CAGTDIR} ]]; then echo "CAGT directory: ${CAGTDIR} does not exist" 1>&2 ; exit 1 ; fi

ODIR=$3
[[ ! -d ${ODIR} ]] && mkdir ${ODIR}

COMBLIST='NA'
[[ $# -gt 3 ]] && COMBLIST=$4
[[ -e ${COMBLIST} ]] && mv ${COMBLIST} "${COMBLIST}.old"
if [[ ! -d $(dirname ${COMBLIST}) ]]
    then
    echo "Directory for combined profile parameter list ${COMBLIST} does not exist" 1>&2
    exit 1
fi

JOBGROUP="/cagt_${RANDOM}"

CAGTPATH=$(which cagt.py)
if [[ ! -e ${CAGTPATH} ]]; then echo 'cagt.py needs to be in $PATH' 1>&2 ; exit 1 ; fi

while read i
  do
  peakPrefix=$(echo $i | awk '{print $1}')
  sigPrefix=$(echo $i | awk '{print $2}')
  peakTag=$(echo $i | awk '{print $5}')
  signalTag=$(echo $i | awk '{print $6}')
  cellLine=$(echo $i | awk '{print $3}')
  cagtFile="${CAGTDIR}/${peakPrefix}/${peakPrefix}_AT_${sigPrefix}.cagt.gz"

  # Check if cagtFile exists
  if [[ ! -e ${cagtFile} ]]
      then
      printf "Missing cagt file: [%s]\t[%s]\n" ${peakPrefix} ${sigPrefix} 1>&2
      continue;
  fi
  
  # Check if output directory exists
  [[ -d "${ODIR}/${sigPrefix}_around_${peakPrefix}" ]] && continue

  # Set parameters based on signalTag
  numBases='10'
  lowSigCutoff='4'
  ylim='0,60'
  flipFlag='True'
  mergeCorr='0.75'
  npass='10'
  # For nucleosome data
  if [[ ${signalTag} == 'NUCLEOSOME' ]]
      then
      ylim='0,10'
      lowSigCutoff='0.05'
      mergeCorr='0.6'
  fi
  
  # For TSS data
  if [[ ${peakTag} == 'TSS' ]]
      then
      flipFlag='False'
  fi

  # For DNase data
  if [[ ${signalTag} == 'DNASE' ]]
      then 
      lowSigCutoff='2'
      mergeCorr='0.8'
  fi

  # For FAIRE data
  if [[ ${signalTag} == 'DNASE' ]]
      then 
      lowSigCutoff='2'
      ylim='0,30'
  fi

  # For TF signal around TFs
  if [[ ${peakPrefix} == ${sigPrefix} ]]
      then
      lowSigCutoff='2'
  fi

  RANDSUFFIX="${RANDOM}_${RANDOM}"
  TMPDIR="${TMP}/cagt_${RANDSUFFIX}"
  PRFILE="${TMPDIR}/profile_${RANDSUFFIX}.tab"
  TMPCAGTFILE="${TMPDIR}/cagtFile_${RANDSUFFIX}.cagt"
  [[ ! -d ${TMPDIR} ]] && mkdir ${TMPDIR}

  # Write profiles_file
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" ${TMPCAGTFILE} ${peakTag} ${signalTag} ${cellLine} ${peakPrefix} ${sigPrefix} ${ylim} ${flipFlag} ${numBases} ${lowSigCutoff} > "${PRFILE}"

  if [[ ${COMBLIST} != 'NA' ]]
      then
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" ${cagtFile} ${peakTag} ${signalTag} ${cellLine} ${peakPrefix} ${sigPrefix} ${ylim} ${flipFlag} ${numBases} ${lowSigCutoff} >> "${COMBLIST}"
  fi

  # Write submit script
  submitScript="cagt_${RANDOM}.sh"
  echo '#!/bin/bash' > ${submitScript}
  echo "zcat ${cagtFile} | sed -r 's/NaN/0.0/g' > ${TMPCAGTFILE}" >> ${submitScript}
  echo "python ${CAGTPATH} --cluster --make-plots --low_signal_cutoff_quantile 0.99 --group_by_quantile 0.99 --group_quantile_lower_bound 0.1 --group_quantile_upper_bound 0.9 --num_groups 4 --cluster_merge_correlation_cutoff ${mergeCorr} --npass ${npass} ${ODIR} ${PRFILE}" >> ${submitScript}
  # --cluster_then_merge_num_clusters 10
  echo "rm -rf ${TMPDIR}" >> ${submitScript}
  chmod 755 ${submitScript}

  # Submit script
  logDir="${ODIR}/logFiles"
  [[ ! -d ${logDir} ]] && mkdir ${logDir}
  outFile="${logDir}/${peakPrefix}_AT_${sigPrefix}.out"
  errFile="${logDir}/${peakPrefix}_AT_${sigPrefix}.err"

  bsub -J "${peakPrefix}_AT_${sigPrefix}" -g "${JOBGROUP}" -W 24:00 -o "${outFile}" -e "${errFile}" < ${submitScript}
  rm ${submitScript}
  sleep 1s

done < "${PAIRFILE}"