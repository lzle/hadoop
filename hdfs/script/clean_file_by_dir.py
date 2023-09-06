#!/usr/bin/env python2
# coding: utf-8

import time
import logging
from hdfs import InsecureClient

HDFS_USER = "root"
HDFS_HOST = "http://10.104.3.130:50070"
LOG_FILE = "/var/log/hdfs/clean_file.log"

# second
TIMEOUT = 10
SIZE_4K =  1024 * 4
SIZE_512K =  1024 * 512

HDFS_CLIENT = InsecureClient(HDFS_HOST, user=HDFS_USER, timeout=TIMEOUT)


def list_dir_recursive(dir):
    try:
        files = HDFS_CLIENT.list(dir, status=True)
        for finfo in files:
            if finfo[1]["type"] == "DIRECTORY":
                for file in list_dir_recursive(dir + finfo[0].encode('utf-8') + '/'):
                    yield file
            else:
                yield dir + finfo[0].encode('utf-8')
    except Exception as e:
        logging.error(repr(e))


def delete_file(file):
    try:
        HDFS_CLIENT.delete(file, skip_trash=True)
        logging.info("Delete file %s successfully" % file)
    except Exception as e:
        logging.info("Failed to delete file %s!!, message %s" % (file, repr(e)))

if __name__ == '__main__':
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format='[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s')

    total_count = 0

    for file in list_dir_recursive("/user/root/.Trash/230725140001/"):

        total_count += 1

        delete_file(file)

        logging.warning("Find file path %s" % (file))

        if total_count % 1000 == 0:
            time.sleep(1)
            logging.warning("Process total count %s" %(total_count))

    logging.warning("Finish total count %s" % (total_count))