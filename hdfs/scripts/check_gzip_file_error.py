#!/usr/bin/env python2
# coding: utf-8

import time
import logging
from hdfs import InsecureClient
import subprocess
import threading
import Queue

HDFS_USER = "root"
HDFS_HOST = "http://10.111.20.33:9870"
LOG_FILE = "/var/log/hdfs/check_gzip_file_error.log"

# second
TIMEOUT = 10
SIZE_4K = 1024 * 4
SIZE_512K = 1024 * 512

HDFS_CLIENT = InsecureClient(HDFS_HOST, user=HDFS_USER, timeout=TIMEOUT)


def list_files_recursive(dir):
    print(dir)
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


def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        return output

    except subprocess.CalledProcessError as e:
        if e.output != "":
            logging.error(e)

        return None


def get_error_file(hdfs_path):
    hdfs_command = 'hdfs dfs -text {0} > /dev/null'.format(hdfs_path)
    out = execute_command(hdfs_command)
    if out == None:
        logging.warning(hdfs_path)
        logging.warning('Unexpected end of ZLIB input stream')


def run_task():
    while True:
        path = result_queue.get()
        print(path)
        get_error_file(path)


if __name__ == '__main__':
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format='[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s')

    result_queue = Queue.Queue(maxsize=1000)

    threads = []
    for i in range(100):
        thread = threading.Thread(target=run_task)
        threads.append(thread)
        thread.start()

    count = 0
    for fitem in list_files_recursive('/separated_tengine/v9.tiktokcdn.com'):
        dir, finfo = fitem[0], fitem[1]
        path = dir + '/' + finfo[0].encode('utf-8')
        print(count)
        if path.startswith("/separated_tengine/v9.tiktokcdn.com/2024020106"):
            print(path)
            result_queue.put(path)
        count += 1

    while not result_queue.empty():
        time.sleep(1)

    print(result_queue.empty())
    time.sleep(30)
