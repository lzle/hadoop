# HDFS 常用命令


### 1、daemon

NameNode 启动/停止
```shell
hdfs --daemon start namenode
hdfs --daemon stop namenode
```

DataNode 启动/停止
```shell
hdfs --daemon start datanode
hdfs --daemon stop datanode
```

### 2、dfsadmin

汇报集群状态
```shell
hdfs dfsadmin -report -live
hdfs dfsadmin -report -dead
```

### 3、dfs

创建目录
```shell
hdfs dfs -mkdir -p /lzl/test
```

从本地上次文件

```shell
hdfs dfs -put a.txt /lzl/test
```

从本地上传目录
```shell
hdfs dfs -copyFromLocal localdir /lzl/test

# 两者效果不一样
hdfs dfs -copyFromLocal localdir/* /lzl/test
```

上传本地目录并删除
```shell
hdfs dfs -moveFromLocal localdir /lzl/test
```

查看文件

```shell
hdfs dfs -cat /lzl/test/a.txt
```

下载文件
```shell
hdfs dfs -get /lzl/test/b.txt ./
```

下载目录
```shell
# 本地有 test 目录
hdfs dfs -copyToLocal /lzl/test ./
```

删除文件/目录
```shell
# -r 递归删除子目录
hdfs dfs -rm -r /lzl/test
```

### 4、haadmin

查看节点状态
```
hdfs haadmin -getServiceState nn1
```

将 nn1 切换为 Standby 备用节点
```
hdfs haadmin -transitionToStandby --forcemanual nn1
```


 sudo -u flume hdfs debug recoverLease -path  /fucheng.wang/crudeoil.hexun.com_202211220000.3.24.k7_haidene.1669046460213.gz -retries 10
 
