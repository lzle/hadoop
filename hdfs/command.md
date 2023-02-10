# HDFS 使用文档

## 目录

* [常用命令](#常用命令)
    * [daemon](#daemon)
    * [dfsadmin](#dfsadmin)
    * [dfs](#dfs)
    * [haadmin](#haadmin)
    * [balancer](#balancer)
* [日志](#日志)
    * [设置日志级别](设置日志级别)
    * [DateNode 心跳超时](#DateNode-心跳超时)
    * [DateNode 注册](#DateNode-注册)
    * [上传文件](#上传文件)
    * [下载文件](#下载文件)
    * [删除文件](#删除文件)
    

## 常用命令

### daemon

NameNode 启动/停止
```shell
hdfs --daemon start namenode
hdfs --daemon stop namenode
hdfs --daemon status namenode
```

DataNode 启动/停止
```shell
hdfs --daemon start datanode
hdfs --daemon stop datanode
hdfs --daemon status datanode
```

支持的操作如下

```shell
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

汇报集群状态

```shell
hdfs dfsadmin -report -live
hdfs dfsadmin -report -dead
```

支持的操作如下

```shell
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
[使用手册](https://hadoop.apache.org/docs/r3.1.1/hadoop-project-dist/hadoop-hdfs/HDFSCommands.html#dfsadmin)

### dfs

1、创建目录
```shell
hdfs dfs -mkdir -p /lzl/test
```

2、从本地上次文件
```shell
hdfs dfs -put a.txt /lzl/test
```

3、从本地上传目录
```shell
hdfs dfs -copyFromLocal localdir /lzl/test

# 两者效果不一样
hdfs dfs -copyFromLocal localdir/* /lzl/test
```

4、上传本地目录并删除
```shell
hdfs dfs -moveFromLocal localdir /lzl/test
```

5、查看文件
```shell
hdfs dfs -cat /lzl/test/a.txt
```

6、下载文件
```shell
hdfs dfs -get /lzl/test/b.txt ./
```

7、下载目录
```shell
# 本地有 test 目录
hdfs dfs -copyToLocal /lzl/test ./
```

8、删除文件/目录
```shell
# -r 递归删除子目录
hdfs dfs -rm -r /lzl/test
```

支持的操作如下

```shell
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

[使用手册](https://hadoop.apache.org/docs/r3.1.1/hadoop-project-dist/hadoop-common/FileSystemShell.html)


### haadmin

查看节点状态
```
hdfs haadmin -getServiceState nn1
```

将 nn1 切换为 Standby 备用节点
```
hdfs haadmin -transitionToStandby --forcemanual nn1
```
把 active 切换到nn1上。
```
hdfs haadmin -failover nn2 nn1
```

支持的操作如下

```shell
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

支持的操作如下

```shell
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

[使用手册](https://hadoop.apache.org/docs/r3.1.1/hadoop-project-dist/hadoop-hdfs/HDFSCommands.html#balancer)

[设计文档](https://issues.apache.org/jira/browse/HADOOP-1652)


## 日志


### 设置日志级别

临时修改日志级别，无需重启

```
namenode
http://bsy-fujian-xiamen-1-172-18-154-201:9870/logLevel

Log Level

Results
Submitted Class Name: org.apache.hadoop.hdfs.StateChange
Log Class: org.apache.commons.logging.impl.Log4JLogger
Effective Level: DEBUG

datanode
http://bsy-fujian-xiamen-1-172-18-154-201:9864/logLevel
Log Level

Results
Submitted Class Name: org.apache.hadoop.hdfs.StateChange
Log Class: org.apache.commons.logging.impl.Log4JLogger
Submitted Level: DEBUG
Setting Level to DEBUG ...
Effective Level: DEBUG
```

### DateNode 心跳超时

NateNode 端日志输出
```
2022-12-02 15:22:04,287 INFO org.apache.hadoop.hdfs.StateChange: BLOCK* removeDeadDatanode: lost heartbeat from 172.18.154.201:9866, removeBlocksFromBlockMap true
2022-12-02 15:22:04,291 INFO org.apache.hadoop.net.NetworkTopology: Removing a node: /default-rack/172.18.154.201:9866
```

### DateNode 注册

NateNode 端日志输出
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

NameNode 端日志输出，移动到回收站
```
2023-02-08 17:46:02,904 DEBUG org.apache.hadoop.hdfs.StateChange: *DIR* NameNode.mkdirs: /user/root/.Trash/Current/lzl/test
2023-02-08 17:46:02,904 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* NameSystem.mkdirs: /user/root/.Trash/Current/lzl/test
2023-02-08 17:46:02,905 INFO org.apache.hadoop.ipc.Server: IPC Server handler 3 on 8020, call Call#6 Retry#0 org.apache.hadoop.hdfs.protocol.ClientProtocol.mkdirs from 172.18.154.201:35966: org.apache.hadoop.security.AccessControlException: Permission denied: user=root, access=EXECUTE, inode="/user":hadoop:supergroup:drwx------
2023-02-08 17:46:29,355 DEBUG org.apache.hadoop.hdfs.StateChange: *DIR* NameNode.mkdirs: /user/hadoop/.Trash/Current/lzl/test
2023-02-08 17:46:29,355 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* NameSystem.mkdirs: /user/hadoop/.Trash/Current/lzl/test
2023-02-08 17:46:29,356 DEBUG org.apache.hadoop.hdfs.StateChange: mkdirs: created directory /user/hadoop/.Trash/Current
2023-02-08 17:46:29,357 DEBUG org.apache.hadoop.hdfs.StateChange: mkdirs: created directory /user/hadoop/.Trash/Current/lzl
2023-02-08 17:46:29,357 DEBUG org.apache.hadoop.hdfs.StateChange: mkdirs: created directory /user/hadoop/.Trash/Current/lzl/test
2023-02-08 17:46:29,357 INFO org.apache.hadoop.hdfs.server.namenode.FSEditLog: Number of transactions: 4 Total time for transactions(ms): 4 Number of transactions batched in Syncs: 0 Number of syncs: 1 SyncTimes(ms): 8 13
2023-02-08 17:46:29,384 DEBUG org.apache.hadoop.hdfs.StateChange: *DIR* NameNode.rename: /lzl/test/a.txt to /user/hadoop/.Trash/Current/lzl/test/a.txt
2023-02-08 17:46:29,385 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* NameSystem.renameTo: with options - /lzl/test/a.txt to /user/hadoop/.Trash/Current/lzl/test/a.txt
2023-02-08 17:46:29,385 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.renameTo: /lzl/test/a.txt to /user/hadoop/.Trash/Current/lzl/test/a.txt
2023-02-08 17:46:29,386 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.unprotectedRenameTo: /lzl/test/a.txt is renamed to /user/hadoop/.Trash/Current/lzl/test/a.txt
```



``` shell
sudo -u flume hdfs debug recoverLease -path  /fucheng.wang/crudeoil.hexun.com_202211220000.3.24.k7_haidene.1669046460213.gz -retries 10
```

