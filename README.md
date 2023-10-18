# hadoop

## 常用命令

### 日志分析

1、NameNode 节点查看 Block 分配 DataNode 节点是否平衡

```
# 喜鹊
$ grep allocate hadoop-cmf-hdfs-NAMENODE-`hostname`.log.out.1 | \
  awk -F "replicas=" '{print $2}' | \
  awk -F 'for' '{print $1}' | \
  awk -F ',' '{print $1,$2,$3}' | \
  awk -F" " '{for(i=1;i<=NF;i++) print $i}'

# 新金华
$ grep allocate  hadoop-hadoop-namenode-dx-lt-yd-zhejiang-jinhua-5-10-104-4-41.log | \
  awk -F "replicas=" '{print $2}' | \
  awk -F 'for' '{print $1}' | \
  awk -F ',' '{print $1,$2,$3}' | \
  awk -F" " '{for(i=1;i<=NF;i++) print $i}'
```

2、查看分钟粒度 Block 的分配数

```
$ grep allocate hadoop-hadoop-namenode-dx-lt-yd-zhejiang-jinhua-5-10-104-4-41.log.4 | \
  awk '{++a[substr($2,1,length($2)-7)]} END {for (k in a) {print $1" "k, a[k]}}' | sort
2023-09-05 04:07 3264
2023-09-05 04:08 9797
2023-09-05 04:09 10086
2023-09-05 04:10 11207
2023-09-05 04:11 12381
2023-09-05 04:12 7952
2023-09-05 04:13 7705
```

3、根据文件目录下 Block 的分配数排序

```
$ grep allocate hadoop-hadoop-namenode-dx-lt-yd-zhejiang-jinhua-5-10-104-4-41.log.4 | \
  grep "2023-09-05 04:09" | \
  awk '{print $NF}' | \
  awk -F '/' '{print "/"$2"/"$3"/"$4}'| \
  sort | uniq -c
8690 /user/hive/warehouse
```

### 执行命令

1、使用其他用户权限执行命令

```
$ sudo -u hadoop /opt/hadoop/bin/hdfs dfs -du -h /
```

2、文件未正常关闭，执行 recoverLease

```
$ sudo -u flume hdfs debug recoverLease -path  /fucheng.wang/crudeoil.hexun.com_202211220000.3.24.k7_haidene.1669046460213.gz -retries 10
```