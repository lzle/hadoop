# HDFS 使用文档

## 目录

* [常用](#常用)
    * [统计Block分配](#统计Block分配)
    * [统计文件数&容量](#统计文件数量和容量)
    * [metric](#metric)
    * [文件时间](#文件时间)
    * [移动文件](#移动文件)
* [命令](#命令)
    * [systemd](#systemd)
    * [daemon](#daemon)
    * [dfsadmin](#dfsadmin)
    * [dfs](#dfs)
    * [haadmin](#haadmin)
    * [balancer](#balancer)
    * [fsck](#fsck)
* [日志](#日志)
    * [日志级别](#日志级别)
    * [心跳超时](#心跳超时)
    * [注册](#注册)
    * [上传文件](#上传文件)
    * [下载文件](#下载文件)
    * [删除文件](#删除文件)
    * [写锁](#写锁)
* [问题](#问题)
* [相关文档](#相关文档)

## 常用

### 统计 Block 分配

#### 1、NameNode 节点查看 Block 分配是否平衡

喜鹊集群

```
$ grep allocate hadoop-cmf-hdfs-NAMENODE-`hostname`.log.out.1 | \
  awk -F "replicas=" '{print $2}' | \
  awk -F 'for' '{print $1}' | \
  awk -F ',' '{print $1,$2,$3}' | \
  awk -F " " '{for(i=1;i<=NF;i++) print $i}' | sort | uniq -c | sort -n
  
10172 10.104.6.154:9866
10268 10.104.6.158:9866
10302 10.104.6.160:9866
10304 10.104.6.156:9866
10311 10.104.6.157:9866
10482 10.104.6.155:9866
10611 10.104.6.159:9866
```

新金华集群

```
$ grep allocate  hadoop-hadoop-namenode-dx-lt-yd-zhejiang-jinhua-5-10-104-4-41.log | \
  awk -F "replicas=" '{print $2}' | \
  awk -F 'for' '{print $1}' | \
  awk -F ',' '{print $1,$2,$3}' | \
  awk -F " " '{for(i=1;i<=NF;i++) print $i}' | sort | uniq -c | sort -n
  
219 10.104.8.52:9866
224 10.104.8.145:9866
225 10.104.8.163:9866
226 10.104.8.155:9866
231 10.104.8.170:9866
243 10.104.8.169:9866
```

#### 2、统计分钟粒度 Block 的分配数量

新金华集群

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

#### 3、统计文件路径下 Block 的分配数并排序

新金华集群

```
$ grep allocate hadoop-hadoop-namenode-dx-lt-yd-zhejiang-jinhua-5-10-104-4-41.log.4 | \
  grep "2023-09-05 04:09" | \
  awk '{print $NF}' | \
  awk -F '/' '{print "/"$2"/"$3"/"$4}'| \
  sort | uniq -c

8690 /user/hive/warehouse
2634 /separated_tengine/zzx.sinaimg.cn/20240204
```

### 统计文件数量和容量

#### 1、统计文件系统下1级目录下文件的数量

新金华

```
$ sudo -u hadoop /opt/hadoop/bin/hdfs dfs -count -h -t '/*'

  71        3.6 K              5.5 T /audit
58.8 K        6.1 M            637.5 T /data
  89          275             10.9 G /dolphinscheduler
   4            0                  0 /home
  42           13             51.0 M /jarod
49.5 K       15.4 M            105.0 T /separated
 151      137.4 K             62.6 G /separated_bgaa
   2          917            668.2 G /separated_bk
   2          120            232.0 G /separated_ic
 113        1.8 M             70.5 T /separated_ict
```

#### 2、统计文件系统下1级目录使用容量

新金华

```
$ sudo -u hadoop /opt/hadoop/bin/hdfs dfs -du -h '/'

5.5 T    16.4 T   /audit
638.2 T  1.9 P    /data
10.9 G   32.6 G   /dolphinscheduler
0        0        /home
51.0 M   152.9 M  /jarod
105.4 T  321.3 T  /separated
62.8 G   276.8 G  /separated_bgaa
668.2 G  2.0 T    /separated_bk
232.0 G  696.0 G  /separated_ic
70.6 T   211.8 T  /separated_ict
```

### metric

获取 NameNode metric 数据

```
$ curl -v http://dx-lt-yd-hebei-shijiazhuang-10-10-103-1-34:17106/metric
```

### 文件时间

文件时间在 create 时就会生成，在 close 时进行更新，执行修改操作（append）时间也会更新

```
$ hdfs dfs -ls /tmp/
-rwxrwxrwx   2 hadoop supergroup    1048582 2023-11-02 14:28 /tmp/10M
-rwxrwxrwx   2 hadoop supergroup    1048582 2023-11-02 14:46 /tmp/1M
-rw-r--r--   2 hdfs   supergroup       1861 2024-02-04 15:11 /tmp/bsy-fujian-xiamen-1-172-18-154-107_1707030392.91.file
```

### 移动文件

```
$ sudo -u hadoop /opt/hadoop/bin/hdfs dfs -mv /separated_ict/st-bak.dl.vycloud.vip/20240712* /separated_ict_backup/st-bak.dl.vycloud.vip/20240712/
```

## 命令

### systemd

使用 systemd 管理服务

```bash
$ ll /etc/systemd/system/multi-user.target.wants/datanode.service
lrwxrwxrwx 1 root root 40 Nov 24 15:20 /etc/systemd/system/multi-user.target.wants/datanode.service -> /usr/lib/systemd/system/datanode.service
```

查看 datanode.service 文件内容（namenode.service 也是同样的方式）。

```bash
$ cat /usr/lib/systemd/system/datanode.service
[Unit]
Description=datanode
After=syslog.target network.target

[Service]
Type=forking
User=hadoop
Group=hadoop
ExecStart=/opt/hadoop/bin/hdfs --daemon start datanode
ExecStop=/opt/hadoop/bin/hdfs --daemon stop datanode
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

使用命令

```bash
$ systemctl status datanode
$ systemctl stop datanode
$ systemctl start datanode
```

### daemon

NameNode 启动/停止

```bash
$ hdfs --daemon start namenode
$ hdfs --daemon stop namenode
$ /opt/hadoop/bin/hdfs --daemon status namenode
```

DataNode 启动/停止

```bash
$ hdfs --daemon start datanode
$ hdfs --daemon stop datanode
$ /opt/hadoop/bin/hdfs --daemon status datanode
```

Usage 信息

```bash
Daemon Commands:

balancer             run a cluster balancing utility
datanode             run a DFS datanode
dfsrouter            run the DFS router
diskbalancer         Distributes data evenly among disks on a given node
httpfs               run HttpFS server, the HDFS HTTP Gateway
journalnode          run the DFS journalnode
mover                run a utility to move block replicas across storage types
namenode             run the DFS namenode
nfs3                 run an NFS version 3 gateway
portmap              run a portmap service
secondarynamenode    run the DFS secondary namenode
zkfc                 run the ZK Failover Controller daemon
```

### dfsadmin

汇报集群状态，用了查看真实活跃的 datanode 数量。

```bash
$ sudo -u hadoop /opt/hadoop/bin/hdfs dfsadmin -report -live
$ sudo -u hadoop /opt/hadoop/bin/hdfs dfsadmin -report -dead
```

刷新节点，一般用来退役节点，更新 hdfs-exclude。

```bash
$ echo 'decommissioning-hostname' >> /opt/hadoop/etc/hadoop/hdfs-exclude
$ sudo -u hadoop /opt/hadoop/bin/hdfs dfsadmin -refreshNodes
```

Usage 信息

```bash
$ hdfs dfsadmin -h
Usage: hdfs dfsadmin
Note: Administrative commands can only be run as the HDFS superuser.
	[-report [-live] [-dead] [-decommissioning] [-enteringmaintenance] [-inmaintenance]]
	[-safemode <enter | leave | get | wait>]
	[-saveNamespace [-beforeShutdown]]
	[-rollEdits]
	[-restoreFailedStorage true|false|check]
	[-refreshNodes]
	[-setQuota <quota> <dirname>...<dirname>]
	[-clrQuota <dirname>...<dirname>]
	[-setSpaceQuota <quota> [-storageType <storagetype>] <dirname>...<dirname>]
	[-clrSpaceQuota [-storageType <storagetype>] <dirname>...<dirname>]
	[-finalizeUpgrade]
	[-rollingUpgrade [<query|prepare|finalize>]]
	[-upgrade <query | finalize>]
	[-refreshServiceAcl]
	[-refreshUserToGroupsMappings]
	[-refreshSuperUserGroupsConfiguration]
	[-refreshCallQueue]
	[-refresh <host:ipc_port> <key> [arg1..argn]
	[-reconfig <namenode|datanode> <host:ipc_port> <start|status|properties>]
	[-printTopology]
	[-refreshNamenodes datanode_host:ipc_port]
	[-getVolumeReport datanode_host:ipc_port]
	[-deleteBlockPool datanode_host:ipc_port blockpoolId [force]]
	[-setBalancerBandwidth <bandwidth in bytes per second>]
	[-getBalancerBandwidth <datanode_host:ipc_port>]
	[-fetchImage <local directory>]
	[-allowSnapshot <snapshotDir>]
	[-disallowSnapshot <snapshotDir>]
	[-shutdownDatanode <datanode_host:ipc_port> [upgrade]]
	[-evictWriters <datanode_host:ipc_port>]
	[-getDatanodeInfo <datanode_host:ipc_port>]
	[-metasave filename]
	[-triggerBlockReport [-incremental] <datanode_host:ipc_port>]
	[-listOpenFiles [-blockingDecommission] [-path <path>]]
	[-help [cmd]]
```

### dfs

1、创建目录

```bash
$ hdfs dfs -mkdir -p /lzl/test
```

2、从本地上传文件

```bash
$ hdfs dfs -put a.txt /lzl/test
```

3、从本地上传目录

```bash
$ hdfs dfs -copyFromLocal localdir /lzl/test

# 两者效果不一样
$ hdfs dfs -copyFromLocal localdir/* /lzl/test
```

4、上传本地目录并删除

```bash
$ hdfs dfs -moveFromLocal localdir /lzl/test
```

5、查看文件

```bash
$ hdfs dfs -cat /lzl/test/a.txt
```

6、下载文件

```bash
$ hdfs dfs -get /lzl/test/b.txt ./
```

7、下载目录

```bash
# 本地有 test 目录
$ hdfs dfs -copyToLocal /lzl/test ./
```

8、删除文件/目录

```bash
# -r 递归删除子目录
$ hdfs dfs -rm -r /lzl/test
```

9、查看压缩文件内容

```bash
$ hdfs dfs -text /lzl/test.gz
```

Usage 信息如下

```bash
$ hdfs dfs -h
Usage: hadoop fs [generic options]
	[-appendToFile <localsrc> ... <dst>]
	[-cat [-ignoreCrc] <src> ...]
	[-checksum <src> ...]
	[-chgrp [-R] GROUP PATH...]
	[-chmod [-R] <MODE[,MODE]... | OCTALMODE> PATH...]
	[-chown [-R] [OWNER][:[GROUP]] PATH...]
	[-copyFromLocal [-f] [-p] [-l] [-d] [-t <thread count>] <localsrc> ... <dst>]
	[-copyToLocal [-f] [-p] [-ignoreCrc] [-crc] <src> ... <localdst>]
	[-count [-q] [-h] [-v] [-t [<storage type>]] [-u] [-x] [-e] <path> ...]
	[-cp [-f] [-p | -p[topax]] [-d] <src> ... <dst>]
	[-createSnapshot <snapshotDir> [<snapshotName>]]
	[-deleteSnapshot <snapshotDir> <snapshotName>]
	[-df [-h] [<path> ...]]
	[-du [-s] [-h] [-v] [-x] <path> ...]
	[-expunge]
	[-find <path> ... <expression> ...]
	[-get [-f] [-p] [-ignoreCrc] [-crc] <src> ... <localdst>]
	[-getfacl [-R] <path>]
	[-getfattr [-R] {-n name | -d} [-e en] <path>]
	[-getmerge [-nl] [-skip-empty-file] <src> <localdst>]
	[-head <file>]
	[-help [cmd ...]]
	[-ls [-C] [-d] [-h] [-q] [-R] [-t] [-S] [-r] [-u] [-e] [<path> ...]]
	[-mkdir [-p] <path> ...]
	[-moveFromLocal <localsrc> ... <dst>]
	[-moveToLocal <src> <localdst>]
	[-mv <src> ... <dst>]
	[-put [-f] [-p] [-l] [-d] <localsrc> ... <dst>]
	[-renameSnapshot <snapshotDir> <oldName> <newName>]
	[-rm [-f] [-r|-R] [-skipTrash] [-safely] <src> ...]
	[-rmdir [--ignore-fail-on-non-empty] <dir> ...]
	[-setfacl [-R] [{-b|-k} {-m|-x <acl_spec>} <path>]|[--set <acl_spec> <path>]]
	[-setfattr {-n name [-v value] | -x name} <path>]
	[-setrep [-R] [-w] <rep> <path> ...]
	[-stat [format] <path> ...]
	[-tail [-f] <file>]
	[-test -[defsz] <path>]
	[-text [-ignoreCrc] <src> ...]
	[-touch [-a] [-m] [-t TIMESTAMP ] [-c] <path> ...]
	[-touchz <path> ...]
	[-truncate [-w] <length> <path> ...]
	[-usage [cmd ...]]
```

### haadmin

查看节点状态

```bash
$ hdfs haadmin -getServiceState nn1
```

将 nn1 切换为 standby 备用节点

```bash
$ hdfs haadmin -transitionToStandby --forcemanual nn1
```

把 active 切换到 nn1 上

```bash
$ sudo -u hadoop /opt/hadoop/bin/hdfs haadmin -failover nn2 nn1
```

查看 NameNode 状态

```bash
$ hdfs haadmin -getAllServiceState
dx-lt-yd-hebei-shijiazhuang-10-10-103-1-34:8020    active
dx-lt-yd-hebei-shijiazhuang-10-10-103-2-160:8020   standby
dx-lt-yd-hebei-shijiazhuang-10-10-103-2-25:8020    standby
```

Usage 信息如下

```bash
$ hdfs  haadmin
Usage: haadmin [-ns <nameserviceId>]
    [-transitionToActive [--forceactive] <serviceId>]
    [-transitionToStandby <serviceId>]
    [-failover [--forcefence] [--forceactive] <serviceId> <serviceId>]
    [-getServiceState <serviceId>]
    [-getAllServiceState]
    [-checkHealth <serviceId>]
    [-help <command>]
```

### balancer

数据平衡工具，Usage 信息

```bash
$ hdfs  balancer -h
Usage: hdfs balancer
	[-policy <policy>]	the balancing policy: datanode or blockpool
	[-threshold <threshold>]	Percentage of disk capacity
	[-exclude [-f <hosts-file> | <comma-separated list of hosts>]]	Excludes the specified datanodes.
	[-include [-f <hosts-file> | <comma-separated list of hosts>]]	Includes only the specified datanodes.
	[-source [-f <hosts-file> | <comma-separated list of hosts>]]	Pick only the specified datanodes as source nodes.
	[-blockpools <comma-separated list of blockpool ids>]	The balancer will only run on blockpools included in this list.
	[-idleiterations <idleiterations>]	Number of consecutive idle iterations (-1 for Infinite) before exit.
	[-runDuringUpgrade]	Whether to run the balancer during an ongoing HDFS upgrade.This is usually not desired since it will not affect used space on over-utilized machines.
```

### fsck

查看文件目录的健康信息、状态、块报告、文件中损坏的块等。它旨在报告各种文件的问题。

1、检查目录下或文件是否存在损坏的 block

```bash
$ hdfs fsck -fs hdfs://dx-lt-yd-zhejiang-jinhua-5-10-104-4-41:8020/ /data  -list-corruptfileblocks
Connecting to namenode via http://dx-lt-yd-zhejiang-jinhua-5-10-104-4-41:9870/fsck?ugi=hadoop&listcorruptfileblocks=1&path=%2Ftmp
The filesystem under path '/data' has 0 CORRUPT files
```

2、检查目录下或文件是否处于 openforwrite 状态

```bash
hdfs fsck -fs hdfs://dx-lt-yd-zhejiang-jinhua-5-10-104-4-41:8020/ /data -openforwrite
```

3、检查文件的基本信息，HEALTHY 表示文件正常

```bash
$ hdfs fsck -fs hdfs://dx-lt-yd-zhejiang-jinhua-5-10-104-4-41:8020/ /tmp/fsck-file
Connecting to namenode via http://dx-lt-yd-zhejiang-jinhua-5-10-104-4-41:9870/fsck?ugi=hadoop&path=%2Ftmp%2Ffsck-file
FSCK started by hadoop (auth:SIMPLE) from /10.104.4.41 for path /tmp/fsck-file at Mon Dec 04 01:14:39 CST 2023

Status: HEALTHY
 Number of data-nodes:	207
 Number of racks:		1
 Total dirs:			0
 Total symlinks:		0

Replicated Blocks:
 Total size:	2188 B
 Total files:	1
 Total blocks (validated):	1 (avg. block size 2188 B)
 Minimally replicated blocks:	1 (100.0 %)
 Over-replicated blocks:	0 (0.0 %)
 Under-replicated blocks:	0 (0.0 %)
 Mis-replicated blocks:		0 (0.0 %)
 Default replication factor:	3
 Average block replication:	3.0
 Missing blocks:		0
 Corrupt blocks:		0
 Missing replicas:		0 (0.0 %)

Erasure Coded Block Groups:
    ......
FSCK ended at Mon Dec 04 01:14:39 CST 2023 in 0 milliseconds


The filesystem under path '/tmp/fsck-file' is HEALTHY
```

4、输出文件 block 信息，包含 blockid

```bash
$ hdfs fsck -fs hdfs://dx-lt-yd-zhejiang-jinhua-5-10-104-4-41:8020/ /tmp/fsck-file -files -blocks
Connecting to namenode via http://dx-lt-yd-zhejiang-jinhua-5-10-104-4-41:9870/fsck?ugi=hadoop&files=1&blocks=1&path=%2Ftmp%2Ffsck-file
FSCK started by hadoop (auth:SIMPLE) from /10.104.4.41 for path /tmp/fsck-file at Mon Dec 04 01:23:40 CST 2023
/tmp/fsck-file 2188 bytes, replicated: replication=3, 1 block(s):  OK
0. BP-1637949269-10.104.5.12-1683817104974:blk_1961802534_888879227 len=2188 Live_repl=3

.....

The filesystem under path '/tmp/fsck-file' is HEALTHY
```

打印目录下所有的 block 信息

```bash
$ hdfs fsck  -fs hdfs://dx-lt-yd-zhejiang-jinhua-5-10-104-4-41:8020/ /tmp -files -blocks
/tmp/logs/flume/logs/application_1693785702620_63669/dx-lt-yd-zhejiang-jinhua-5-10-104-3-15_45454 31496 bytes, replicated: replication=3, 1 block(s):  OK
0. BP-1637949269-10.104.5.12-1683817104974:blk_1960221891_887297971 len=31496 Live_repl=3

/tmp/logs/flume/logs/application_1693785702620_63669/dx-lt-yd-zhejiang-jinhua-5-10-104-3-160_45454 32528 bytes, replicated: replication=3, 1 block(s):  OK
0. BP-1637949269-10.104.5.12-1683817104974:blk_1960221899_887297979 len=32528 Live_repl=3
```

5、除了输出 4 以外，输出对应的 datanode 节点

```bash
 hdfs fsck -fs hdfs://dx-lt-yd-zhejiang-jinhua-5-10-104-4-41:8020/ /tmp/fsck-file -files -blocks -locations
Connecting to namenode via http://dx-lt-yd-zhejiang-jinhua-5-10-104-4-41:9870/fsck?ugi=hadoop&files=1&blocks=1&locations=1&path=%2Ftmp%2Ffsck-file
FSCK started by hadoop (auth:SIMPLE) from /10.104.4.41 for path /tmp/fsck-file at Mon Dec 04 01:26:26 CST 2023
/tmp/fsck-file 2188 bytes, replicated: replication=3, 1 block(s):  OK
0. BP-1637949269-10.104.5.12-1683817104974:blk_1961802534_888879227 len=2188 Live_repl=3  [DatanodeInfoWithStorage[10.104.1.41:9866,DS-8d0c78ab-0dfa-48ac-a003-e9250e3c65ef,DISK], 
DatanodeInfoWithStorage[10.104.2.146:9866,DS-291037f4-3ee7-4323-a2c1-3fa147b3764d,DISK], DatanodeInfoWithStorage[10.104.8.26:9866,DS-7cc409c7-3ce8-4b04-bc38-29e01d765c60,DISK]]
```

6、根据 BlockID 输出对应的文件信息

不包含 generationStamp

```bash
$ hdfs fsck -fs hdfs://dx-lt-yd-zhejiang-jinhua-5-10-104-4-41:8020/ -blockId blk_1961802534
Connecting to namenode via http://dx-lt-yd-zhejiang-jinhua-5-10-104-4-41:9870/fsck?ugi=hadoop&blockId=blk_1961802534+&path=%2F
FSCK started by hadoop (auth:SIMPLE) from /10.104.4.41 at Mon Dec 04 01:30:34 CST 2023

Block Id: blk_1961802534
Block belongs to: /tmp/fsck-file
No. of Expected Replica: 3
No. of live Replica: 3
No. of excess Replica: 0
No. of stale Replica: 0
No. of decommissioned Replica: 0
No. of decommissioning Replica: 0
No. of corrupted Replica: 0
Block replica on datanode/rack: dx-lt-yd-zhejiang-jinhua-5-10-104-8-26/default-rack is HEALTHY
Block replica on datanode/rack: dx-lt-yd-zhejiang-jinhua-5-10-104-2-146/default-rack is HEALTHY
Block replica on datanode/rack: dx-lt-yd-zhejiang-jinhua-5-10-104-1-41/default-rack is HEALTHY
```

包含 generationStamp 需要在 blockid 加上 `.meta` 后缀

```bash
hdfs fsck  -fs hdfs://dx-lt-yd-zhejiang-jinhua-5-10-104-4-41:8020/ -blockId blk_1961802534_888879227.meta
Connecting to namenode via http://dx-lt-yd-zhejiang-jinhua-5-10-104-4-41:9870/fsck?ugi=hadoop&blockId=blk_1961802534_888879227.meta+&path=%2F
FSCK started by hadoop (auth:SIMPLE) from /10.104.4.41 at Mon Dec 04 01:39:44 CST 2023

Block Id: blk_1961802534_888879227.meta
Block belongs to: /tmp/fsck-file
No. of Expected Replica: 3
No. of live Replica: 3
No. of excess Replica: 0
No. of stale Replica: 0
No. of decommissioned Replica: 0
No. of decommissioning Replica: 0
No. of corrupted Replica: 0
Block replica on datanode/rack: dx-lt-yd-zhejiang-jinhua-5-10-104-8-26/default-rack is HEALTHY
Block replica on datanode/rack: dx-lt-yd-zhejiang-jinhua-5-10-104-2-146/default-rack is HEALTHY
Block replica on datanode/rack: dx-lt-yd-zhejiang-jinhua-5-10-104-1-41/default-rack is HEALTHY
```

Usage 信息

```bash
$ hdfs fsck
Usage: hdfs fsck <path> [-list-corruptfileblocks | [-move | -delete | -openforwrite] [-files [-blocks [-locations | -racks | -replicaDetails | -upgradedomains]]]] [-includeSnapshots] [-showprogress] [-storagepolicies] [-maintenance] [-blockId <blk_Id>]
	<path>	start checking from this path
	-move	move corrupted files to /lost+found
	-delete	delete corrupted files
	-files	print out files being checked
	-openforwrite	print out files opened for write
	-includeSnapshots	include snapshot data if the given path indicates a snapshottable directory or there are snapshottable directories under it
	-list-corruptfileblocks	print out list of missing blocks and files they belong to
	-files -blocks	print out block report
	-files -blocks -locations	print out locations for every block
	-files -blocks -racks	print out network topology for data-node locations
	-files -blocks -replicaDetails	print out each replica details
	-files -blocks -upgradedomains	print out upgrade domains for every block
	-storagepolicies	print out storage policy summary for the blocks
	-maintenance	print out maintenance state node details
	-showprogress	show progress in output. Default is OFF (no progress)
	-blockId	print out which file this blockId belongs to, locations (nodes, racks) of this block, and other diagnostics info (under replicated, corrupted or not, etc)
```

## 日志

### 日志级别

动态修改日志级别，无需重启，重启后失效

**NameNode**

```bash
http://bsy-fujian-xiamen-1-172-18-154-201:9870/logLevel

org.apache.commons.logging.impl.Log4JLogger
BlockStateChange
org.apache.hadoop.hdfs.StateChange
```

**DataNode**

```bash
http://bsy-fujian-xiamen-1-172-18-154-201:9864/logLevel

org.apache.hadoop.hdfs.server.datanode.DataNode
org.apache.hadoop.hdfs.server.datanode.IncrementalBlockReportManager
```

### 心跳超时

DataNode 端日志输出

```
2022-12-02 15:22:04,287 INFO org.apache.hadoop.hdfs.StateChange: BLOCK* removeDeadDatanode: lost heartbeat from 172.18.154.201:9866, removeBlocksFromBlockMap true
2022-12-02 15:22:04,291 INFO org.apache.hadoop.net.NetworkTopology: Removing a node: /default-rack/172.18.154.201:9866
```

### 注册

NameNode 端日志输出

```
2022-12-02 15:26:07,556 INFO org.apache.hadoop.hdfs.StateChange: BLOCK* registerDatanode: from DatanodeRegistration(172.18.154.201:9866, datanodeUuid=126b4743-728d-4800-b5bd-5e83c819fecc, infoPort=9864, infoSecurePort=0, ipcPort=9867, storageInfo=lv=-57;cid=CID-b3746fbe-15c7-4492-9690-29df9fcf4749;nsid=652530984;c=1666691608942) storage 126b4743-728d-4800-b5bd-5e83c819fecc
2022-12-02 15:26:07,556 INFO org.apache.hadoop.net.NetworkTopology: Removing a node: /default-rack/172.18.154.201:9866
2022-12-02 15:26:07,556 INFO org.apache.hadoop.net.NetworkTopology: Adding a new node: /default-rack/172.18.154.201:9866
2022-12-02 15:26:07,556 INFO org.apache.hadoop.hdfs.server.blockmanagement.DatanodeDescriptor: [DISK]DS-cfb05c2b-211c-4e42-9f22-b6999d341f88:NORMAL:172.18.154.201:9866 failed.
2022-12-02 15:26:07,556 INFO org.apache.hadoop.hdfs.server.blockmanagement.DatanodeDescriptor: Removed storage [DISK]DS-cfb05c2b-211c-4e42-9f22-b6999d341f88:FAILED:172.18.154.201:9866 from DataNode 172.18.154.201:9866
2022-12-02 15:26:07,564 INFO org.apache.hadoop.hdfs.server.blockmanagement.DatanodeDescriptor: Adding new storage ID DS-cfb05c2b-211c-4e42-9f22-b6999d341f88 for DN 172.18.154.201:9866
2022-12-02 15:26:07,565 WARN org.apache.hadoop.hdfs.server.blockmanagement.BlockReportLeaseManager: DN 126b4743-728d-4800-b5bd-5e83c819fecc (172.18.154.201:9866) requested a lease even though it wasn't yet registered.  Registering now.
2022-12-02 15:26:07,565 INFO org.apache.hadoop.hdfs.server.blockmanagement.BlockReportLeaseManager: Registered DN 126b4743-728d-4800-b5bd-5e83c819fecc (172.18.154.201:9866).
2022-12-02 15:26:07,645 INFO BlockStateChange: BLOCK* processReport 0xc8a3e68f7a2a8a4a: Processing first storage report for DS-cfb05c2b-211c-4e42-9f22-b6999d341f88 from datanode 126b4743-728d-4800-b5bd-5e83c819fecc
2022-12-02 15:26:07,647 INFO BlockStateChange: BLOCK* processReport 0xc8a3e68f7a2a8a4a: from storage DS-cfb05c2b-211c-4e42-9f22-b6999d341f88 node DatanodeRegistration(172.18.154.201:9866, datanodeUuid=126b4743-728d-4800-b5bd-5e83c819fecc, infoPort=9864, infoSecurePort=0, ipcPort=9867, storageInfo=lv=-57;cid=CID-b3746fbe-15c7-4492-9690-29df9fcf4749;nsid=652530984;c=1666691608942), blocks: 207, hasStaleStorage: false, processing time: 2 msecs, invalidatedBlocks: 0
2022-12-02 15:26:08,833 INFO org.apache.hadoop.hdfs.server.blockmanagement.BlockManager: Rescan of postponedMisreplicatedBlocks completed in 0 msecs. 207 blocks are left. 0 blocks were removed.
2022-12-02 15:26:11,834 INFO org.apache.hadoop.hdfs.server.blockmanagement.BlockManager: Rescan of postponedMisreplicatedBlocks completed in 0 msecs. 207 blocks are left. 0 blocks were removed.
2022-12-02 15:26:14,835 INFO org.apache.hadoop.hdfs.server.blockmanagement.BlockManager: Rescan of postponedMisreplicatedBlocks completed in 0 msecs. 207 blocks are left. 0 blocks were removed.
```

### 上传文件

NameNode 端日志输出

```
2023-01-03 14:50:13,911 DEBUG org.apache.hadoop.hdfs.StateChange: *DIR* NameNode.create: file /lzl/test/c.txt._COPYING_ for DFSClient_NONMAPREDUCE_-1987862239_1 at 172.18.154.107
2023-01-03 14:50:13,912 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* NameSystem.startFile: src=/lzl/test/c.txt._COPYING_, holder=DFSClient_NONMAPREDUCE_-1987862239_1, clientMachine=172.18.154.107, createParent=true, replication=2, createFlag=[CREATE, OVERWRITE], blockSize=268435456, supportedVersions=[CryptoProtocolVersion{description='Encryption zones', version=2, unknownValue=null}]
2023-01-03 14:50:13,912 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* addFile: c.txt._COPYING_ is added
2023-01-03 14:50:13,913 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* NameSystem.startFile: added /lzl/test/c.txt._COPYING_ inode 18367 DFSClient_NONMAPREDUCE_-1987862239_1
2023-01-03 14:50:13,961 DEBUG org.apache.hadoop.hdfs.StateChange: BLOCK* getAdditionalBlock: /lzl/test/c.txt._COPYING_  inodeId 18367 for DFSClient_NONMAPREDUCE_-1987862239_1
2023-01-03 14:50:13,963 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.addBlock: /lzl/test/c.txt._COPYING_ with blk_1073743790_2966 block is added to the in-memory file system
2023-01-03 14:50:13,963 INFO org.apache.hadoop.hdfs.StateChange: BLOCK* allocate blk_1073743790_2966, replicas=172.18.154.107:9866, 172.18.154.224:9866 for /lzl/test/c.txt._COPYING_
2023-01-03 14:50:13,963 DEBUG org.apache.hadoop.hdfs.StateChange: persistNewBlock: /lzl/test/c.txt._COPYING_ with new block blk_1073743790_2966, current total block count is 1
2023-01-03 14:50:14,287 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* NameSystem.completeFile: /lzl/test/c.txt._COPYING_ for DFSClient_NONMAPREDUCE_-1987862239_1
2023-01-03 14:50:14,287 DEBUG org.apache.hadoop.hdfs.StateChange: closeFile: /lzl/test/c.txt._COPYING_ with 1 blocks is persisted to the file system
2023-01-03 14:50:14,288 INFO org.apache.hadoop.hdfs.StateChange: DIR* completeFile: /lzl/test/c.txt._COPYING_ is closed by DFSClient_NONMAPREDUCE_-1987862239_1
2023-01-03 14:50:14,297 DEBUG org.apache.hadoop.hdfs.StateChange: *DIR* NameNode.rename: /lzl/test/c.txt._COPYING_ to /lzl/test/c.txt
2023-01-03 14:50:14,297 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* NameSystem.renameTo: /lzl/test/c.txt._COPYING_ to /lzl/test/c.txt
2023-01-03 14:50:14,297 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.renameTo: /lzl/test/c.txt._COPYING_ to /lzl/test/c.txt
2023-01-03 14:50:14,298 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.unprotectedRenameTo: /lzl/test/c.txt._COPYING_ is renamed to /lzl/test/c.txt
```

DataNode 端日志输出

```
2023-02-08 17:55:56,576 INFO org.apache.hadoop.hdfs.server.datanode.DataNode: Receiving BP-182789411-172.18.154.107-1666691608942:blk_1073743793_2969 src: /172.18.154.201:37440 dest: /172.18.154.107:9866
2023-02-08 17:55:56,606 INFO org.apache.hadoop.hdfs.server.datanode.DataNode.clienttrace: src: /172.18.154.201:37440, dest: /172.18.154.107:9866, bytes: 25968, op: HDFS_WRITE, cliID: DFSClient_NONMAPREDUCE_469479046_1, offset: 0, srvID: e9570619-9a17-4c1e-8471-3d044ae9dcd3, blockid: BP-182789411-172.18.154.107-1666691608942:blk_1073743793_2969, duration(ns): 26624471
2023-02-08 17:55:56,606 INFO org.apache.hadoop.hdfs.server.datanode.DataNode: PacketResponder: BP-182789411-172.18.154.107-1666691608942:blk_1073743793_2969, type=LAST_IN_PIPELINE terminating
```

### 下载文件

无日志

### 删除文件

DataNode 端日志输出，移动到回收站

```
2023-05-29 22:22:48,191 DEBUG org.apache.hadoop.hdfs.StateChange: *DIR* NameNode.mkdirs: /user/hadoop/.Trash/Current/tmp
2023-05-29 22:22:48,191 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* NameSystem.mkdirs: /user/hadoop/.Trash/Current/tmp
2023-05-29 22:22:48,199 DEBUG org.apache.hadoop.hdfs.StateChange: *DIR* NameNode.rename: /tmp/c.txt to /user/hadoop/.Trash/Current/tmp/c.txt1685370168196
2023-05-29 22:22:48,200 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* NameSystem.renameTo: with options - /tmp/c.txt to /user/hadoop/.Trash/Current/tmp/c.txt1685370168196
2023-05-29 22:22:48,200 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.renameTo: /tmp/c.txt to /user/hadoop/.Trash/Current/tmp/c.txt1685370168196
2023-05-29 22:22:48,200 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.unprotectedRenameTo: /tmp/c.txt is renamed to /user/hadoop/.Trash/Current/tmp/c.txt1685370168196
2023-05-29 22:22:48,200 INFO org.apache.hadoop.hdfs.server.namenode.FSEditLog: Number of transactions: 8 Total time for transactions(ms): 4 Number of transactions batched in Syncs: 1 Number of syncs: 6 SyncTimes(ms): 140 41
```

### 写锁

NameNode 端日志输出

```
[root@dx-lt-yd-zhejiang-jinhua-5-10-104-4-41 hadoop]# grep -rn "FSNamesystem write lock held" hadoop-hadoop-namenode-dx-lt-yd-zhejiang-jinhua-5-10-104-4-41.*
hadoop-hadoop-namenode-dx-lt-yd-zhejiang-jinhua-5-10-104-4-41.log:33372:2024-07-15 11:16:43,924 INFO org.apache.hadoop.hdfs.server.namenode.FSNamesystem: FSNamesystem write lock held for 11966 ms via java.lang.Thread.getStackTrace(Thread.java:1559)
hadoop-hadoop-namenode-dx-lt-yd-zhejiang-jinhua-5-10-104-4-41.log.1:580127:2024-07-15 11:13:34,160 INFO org.apache.hadoop.hdfs.server.namenode.FSNamesystem: FSNamesystem write lock held for 5665 ms via java.lang.Thread.getStackTrace(Thread.java:1559)
hadoop-hadoop-namenode-dx-lt-yd-zhejiang-jinhua-5-10-104-4-41.log.100:118884:2024-07-14 20:12:24,745 INFO org.apache.hadoop.hdfs.server.namenode.FSNamesystem: FSNamesystem write lock held for 10207 ms via java.lang.Thread.getStackTrace(Thread.java:1559)
hadoop-hadoop-namenode-dx-lt-yd-zhejiang-jinhua-5-10-104-4-41.log.100:791722:2024-07-14 20:19:57,180 INFO org.apache.hadoop.hdfs.server.namenode.FSNamesystem: FSNamesystem write lock held for 16606 ms via java.lang.Thread.getStackTrace(Thread.java:1559)
hadoop-hadoop-namenode-dx-lt-yd-zhejiang-jinhua-5-10-104-4-41.log.100:896340:2024-07-14 20:21:17,531 INFO org.apache.hadoop.hdfs.server.namenode.FSNamesystem: FSNamesystem write lock held for 7541 ms via java.lang.Thread.getStackTrace(Thread.java:1559)
hadoop-hadoop-namenode-dx-lt-yd-zhejiang-jinhua-5-10-104-4-41.log.14:744456:2024-07-15 09:36:45,901 INFO org.apache.hadoop.hdfs.server.namenode.FSNamesystem: FSNamesystem write lock held for 8511 ms via java.lang.Thread.getStackTrace(Thread.java:1559)
hadoop-hadoop-namenode-dx-lt-yd-zhejiang-jinhua-5-10-104-4-41.log.15:162524:2024-07-15 09:29:26,556 INFO org.apache.hadoop.hdfs.server.namenode.FSNamesystem: FSNamesystem write lock held for 18014 ms via java.lang.Thread.getStackTrace(Thread.java:1559)
hadoop-hadoop-namenode-dx-lt-yd-zhejiang-jinhua-5-10-104-4-41.log.15:671008:2024-07-15 09:32:20,644 INFO org.apache.hadoop.hdfs.server.namenode.FSNamesystem: FSNamesystem write lock held for 20715 ms via java.lang.Thread.getStackTrace(Thread.java:1559)
```

## 问题

[问题追踪](hdfs/troubleshooting.md)

### 1、默认 Block Size 的大小

金华 HDFS 集群 128M，石家庄、喜鹊、海外 HDFS 集群 256M，默认 128M

```
<property>
<name>dfs.blocksize</name>
<value>134217728</value>
<final>false</final>
<source>hdfs-default.xml</source>
</property>
```

### 2、不同客户端并发上传，会有什么效果

客户端 10.104.4.41
```
[root@dx-lt-yd-zhejiang-jinhua-5-10-104-7-155 ~]# hdfs dfs -put -f 500M /tmp/500M
2024-07-21 03:16:47,956 WARN ha.RequestHedgingProxyProvider: Invocation returned exception on [dx-lt-yd-zhejiang-jinhua-5-10-104-4-41/10.104.4.41:8020]
org.apache.hadoop.ipc.RemoteException(java.io.FileNotFoundException): File does not exist: /tmp/500M._COPYING_ (inode 3102566644) Holder DFSClient_NONMAPREDUCE_1503873289_1 does not have any open files.
	at org.apache.hadoop.hdfs.server.namenode.FSNamesystem.checkLease(FSNamesystem.java:2811)
	at org.apache.hadoop.hdfs.server.namenode.FSDirWriteFileOp.completeFileInternal(FSDirWriteFileOp.java:699)
	at org.apache.hadoop.hdfs.server.namenode.FSDirWriteFileOp.completeFile(FSDirWriteFileOp.java:685)
	at org.apache.hadoop.hdfs.server.namenode.FSNamesystem.completeFile(FSNamesystem.java:2854)
	at org.apache.hadoop.hdfs.server.namenode.NameNodeRpcServer.complete(NameNodeRpcServer.java:928)
	at org.apache.hadoop.hdfs.protocolPB.ClientNamenodeProtocolServerSideTranslatorPB.complete(ClientNamenodeProtocolServerSideTranslatorPB.java:607)
```

客户端 10.104.5.12

```
[root@dx-lt-yd-zhejiang-jinhua-5-10-104-5-12 ~]#  hdfs dfs -put -f 500M /tmp/500M
2024-07-21 03:16:47,996 WARN ha.RequestHedgingProxyProvider: Invocation returned exception on [dx-lt-yd-zhejiang-jinhua-5-10-104-4-41/10.104.4.41:8020]
org.apache.hadoop.ipc.RemoteException(java.io.FileNotFoundException): File does not exist: /tmp/500M._COPYING_ (inode 3102566705) Holder DFSClient_NONMAPREDUCE_503911796_1 does not have any open files.
	at org.apache.hadoop.hdfs.server.namenode.FSNamesystem.checkLease(FSNamesystem.java:2811)
	at org.apache.hadoop.hdfs.server.namenode.FSDirWriteFileOp.analyzeFileState(FSDirWriteFileOp.java:605)
	at org.apache.hadoop.hdfs.server.namenode.FSDirWriteFileOp.validateAddBlock(FSDirWriteFileOp.java:172)
	at org.apache.hadoop.hdfs.server.namenode.FSNamesystem.getAdditionalBlock(FSNamesystem.java:2690)
	at org.apache.hadoop.hdfs.server.namenode.NameNodeRpcServer.addBlock(NameNodeRpcServer.java:875)
	at org.apache.hadoop.hdfs.protocolPB.ClientNamenodeProtocolServerSideTranslatorPB.addBlock(ClientNamenodeProtocolServerSideTranslatorPB.java:561)
```

日志

```
2024-07-21 03:16:46,404 DEBUG org.apache.hadoop.hdfs.StateChange: *DIR* NameNode.create: file /tmp/500M._COPYING_ for DFSClient_NONMAPREDUCE_1503873289_1 at 10.104.7.155
2024-07-21 03:16:46,404 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* NameSystem.startFile: src=/tmp/500M._COPYING_, holder=DFSClient_NONMAPREDUCE_1503873289_1, clientMachine=10.104.7.155, createParent=true, replication=3, createFlag=[CREATE, OVERWRITE], blockSize=134217728, supportedVersions=[CryptoProtocolVersion{description='Encryption zones', version=2, unknownValue=null}]
2024-07-21 03:16:46,404 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* NameSystem.startFile: added /tmp/500M._COPYING_ inode 3102566644 DFSClient_NONMAPREDUCE_1503873289_1
2024-07-21 03:16:46,440 DEBUG org.apache.hadoop.hdfs.StateChange: BLOCK* getAdditionalBlock: /tmp/500M._COPYING_  inodeId 3102566644 for DFSClient_NONMAPREDUCE_1503873289_1
2024-07-21 03:16:46,442 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.addBlock: /tmp/500M._COPYING_ with blk_3458315963_2386086046 block is added to the in-memory file system
2024-07-21 03:16:46,442 INFO org.apache.hadoop.hdfs.StateChange: BLOCK* allocate blk_3458315963_2386086046, replicas=10.104.21.14:9866, 10.104.16.53:9866, 10.104.1.5:9866 for /tmp/500M._COPYING_
2024-07-21 03:16:46,442 DEBUG org.apache.hadoop.hdfs.StateChange: persistNewBlock: /tmp/500M._COPYING_ with new block blk_3458315963_2386086046, current total block count is 1
2024-07-21 03:16:46,869 DEBUG org.apache.hadoop.hdfs.StateChange: BLOCK* getAdditionalBlock: /tmp/500M._COPYING_  inodeId 3102566644 for DFSClient_NONMAPREDUCE_1503873289_1
2024-07-21 03:16:46,872 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.addBlock: /tmp/500M._COPYING_ with blk_3458315972_2386086055 block is added to the in-memory file system
2024-07-21 03:16:46,872 INFO org.apache.hadoop.hdfs.StateChange: BLOCK* allocate blk_3458315972_2386086055, replicas=10.104.3.139:9866, 10.104.3.8:9866, 10.104.4.4:9866 for /tmp/500M._COPYING_
2024-07-21 03:16:46,872 DEBUG org.apache.hadoop.hdfs.StateChange: persistNewBlock: /tmp/500M._COPYING_ with new block blk_3458315972_2386086055, current total block count is 2
2024-07-21 03:16:47,203 DEBUG org.apache.hadoop.hdfs.StateChange: BLOCK* getAdditionalBlock: /tmp/500M._COPYING_  inodeId 3102566644 for DFSClient_NONMAPREDUCE_1503873289_1
2024-07-21 03:16:47,210 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.addBlock: /tmp/500M._COPYING_ with blk_3458315978_2386086061 block is added to the in-memory file system
2024-07-21 03:16:47,210 INFO org.apache.hadoop.hdfs.StateChange: BLOCK* allocate blk_3458315978_2386086061, replicas=10.104.3.147:9866, 10.104.1.167:9866, 10.104.2.14:9866 for /tmp/500M._COPYING_
2024-07-21 03:16:47,210 DEBUG org.apache.hadoop.hdfs.StateChange: persistNewBlock: /tmp/500M._COPYING_ with new block blk_3458315978_2386086061, current total block count is 3
2024-07-21 03:16:47,703 DEBUG org.apache.hadoop.hdfs.StateChange: BLOCK* getAdditionalBlock: /tmp/500M._COPYING_  inodeId 3102566644 for DFSClient_NONMAPREDUCE_1503873289_1
2024-07-21 03:16:47,706 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.addBlock: /tmp/500M._COPYING_ with blk_3458315988_2386086071 block is added to the in-memory file system
2024-07-21 03:16:47,706 INFO org.apache.hadoop.hdfs.StateChange: BLOCK* allocate blk_3458315988_2386086071, replicas=10.104.8.162:9866, 10.104.1.171:9866, 10.104.1.37:9866 for /tmp/500M._COPYING_
2024-07-21 03:16:47,706 DEBUG org.apache.hadoop.hdfs.StateChange: persistNewBlock: /tmp/500M._COPYING_ with new block blk_3458315988_2386086071, current total block count is 4
2024-07-21 03:16:47,966 DEBUG org.apache.hadoop.hdfs.StateChange: *DIR* NameNode.create: file /tmp/500M._COPYING_ for DFSClient_NONMAPREDUCE_503911796_1 at 10.104.5.12
2024-07-21 03:16:47,967 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* NameSystem.startFile: src=/tmp/500M._COPYING_, holder=DFSClient_NONMAPREDUCE_503911796_1, clientMachine=10.104.5.12, createParent=true, replication=3, createFlag=[CREATE, OVERWRITE], blockSize=134217728, supportedVersions=[CryptoProtocolVersion{description='Encryption zones', version=2, unknownValue=null}]
2024-07-21 03:16:47,967 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.delete: /tmp/500M._COPYING_
2024-07-21 03:16:47,967 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.unprotectedDelete: /tmp/500M._COPYING_ is removed
2024-07-21 03:16:47,967 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* NameSystem.startFile: added /tmp/500M._COPYING_ inode 3102566705 DFSClient_NONMAPREDUCE_503911796_1
2024-07-21 03:16:47,969 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* NameSystem.completeFile: /tmp/500M._COPYING_ for DFSClient_NONMAPREDUCE_1503873289_1
2024-07-21 03:16:47,969 INFO org.apache.hadoop.ipc.Server: IPC Server handler 22 on 8020, call Call#11 Retry#0 org.apache.hadoop.hdfs.protocol.ClientProtocol.complete from 10.104.7.155:57106: java.io.FileNotFoundException: File does not exist: /tmp/500M._COPYING_ (inode 3102566644) Holder DFSClient_NONMAPREDUCE_1503873289_1 does not have any open files.
2024-07-21 03:16:47,984 DEBUG org.apache.hadoop.hdfs.StateChange: *DIR* Namenode.delete: src=/tmp/500M._COPYING_, recursive=true
2024-07-21 03:16:47,984 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* NameSystem.delete: /tmp/500M._COPYING_
2024-07-21 03:16:47,984 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.delete: /tmp/500M._COPYING_
2024-07-21 03:16:47,984 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.unprotectedDelete: /tmp/500M._COPYING_ is removed
2024-07-21 03:16:47,984 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* Namesystem.delete: /tmp/500M._COPYING_ is removed
2024-07-21 03:16:48,009 DEBUG org.apache.hadoop.hdfs.StateChange: BLOCK* getAdditionalBlock: /tmp/500M._COPYING_  inodeId 3102566705 for DFSClient_NONMAPREDUCE_503911796_1
2024-07-21 03:16:48,010 INFO org.apache.hadoop.ipc.Server: IPC Server handler 149 on 8020, call Call#6 Retry#0 org.apache.hadoop.hdfs.protocol.ClientProtocol.addBlock from 10.104.5.12:57694: java.io.FileNotFoundException: File does not exist: /tmp/500M._COPYING_ (inode 3102566705) Holder DFSClient_NONMAPREDUCE_503911796_1 does not have any open files.
```

1、客户端 10.104.4.41 创建文件 /tmp/500M._COPYING_ inode 3102566644，添加 node 到 inodeMap 和 fsDirectory 中，绑定租约，开始申请 block

2、客户端 10.104.5.12 创建文件 /tmp/500M._COPYING_ inode 3102566705，删除旧的 node 3102566644，重新生成 node 到 inodeMap 和 fsDirectory 中，绑定租约

3、客户端 10.104.4.41 调用 NameSystem.completeFile 时失败，此时 inode 3102566644 已经不在 inodeMap 中，触发 FileNotFoundException 异常，然后执行 rpc 调用 NameSystem.delete 删除文件 /tmp/500M._COPYING_。

4、客户端 10.104.5.12 申请 block 时失败，此时 inode 3102566705 已经不在 inodeMap 中，触发 FileNotFoundException 异常。


## 相关文档

[HDFS Commands Guide](https://hadoop.apache.org/docs/r3.1.1/hadoop-project-dist/hadoop-hdfs/HDFSCommands.html)

[Rebalance Design](https://issues.apache.org/jira/browse/HADOOP-1652)
