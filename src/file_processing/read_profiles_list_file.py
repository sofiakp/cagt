
from src.ProfilesInfo.ProfilesInfo import *

def read_profiles_list_file(filename, output_id, args):
	f = open(filename,"r")
	profiles = []
	for line in f:
		profiles.append(ProfileInfo(line, output_id, args))
		# line = line.split()
		# entry = {}
		# entry["filename"] = line[0]
		# entry["peak_tag"] = line[1]
		# entry["signal_tag"] = line[2]
		# entry["cell_line"] = line[3]
		# entry["peak_filename"] = line[4]
		# entry["signal_filename"] = line[5]
		# entry["ylims"] = map(float, line[6].split(','))
		# entry["flip"] = line[7]
		# entry["bin_size"] = line[8]
		# profiles.append(entry)
	return profiles

