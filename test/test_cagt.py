#!/bin/env python
""" Runs a test of CAGT """
import sys
import os
import argparse
import uuid
_folder_path = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(_folder_path)

def main():
    parser = argparse.ArgumentParser(description='Runs a test of CAGT')
    parser.add_argument('output_dir', type=str, action='store', default=None, help='Location of CAGT\'s output directory')
    args = parser.parse_args()

    test_uuid = uuid.uuid1()

    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)

    print "Generating test profiles..."
    make_test_profiles_path = os.path.join(_folder_path, 'make_test_profiles.py')
    profiles_list_path = os.path.join(args.output_dir, 'profiles_list_%s.txt' % test_uuid)
    test_data_prefix = os.path.join(args.output_dir, 'test_data%s' % test_uuid)
    os.system("python %s %s %s"
              % (make_test_profiles_path, test_data_prefix, profiles_list_path))

    print "Running CAGT..."
    cagt_path = os.path.join(_folder_path, '../cagt.py')
    os.system("python %s %s %s --cluster --make-plots --make-html" % (cagt_path, args.output_dir, profiles_list_path))


if __name__ == '__main__':
    main()
