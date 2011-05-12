
import sys
sys.path.append("../../")

from src.filenames import *

def read_assignments(cluster_type, peak_tag, signal_tag):
	filename = make_assignments_filename(peak_tag, signal_tag, output_id)
	return map(int,open(filename, "r").read().split())
