#!/usr/bin/env python2
# coding: utf-8

import os
import tarfile
import time

import boto3
import socket
import logging
import shutil
from datetime import datetime

BUCKET = 'bigdata-hdfs'
AWS_ACCESS_KEY = 'oqi9zsc01d6r873vea24'
AWS_SECRET_KEY = 'trJgQa7ElbATyV1kUwlpJA3T2J67u+R4rhbKED7X'
ENDPOINT_URL = 'http://ss.bscstorage.com'
LOG_FILE = "/var/log/hdfs/namenode_metadata_backup.log"


def get_host_name():
    return socket.gethostname()


def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")


def archive_dir(src_dir_path, output_file):
    file_names = []
    for fn in os.listdir(src_dir_path):
        # need first to archive
        if fn.startswith("edits_inprogress"):
            file_names.insert(0, fn)
        else:
            file_names.append(fn)
    try:
        with tarfile.open(output_file, "w:") as tar:
            for fn in file_names:
                tar.add(os.path.join(src_dir_path, fn))
                time.sleep(1)
                logging.info("tar file %s" % (fn))
    except Exception as e:
        logging.warning(repr(e))


def upload_to_s3(key, file):
    cli = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        endpoint_url=ENDPOINT_URL
    )
    resp = cli.put_object(
        ACL='private',
        Bucket=BUCKET,
        Key=key,
        Body=open(file, 'rb')
    )
    return resp


if __name__ == "__main__":
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format='[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s')

    meta_dir_path = "/opt/hadoop/data/dfs/nn/current"
    host_name = get_host_name()
    current_date = get_current_date()
    mete_tar_file = "/data/0/%s-%s.tar" % (host_name, datetime.now().strftime("%Y%m%d%H%M"))

    logging.info("Prepare to archive dir %s to file %s" % (meta_dir_path, mete_tar_file))

    archive_dir(meta_dir_path, mete_tar_file)

    logging.info("Archive dir finish")

    key = "namenode/%s/%s_%s.tar" % (current_date, host_name, datetime.now().strftime("%Y%m%d%H%M"))
    resp = upload_to_s3(key, mete_tar_file)

    os.remove(mete_tar_file)

    logging.info("Upload file %s to s3, result: %s" % (key, resp))

# pip2 install boto3==1.5.1
# tar xvf dx-lt-yd-zhejiang-jinhua-5-10-104-5-12-2023-09-06.tar
