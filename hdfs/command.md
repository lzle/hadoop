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
把 active 切换到nn1上。
```
hdfs haadmin -failover nn2 nn1
```



### 5、日志输出

DateNode 停止
```
2022-12-02 15:22:04,287 INFO org.apache.hadoop.hdfs.StateChange: BLOCK* removeDeadDatanode: lost heartbeat from 172.18.154.201:9866, removeBlocksFromBlockMap true
2022-12-02 15:22:04,291 INFO org.apache.hadoop.net.NetworkTopology: Removing a node: /default-rack/172.18.154.201:9866
```

DateNode 重新加入
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

NameNode 创建文件
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

### 6、设置日志级别

临时修改日志级别

```
http://bsy-fujian-xiamen-1-172-18-154-201:9870/logLevel

Log Level

Results
Submitted Class Name: org.apache.hadoop.hdfs.StateChange
Log Class: org.apache.commons.logging.impl.Log4JLogger
Effective Level: DEBUG
```


``` shell
sudo -u flume hdfs debug recoverLease -path  /fucheng.wang/crudeoil.hexun.com_202211220000.3.24.k7_haidene.1669046460213.gz -retries 10
```

