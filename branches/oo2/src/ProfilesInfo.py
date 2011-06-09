import os

class ProfileInfo:
    def __init__(self, profile_info_str, output_folder, args):
        self.output_folder = output_folder
        self.args = args
        self.from_str(profile_info_str)

    def from_str(self, str):
        entries = str.split()
        self.filename = entries[0]
        self.peak_tag = entries[1]
        self.signal_tag = entries[2]
        self.cell_line = entries[3]
        self.peak_filename = os.path.basename(entries[4])
        self.signal_filename = os.path.basename(entries[5])
        self.ylims = map(float, entries[6].split(','))
        assert(len(self.ylims)==2)
        if entries[7] in ["True","true","T","t","1","y","Y","yes","Yes"]:
          self.flip = True
        else:
          self.flip = False
        self.bin_size = int(entries[8])
        self.low_signal_cutoff_value = float(entries[9])

    def __str__(self):
        return self.signal_tag + " around " + self.peak_tag + " in " + self.cell_line

    def handle(self):
        return "%s_around_%s" % (self.signal_filename, self_peak_filename)


class ProfileInfoPair:
    def __init__(self, clustering_info1, clustering_info2, entropy1, entropy2, mutual_entropy, mutual_information, args):
        self.args = args
        self.clustering_info1 = clustering_info1
        self.clusteirng_info2 = clustering_info2
        self.profiles_info1 = clustering_info1.profiles_info
        self.profiles_info2 = clustering_info2.profiles_info
        assert(profiles_info1.output_folder == profiles_info2.output_folder)
        self.output_folder = profiles_info1.output_folder
        assert(profiles_info1.cell_line == profiles_info2.cell_line)
        self.cell_line = profiles_info1.cell_line
        assert(profiles_info1.peak_tag == profiles_info2.peak_tag)
        self.peak_tag = profiles_info1.peak_tag
        assert(profiles_info1.bin_size == profiles_info2.bin_size)
        self.bin_size = profiles_info1.bin_size
        self.entropy1, self.entropy2, self.mutual_entropy, self.mutual_information =\
        entropy1, entropy2, mutual_entropy, mutual_information



