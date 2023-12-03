#!/usr/bin/env python2
# coding: utf-8

import time
import logging
from hdfs import InsecureClient

HDFS_USER = "root"
HDFS_HOST = "http://10.104.3.130:50070"
LOG_FILE = "/var/log/hdfs/clean_empty_dir.log"

# second
TIMEOUT = 10
SIZE_4K =  1024 * 4
SIZE_512K =  1024 * 512

HDFS_CLIENT = InsecureClient(HDFS_HOST, user=HDFS_USER, timeout=TIMEOUT)


def list_empty_dir_recursive(dir):
    try:
        files = HDFS_CLIENT.list(dir, status=True)
        if not files:
            yield dir
        for finfo in files:
            if finfo[1]["type"] == "DIRECTORY":
                for _dir in list_empty_dir_recursive(dir + finfo[0].encode('utf-8') + '/'):
                    yield _dir
    except Exception as e:
        logging.error(repr(e))


def delete_dir(dir):
    try:
        HDFS_CLIENT.delete(dir, recursive=True, skip_trash=False)
        logging.info("Delete dir %s successfully" % dir)
    except Exception as e:
        logging.info("Failed to delete file %s!!, message %s" % (dir, repr(e)))

if __name__ == '__main__':
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format='[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s')

    total_count = 0

    for dir in list_empty_dir_recursive('/'):
        total_count += 1

        delete_dir(dir)

        logging.warning("Find empty dir path %s" % (dir))

        if total_count % 1000 == 0:
            time.sleep(0.1)
            logging.warning("Process total count %s" %(total_count))

    logging.warning("Finish total count %s" % (total_count))