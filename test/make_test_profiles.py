#!/bin/env python
""" Generate profiles for testing CAGT  """
import sys
import os
import argparse
import numpy as np
import scipy.stats as spstats
import random
_folder_path = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(_folder_path)

def generate_profiles(num_clusters, num_per_cluster, profile_length=100,
                      mode_val=40, spread_stdev_fraction=.03, noise_stdev_fraction=.1, **_):
    """Generates num_clusters profiles with num_per_cluster profiles each.
    Profiles are (usually) more similar within clusters than between them.

    Each cluster consists of profiles with a peak at a position chosen uniformly
    from [0,profile_length-1], with a Gaussian shape, mode at mode_val, and stdev
    profile_length*spread_stdev_fraction.  In addition to the Gaussian shape, each
    point has noise added to it with value Normal(0, (mode_val*noise_stdev_fraction)^2)"""
    spread_stdev = spread_stdev_fraction * profile_length
    noise_stdev = mode_val * noise_stdev_fraction
    val_scale = mode_val / spstats.norm(0, spread_stdev).pdf(0)
    profiles = []
    centers = []
    for c in range(num_clusters):
        cluster_center = random.randrange(profile_length)
        centers.append(cluster_center)
        for p in range(num_per_cluster):
            profile = np.zeros(profile_length)
            for i in range(profile_length):
                val = spstats.norm(cluster_center, spread_stdev).pdf(i)
                val *= val_scale
                noise = random.normalvariate(0, noise_stdev)
                val += noise
                val = max(val, 0)
                profile[i] = val
            # flip some profiles
            if random.randrange(2) == 0:
                profile = profile[::-1]
            profiles.append(profile)
    return profiles, centers


def write_cagt_file(profiles, filename):
    """Writes a set of profiles to a CAGT file"""
    f = open(filename, 'w')
    for profile in profiles:
        f.write('chrname\t')
        pos = random.randrange(1000000)
        f.write('%i\t' % pos)
        f.write('%i\t' % (pos+1))
        for i in range(len(profile)):
            f.write('%s' % profile[i])
            if i != len(profile)-1:
                f.write(',')
        f.write('\n')
    f.close()
    return

def write_profiles_list_file(profile_filenames, filename):
    """Writes a profiles list file"""
    f = open(filename, 'w')
    for profile_filename in profile_filenames:
        f.write('%s\t' % os.path.abspath(profile_filename))
        f.write('TestPeak\tTestSignal\tTestCellLine\ttest_peaks.bed\ttest_sig.begraph\t0,50\tTrue\t10\t1\n')
    f.close()
    return


def main(args):

    cagt_filenames = ['%s%s.cagt' % (args.cagt_filename_prefix, i)
                     for i in range(args.num_files)]


    for i in range(len(cagt_filenames)):
        profiles, centers = generate_profiles(**vars(args))
        print "file %s cluster centers: %s" % (i, centers)
        write_cagt_file(profiles, cagt_filenames[i])

    write_profiles_list_file(cagt_filenames, args.profiles_list_filename)
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('cagt_filename_prefix', type=str, action='store', help='Output location of cagt file')
    parser.add_argument('profiles_list_filename', type=str, action='store', help='Output location of profiles list file')
    parser.add_argument('--num_files', type=int, action='store', default=1, help='Number of CAGT files to make')
    parser.add_argument('--num_clusters', type=int, action='store', default=5, help='Number of clusters profiles are divided into')
    parser.add_argument('--num_per_cluster', type=int, action='store', default=100, help='Number of profiles per cluster')
    parser.add_argument('--profile_length', type=int, action='store', default=100, help='Length of each profile')
    args = parser.parse_args()
    main(args)










