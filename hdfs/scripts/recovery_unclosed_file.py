#!/usr/bin/env python2
# coding: utf-8


import subprocess
import socket
import logging
import time

from hdfs import InsecureClient

HDFS_USER = "hadoop"
HDFS_HOST = "http://10.104.4.41:9870"

# second
TIMEOUT = 1
HDFS_CLIENT = InsecureClient(HDFS_HOST, user=HDFS_USER, timeout=TIMEOUT)
LOG_FILE = "/var/log/hdfs/recovery_unclosed_file.log"


def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        return output

    except subprocess.CalledProcessError as e:
        if e.output != "":
            logging.error(e)

        return None


def get_unclosed_files(hdfs_path):
    hdfs_command = 'hdfs fsck -fs hdfs://dx-lt-yd-zhejiang-jinhua-5-10-104-4-41:8020/ {0}' \
                   '  -openforwrite | grep OPENFORWRITE'.format(hdfs_path)

    file_list = []
    out = execute_command(hdfs_command)
    if out is None:
        return file_list

    for line in out.split("OPENFORWRITE"):
        for fields in line.split(" "):
            if "/" in fields and not fields.endswith("tmp") and fields.endswith('gz'):
                file_list.append(fields)
                continue

    logging.info("OPENFORWRITE file list {0} length {1}".format(hdfs_path, len(file_list)))
    return file_list


def recover_file(hdfs_path):
    logging.info("recover file %s" % (hdfs_path))
    hdfs_command = 'sudo -u hadoop /opt/hadoop/bin/hdfs debug recoverLease -path {0} -retries 10'.format(hdfs_path)
    out = execute_command(hdfs_command)
    logging.info("%s" % out)


def main():
    while True:
        logging.info('start recovery')
        for _dir in ['/separated_ict/', '/separated_tengine/']:
            files = HDFS_CLIENT.list(_dir, status=True)
            for finfo in files:
                if finfo[1]["type"] == "DIRECTORY":
                    sub_dir = _dir + finfo[0].encode('utf-8') + '/'
                    unclose_files = get_unclosed_files(sub_dir)
                    for ufile in unclose_files:
                        logging.info("get unclose file %s" % (ufile))
                        recover_file(ufile)
                        time.sleep(0.2)
                time.sleep(1)
        logging.info('finish recovery')
        time.sleep(60 * 5)


if __name__ == "__main__":
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format='[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s')

    main()
