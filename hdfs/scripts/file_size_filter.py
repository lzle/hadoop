#!/usr/bin/env python2
# coding: utf-8

import time
import logging
from hdfs import InsecureClient

HDFS_USER = "root"
HDFS_HOST = "http://10.104.7.25:9870"
LOG_FILE = "/var/log/hdfs/file_state_filter.log"

# second
TIMEOUT = 10
SIZE_4K =  1024 * 4
SIZE_512K =  1024 * 512

HDFS_CLIENT = InsecureClient(HDFS_HOST, user=HDFS_USER, timeout=TIMEOUT)


def list_files_recursive(dir):
    try:
        files = HDFS_CLIENT.list(dir, status=True)
        for finfo in files:
            if finfo[1]["type"] == "DIRECTORY":
                for fitem in list_files_recursive(dir + finfo[0].encode('utf-8') + '/'):
                    yield fitem
            else:
                yield (dir, finfo)
    except Exception as e:
        logging.error(repr(e))


if __name__ == '__main__':
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format='[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s')

    total_count = 0
    small_count_512 = 0
    small_count_4 = 0

    for fitem in list_files_recursive('/'):
        total_count += 1
        dir, finfo = fitem[0], fitem[1]

        file_length = finfo[1]['length']
        if file_length < SIZE_512K:
            path = dir + '/' + finfo[0].encode('utf-8')
            logging.warning("Find small file path %s length %s" % (path, file_length))
            small_count_512 += 1
            if file_length < SIZE_4K:
                small_count_4 += 1

        if total_count % 1000 == 0:
            time.sleep(0.1)
            logging.warning("Process total count %s, small 512K count %s, small 4K count %s, percent %s" %
                            (total_count, small_count_512, small_count_4, float(small_count_512)/total_count*100))

    logging.warning("Finish total count %s, small 512K count %s, small 4K count %s, percent %s" %
                    (total_count, small_count_512, small_count_4, float(small_count_512) / total_count * 100))