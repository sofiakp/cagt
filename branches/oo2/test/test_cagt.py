#!/bin/env python
""" Runs a test of CAGT """
import sys
import os
import uuid
_folder_path = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(_folder_path)
sys.path.append(os.path.join('..', _folder_path))
try:
    import argparse
except ImportError:
    import src.argparse as argparse

import make_test_profiles

def main():
    parser = argparse.ArgumentParser(description='Runs a test of CAGT')
    parser.add_argument('output_dir', type=str, action='store', default=None, help='Location of CAGT\'s output directory')
    parser.add_argument('-r', action='store_true', help='Don\'t regenerate test profiles')
    parser.add_argument('--num_files', type=int, action='store', default=1, help='Number of CAGT files to make')
    parser.add_argument('--num_clusters', type=int, action='store', default=5, help='Number of clusters profiles are divided into')
    parser.add_argument('--num_per_cluster', type=int, action='store', default=100, help='Number of profiles per cluster')
    parser.add_argument('--profile_length', type=int, action='store', default=100, help='Length of each profile')
    args = parser.parse_args()

    test_uuid = uuid.uuid1()

    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)

    if args.r:
        filenames = os.listdir(args.output_dir)
        filenames = [os.path.join(args.output_dir, filename) for filename in filenames]
        profiles_list_filenames = filter(lambda s: 'profiles_list' in s, filenames)
        assert(len(profiles_list_filenames) > 0)
        profiles_list_filename = profiles_list_filenames[0]
        print 'using profiles_list_filename: %s' % profiles_list_filename
    if not (args.r):
        print "Generating test profiles..."
        profiles_list_filename = os.path.join(args.output_dir, 'profiles_list_%s.txt' % test_uuid)
        test_data_prefix = os.path.join(args.output_dir, 'test_data%s' % test_uuid)
        args.profiles_list_filename = profiles_list_filename
        args.cagt_filename_prefix = test_data_prefix
        make_test_profiles.main(args)

    print "Running CAGT..."
    cagt_path = os.path.join(_folder_path, '../cagt.py')
    os.system("python %s %s %s --cluster --make-plots --make-html --debug" % (cagt_path, args.output_dir, profiles_list_filename))


if __name__ == '__main__':
    main()
