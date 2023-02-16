# hadoop


查看allocate分配的datanode节点

```
grep allocate hadoop-cmf-hdfs-NAMENODE-`hostname`.log.out.1 | awk -F "replicas=" '{print $2}' | awk -F 'for' '{print $1}' | awk -F ',' '{print $1,$2,$3}' | awk -F" " '{for(i=1;i<=NF;i++) print $i}'
```
