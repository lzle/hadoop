#!/usr/bin/env python3
# coding: utf-8
import json
import time
import random
import socket
import logging

import requests
from hdfs import InsecureClient

HDFS_USER = "root"
HDFS_VERSION = "v3.1.2"
HDFS_CLUSTER = "hdfs-shijiazhuang"
HDFS_HOST = "http://10.103.1.34:9870"
MALLARD_URL = "http://127.0.0.1:10699/v2/push"
LOG_FILE = "/var/log/hdfs/service_available_report.log"
UPLOAD_DIR = "/tmp/.service_available_monitor"
HOSTNAME = socket.gethostname()

# 1M
FILE_CONTENT = b"A" * 1024 * 1024
# second
TIMEOUT = 1
HDFS_CLIENT = InsecureClient(HDFS_HOST, user=HDFS_USER, timeout=TIMEOUT)


def cost_time(func):
    def inner():
        start = time.time()
        code = func()
        cost = int((time.time() - start) * 1000)
        return code, cost

    return inner


@cost_time
def put_file():
    try:
        with HDFS_CLIENT.write(UPLOAD_FILE_NAME, overwrite=True) as writer:
            writer.write(FILE_CONTENT)
        logging.info("Put file %s successfully" % UPLOAD_FILE_NAME)
        return 200
    except Exception as e:
        logging.info("Failed to put file %s!!, message %s" % (UPLOAD_FILE_NAME, repr(e)))
    return 500


@cost_time
def get_file():
    try:
        with HDFS_CLIENT.read(UPLOAD_FILE_NAME) as reader:
            content = reader.data.decode('utf-8')
        assert (content == FILE_CONTENT)
        logging.info("Get file %s successfully" % UPLOAD_FILE_NAME)
        return 200
    except Exception as e:
        logging.info("Failed to get file %s!!, message %s" % (UPLOAD_FILE_NAME, repr(e)))
    return 500


@cost_time
def delete_file():
    try:
        HDFS_CLIENT.delete(UPLOAD_FILE_NAME, skip_trash=True)
        logging.info("Delete file %s successfully" % UPLOAD_FILE_NAME)
        return 200
    except Exception as e:
        logging.info("Failed to delete file %s!!, message %s" % (UPLOAD_FILE_NAME, repr(e)))
    return 500


def report():
    TIMESTAMP = int(time.time())
    global UPLOAD_FILE_NAME
    UPLOAD_FILE_NAME = "%s/%s_%s.file" % (UPLOAD_DIR, HOSTNAME, TIMESTAMP)

    put_code, put_cost = put_file()
    get_code, get_cost = get_file()
    delete_code, delete_cost = delete_file()

    if put_code & get_code & delete_code != 200:
        rest_code = 500
    else:
        rest_code = 200

    data = [{
        "name": "hdfs_service_availability_report",
        "time": TIMESTAMP,
        "endpoint": HOSTNAME,
        "tags": {
            "version": HDFS_VERSION,
            "cluster": HDFS_CLUSTER
        },
        "fields": {
            "put": put_code,
            "put_cost": put_cost,
            "get": get_code,
            "get_cost": get_cost,
            "delete": delete_code,
            "delete_cost": delete_cost
        },
        "step": 20,
        "value": rest_code
    }]

    resp = requests.post(MALLARD_URL, data=json.dumps(data))
    logging.info("Report to mallard, post data: %s, result: %s" % (data, resp.content))


if __name__ == '__main__':
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format='[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s')

    logging.info("Start to execute ...")

    # random sleep 0-15s to prevent stabbing access
    time.sleep(random.uniform(0, 15))

    # first
    start = time.time()
    report()
    cost = time.time() - start

    # second
    if cost < 20:
        time.sleep(20 - cost)
        report()
        cost = time.time() - start

    # third
    if cost < 40:
        time.sleep(40 - cost)
        report()

    logging.info("Complete")
