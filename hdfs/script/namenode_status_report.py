#!/usr/bin/env python2
# coding: utf-8


import time
import json
import socket
import logging

import requests

HDFS_VERSION = "v3.1.2"
HDFS_CLUSTER = "hdfs-jinhua"
MALLARD_URL = "http://127.0.0.1:10699/v2/push"
LOG_FILE = "/var/log/hdfs/namenode_status_report.log"


def get_namenode_state(hostname, port):
    try:
        url = "http://{hostname}:{port}/jmx?qry=Hadoop:service=NameNode,name=NameNodeStatus". \
            format(hostname=hostname, port=port)
        resp = requests.get(url)
        content = json.loads(resp.content)
        return content['beans'][0]['State']

    except Exception as e:
        logging.error("Request to %s get state error %s" % (hostname, repr(e)))


if __name__ == '__main__':
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format='[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s')

    namenodes = [
        ('dx-lt-yd-zhejiang-jinhua-5-10-104-4-41', '9870'),
        ('dx-lt-yd-zhejiang-jinhua-5-10-104-5-12', '9870'),
        ('dx-lt-yd-zhejiang-jinhua-5-10-104-7-155', '9870'),
    ]

    fields = {}
    value = 0

    for hostname, port in namenodes:
        state = get_namenode_state(hostname, port)
        if state == 'active':
            fields['active'] = hostname
            value = namenodes.index((hostname, port)) + 1
            break

    data = [{
        "name": "hdfs_namenode_active_state_report",
        "time": int(time.time()),
        "endpoint": socket.gethostname(),
        "tags": {
            "version": HDFS_VERSION,
            "cluster": HDFS_CLUSTER
        },
        "fields": fields,
        "step": 60,
        "value": value,
    }]

    resp = requests.post(MALLARD_URL, data=json.dumps(data))
    logging.info("Report to mallard, post data: %s, result: %s" % (data, resp.content))
