#!/usr/bin/env python2
# coding: utf-8


import socket
import time

import Queue
import logging
import subprocess
import threading
from datetime import datetime, timedelta

HDFS_LOG_FILE = "/var/log/hadoop/hadoop-hadoop-namenode-{hostname}.log".format(hostname=socket.gethostname())
LOG_FILE = "/var/log/hdfs/check_gzip_error_file.log"


def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        return output

    except subprocess.CalledProcessError as e:
        if e.output != "":
            logging.error(e)

        return None


def check_gzip_health(hdfs_path):
    hdfs_command = 'hdfs dfs -text {0} > /dev/null'.format(hdfs_path)
    out = execute_command(hdfs_command)
    if out == None:
        return False
    return True

def run_task():
    thread_id = threading.current_thread().ident
    while True:
        gz_file = task_queue.get()
        print("thread id %s \t queue size %s \t prepare check gz file %s " % (thread_id, task_queue.qsize(), gz_file))
        health = check_gzip_health(gz_file)
        if health:
            print("thread id %s \t check gz file %s successfully" % (thread_id, gz_file))
        else:
            print("thread id %s \t check gz file %s failed" % (thread_id, gz_file))

if __name__ == '__main__':
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format='[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s')

    logging.info("start")

    task_queue = Queue.Queue(maxsize=10000)
    threads = []

    for _ in range(20):
        thread = threading.Thread(target=run_task)
        threads.append(thread)
        thread.start()

    while True:
        last_minute = (datetime.now() - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")
        logging.info("handle last minute %s" % (last_minute))

        with open(HDFS_LOG_FILE, 'r') as file:
            for line in file:
                if line.startswith(last_minute) and "NameNode.rename" in line:
                    f_path = line.split(" ")[-1].strip()
                    if f_path.endswith("gz") and f_path.startswith("/separated_tengine"):
                        print("put file to queue file: %s \t time: %s \t queue length %s" % (
                            last_minute, f_path, task_queue.qsize()))
                        task_queue.put(f_path)

        break

    time.sleep(60)
