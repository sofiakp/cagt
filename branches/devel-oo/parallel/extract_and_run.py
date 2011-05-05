import os
import sys
import boto
from s3_put import put_files



def write_profiles_file_line(profiles_list, profile_filename, peak_filename, signal_filename, peak_file, signal_file):
  profiles_list.write(os.path.abspath(profile_filename)) # profiles file absolute path
  profiles_list.write('\t')
  profiles_list.write(peak_file[0]) # peak tag
  profiles_list.write('\t')
  profiles_list.write(signal_file[0]) # signal tag
  profiles_list.write('\t')
  profiles_list.write(signal_file[1]) # cell line
  profiles_list.write('\t')
  profiles_list.write(peak_filename) # peak_original_filename
  profiles_list.write('\t')
  profiles_list.write(signal_filename) # signal_original_filename
  profiles_list.write('\t')
  profiles_list.write(signal_file[2]) # ylims
  profiles_list.write('\t')
  profiles_list.write(peak_file[2]) # flip?
  profiles_list.write('\t')
  profiles_list.write(signal_file[4]) # num_bases_per_value
  profiles_list.write('\t')
  profiles_list.write(signal_file[3]) # low_signal_cutoff_value
  profiles_list.write('\n')


def main(signal_files_filename, peak_files_filename, run_id):
  aws_bucket = 'maxl-cagt'
  bucket_subdir = 'cagt_run_1/'
  
  signal_files = map(lambda l: l.split(), open(signal_files_filename, 'r').readlines())
  peak_files = map(lambda l: l.split(), open(peak_files_filename, 'r').readlines())
  
  signal_files_loc = 'ftp:/something'
  peak_files_loc = 'ftp:/something'
  
	profiles_list_filename = 'profiles_list.txt'
	profiles_list = open(profiles_list_filename, 'w')
  
  for peak_file in peak_files:
    peak_filename = peak_file[3]
    peak_url = signal_files_loc+peak_filename
    os.system('wget %s' % peak_url)

  for signal_file in signal_files:
    signal_filename = signal_file[6]
    signal_url = signal_files_loc+signal_filename
    os.system('wget %s' % signal_url)
	  for peak_file in peak_files:
	    if signal_file[1] != peak_file[1]: continue # skip if cell lines not equal
	    
	    peak_filename = peak_file[3]
	    profile_name = "%s_around_%s" % (signal_filename, peak_filename)
	    profile_filename = "%s.cagt" % profile_name
  	  os.system('/root/extractsignal/bin/extractSignal -t=%s -i=%s -if=narrowpeak -tf=mat -o=%s -of=cagt'\
  	  % (signal_filename, peak_filename, profile_filename))
  	  
  	  write_profiles_file_line(profiles_list, profile_filename, peak_filename, signal_filename, peak_file, signal_file)
  	
  path_to_cagt = 'cagt.py'
  output_folder = 'cagt_output_%s' % run_id
  os.system('python %s --cluster --make-plots %s' % (path_to_cagt, profiles_list_filename))
  
  os.system('zip -r %s.zip %s' % (output_folder, output_folder))
  
  s3_put(aws_bucket, bucket_subdir, ['%s.zip' % output_folder])
  
  
  
  
  
if __name__ == "__main__":
  signal_files_filename = sys.argv[1]
  peak_files_filename = sys.argv[2]
  run_id = sys.argv[3]
  
  main(signal_files_filename, peak_files_filename, run_id)
  