#!/usr/bin/env python2
# coding: utf-8


import subprocess
import socket
import logging
import time
import json
import requests

HDFS_VERSION = "v3.1.2"
HDFS_CLUSTER = "hdfs-shijiazhuang"
MALLARD_URL = "http://127.0.0.1:10699/v2/push"
LOG_FILE = "/var/log/hdfs/max_directory_items_report.log"


def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        return output

    except subprocess.CalledProcessError as e:
        if e.output != "":
            logging.error(e)

        return None


def get_dir_max_items(max_items, dir):
    logging.info("Get dir max items %s" % (dir))
    try:
        hdfs_command = 'sudo -u hadoop /opt/hadoop/bin/hdfs dfs -count %s/\*' % (dir)
        data = execute_command(hdfs_command)

        for line in data.strip().split('\n'):
            dir_count, file_count, content_size, pathname = line.split()
            if int(dir_count) <= 1:
                if int(file_count) > max_items:
                    max_items = int(file_count)
                    logging.info("Got max items %s, filepath %s" % (max_items, pathname))
            elif int(file_count) > max_items and int(file_count) > 100000:
                max_items = get_dir_max_items(max_items, pathname)
                time.sleep(1)
    except Exception as e:
        pass
    return max_items


if __name__ == "__main__":
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format='[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s')

    fields = {}
    check_dirs = ['/audit', '/data', '/separated', '/separated_ict', '/separated_tengine', '/user', '/separated_spark',
                  '/separated_spark_tmp']
    for dir in check_dirs:
        fields[dir[1:]] = get_dir_max_items(0, dir)
        time.sleep(30)

    data = [{
        "name": "hdfs_namenode_max_directory_items_report",
        "time": int(time.time()),
        "endpoint": socket.gethostname(),
        "tags": {
            "version": HDFS_VERSION,
            "cluster": HDFS_CLUSTER
        },
        "fields": fields,
        "step": 60,
        "value": max(fields.values()),
    }]

    resp = requests.post(MALLARD_URL, data=json.dumps(data))
    logging.info("Report to mallard, post data: %s, result: %s" % (data, resp.content))

# dfs.namenode.fs-limits.max-directory-items
