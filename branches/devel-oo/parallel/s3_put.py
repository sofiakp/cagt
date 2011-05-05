"""Usage: %prog [options] FILE [FILE ...]"""

import os
import sys
import uuid
import optparse

import boto
from boto.s3.key import Key

def put_files(bucket_name, subdir, files):
    conn = boto.connect_s3()

    try:
        bucket = conn.create_bucket(bucket_name)
    except boto.exception.S3CreateError:
        bucket = conn.get_bucket(bucket_name)

    for f in files:
        key_name = str(uuid.uuid1())
        if subdir:
            key_name = subdir + '/' + key_name

        k = Key(bucket)
        k.key = key_name
        k.set_contents_from_filename(f)

if __name__ == '__main__':
    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option('-b', '--bucket', dest='bucket', metavar='BUCKET',
                      default='maxl-jlebar-chess-2011',
                      help='Put file into bucket BUCKET')
    parser.add_option('-s', '--subdir', dest='subdir', metavar='SUBDIR',
                      help='Put file into BUCKET/SUBDIR.')

    (options, args) = parser.parse_args()

    if not options.subdir:
        options.subdir = os.environ['CHESS_TESTNAME']

    put_files(options.bucket, options.subdir, args)
