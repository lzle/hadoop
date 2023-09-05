# hadoop


### 查看allocate分配的datanode节点

```
# 喜鹊
$ grep allocate hadoop-cmf-hdfs-NAMENODE-`hostname`.log.out.1 | \
  awk -F "replicas=" '{print $2}' | \
  awk -F 'for' '{print $1}' | \
  awk -F ',' '{print $1,$2,$3}' | \
  awk -F" " '{for(i=1;i<=NF;i++) print $i}'

# 金华
$ grep addStoredBlock hadoop-cmf-hdfs-NAMENODE-dx-lt-yd-zhejiang-jinhua-5-10-104-3-130.log.out.2 | \
  awk '{print $9}' | sort | uniq -c | sort
```


### 使用其他用户权限执行命令

```
$  sudo -u hadoop /opt/hadoop/bin/hdfs dfs -du -h /
```

### 按分钟粒度查看 allocate 速度

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

### 查看 allocate 的文件路径

```
$ grep allocate hadoop-hadoop-namenode-dx-lt-yd-zhejiang-jinhua-5-10-104-4-41.log.4 | \
  grep "2023-09-05 04:09" | \
  awk '{print $NF}' | \
  awk -F '/' '{print "/"$2"/"$3"/"$4}'| \
  sort | uniq -c
8690 /user/hive/warehouse
```
