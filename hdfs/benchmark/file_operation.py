#!/usr/bin/env python3
# coding: utf-8
import random
import socket
import threading
import time

from hdfs import InsecureClient

# HDFS连接配置
hdfs_host = 'http://10.104.4.41:9870'
hdfs_user = 'hadoop'

# 文件路径和内容
file_dir = '/stress/file'
file_content = b'A' * 4096

# 获取系统主机名
hostname = socket.gethostname()


def put_file():
    # 获取当前线程ID
    thread_id = threading.current_thread().ident
    client = InsecureClient(hdfs_host, user=hdfs_user)
    count = 0
    current_time = time.time()
    while True:
        try:
            count += 1
            file_path = '%s/%s/%s/%s-%s' % (file_dir, hostname, thread_id, current_time, count)
            with client.write(file_path) as writer:
                writer.write(file_content)
            print(file_path)
        except Exception as e:
            print('error')


def put_and_get():
    # 获取当前线程ID
    thread_id = threading.current_thread().ident
    client = InsecureClient(hdfs_host, user=hdfs_user)
    count = 0
    current_time = time.time()
    while True:
        try:
            count += 1
            file_path = '%s/%s/%s/%s-%s' % (file_dir, hostname, thread_id, current_time, count)
            with client.write(file_path) as writer:
                writer.write(file_content)
            print('write', file_path)
            with client.read(file_path) as f:  # read方法返回的是上下文管理器对象，所以要使用with调用
                content = f.data.decode('utf-8')
            print('read', len(content))
        except Exception as e:
            print(e)


def get_file():
    # 获取当前线程ID
    client = InsecureClient(hdfs_host, user=hdfs_user)

    def list_files(root):
        file_list = client.list(root)
        random.shuffle(file_list)
        for file_name in file_list:
            file_path = root + '/' + file_name
            if client.status(file_path, strict=False)['type'] == 'DIRECTORY':
                for file_path in list_files(file_path):
                    yield file_path
            else:
                yield file_path

    while True:
        try:
            for file_path in list_files(file_dir + '/' + hostname):
                print(file_path)
                with client.read(file_path) as f:  # read方法返回的是上下文管理器对象，所以要使用with调用
                    content = f.data.decode('utf-8')
                print('read', len(content))

        except Exception as e:
            print(e)


def delete_file():
    # 获取当前线程ID
    client = InsecureClient(hdfs_host, user=hdfs_user)

    def list_files(root):
        file_list = client.list(root)
        random.shuffle(file_list)
        for file_name in file_list:
            file_path = root + '/' + file_name
            if client.status(file_path, strict=False)['type'] == 'DIRECTORY':
                for file_path in list_files(file_path):
                    yield file_path
            else:
                yield file_path

    while True:
        try:
            for file_path in list_files(file_dir + '/' + hostname):
                client.delete(file_path, skip_trash=True)
                print(file_path)

        except Exception as e:
            print(e)


if __name__ == '__main__':
    for i in range(10):
        th = threading.Thread(target=delete_file)
        th.start()


# pip install requests==2.26.0
# pip install hdfs