# hadoop


### 查看allocate分配的datanode节点

```
# 喜鹊
grep allocate hadoop-cmf-hdfs-NAMENODE-`hostname`.log.out.1 | awk -F "replicas=" '{print $2}' | awk -F 'for' '{print $1}' | awk -F ',' '{print $1,$2,$3}' | awk -F" " '{for(i=1;i<=NF;i++) print $i}'

# 金华
grep addStoredBlock hadoop-cmf-hdfs-NAMENODE-dx-lt-yd-zhejiang-jinhua-5-10-104-3-130.log.out.2 | awk '{print $9}' | sort | uniq -c | sort
```


### 使用其他用户权限执行命令

```
sudo -u hadoop /opt/hadoop/bin/hdfs dfs -du -h /
```
