# 问题追踪

## 目录

* [NameNode 频繁切主](#NameNode-频繁切主)
    * [HealthMonitor 检查超时](#HealthMonitor-检查超时)
    * [ZooKeeper 会话超时](#ZooKeeper-会话超时)
* [Block not COMPLETE](#Block-not-COMPLETE)
* [文件未正常关闭](#文件未正常关闭)

## NameNode 频繁切主

目前 NameNode 使用了 HA 的部署模式，但系统会经常出现 HA 的自动切换（NameNode 节点其实正常）。 经过调研发现可能的原因如下：

1、ZKFC 服务的 HealthMonitor 线程 check 本地 NameNode 的 RPC 端口时超时，导致 HealthMonitor 认为 NameNode 挂掉。

2、ZKFC 服务连接 ZooKeeper 上的 session timeout，导致丢掉当前持有的 active 锁（temp节点），引起自动切换。

### HealthMonitor 检查超时

线上石家庄集群发生了主备切换，排查 ZKFC 服务日志，获取到异常信息如下：

```
2023-10-20 02:48:41,616 WARN org.apache.hadoop.ha.HealthMonitor: Transport-level exception trying to monitor health of NameNode at dx-lt-yd-hebei-shijiazhuang-10-10-103-1-34/10.103.1.34:8020
java.net.SocketTimeoutException: Call From dx-lt-yd-hebei-shijiazhuang-10-10-103-1-34/10.103.1.34 to dx-lt-yd-hebei-shijiazhuang-10-10-103-1-34:8020 failed on socket timeout exception: java.net.SocketTimeoutException: 45000 millis timeout while waiting for channel to be ready for read. ch : java.nio.channels.SocketChannel[connected local=/10.103.1.34:45348 remote=dx-lt-yd-hebei-shijiazhuang-10-10-103-1-34/10.103.1.34:8020]; For more details see:  http://wiki.apache.org/hadoop/SocketTimeout
        at sun.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
        at sun.reflect.NativeConstructorAccessorImpl.newInstance(NativeConstructorAccessorImpl.java:62)
        at sun.reflect.DelegatingConstructorAccessorImpl.newInstance(DelegatingConstructorAccessorImpl.java:45)
        at java.lang.reflect.Constructor.newInstance(Constructor.java:423)
        at org.apache.hadoop.net.NetUtils.wrapWithMessage(NetUtils.java:831)
        at org.apache.hadoop.net.NetUtils.wrapException(NetUtils.java:775)
        at org.apache.hadoop.ipc.Client.getRpcResponse(Client.java:1515)
        at org.apache.hadoop.ipc.Client.call(Client.java:1457)
        at org.apache.hadoop.ipc.Client.call(Client.java:1367)
        at org.apache.hadoop.ipc.ProtobufRpcEngine$Invoker.invoke(ProtobufRpcEngine.java:228)
        at org.apache.hadoop.ipc.ProtobufRpcEngine$Invoker.invoke(ProtobufRpcEngine.java:116)
        at com.sun.proxy.$Proxy9.getServiceStatus(Unknown Source)
        at org.apache.hadoop.ha.protocolPB.HAServiceProtocolClientSideTranslatorPB.getServiceStatus(HAServiceProtocolClientSideTranslatorPB.java:122)
        at org.apache.hadoop.ha.HealthMonitor.doHealthChecks(HealthMonitor.java:202)
        at org.apache.hadoop.ha.HealthMonitor.access$600(HealthMonitor.java:49)
        at org.apache.hadoop.ha.HealthMonitor$MonitorDaemon.run(HealthMonitor.java:296)
Caused by: java.net.SocketTimeoutException: 45000 millis timeout while waiting for channel to be ready for read. ch : java.nio.channels.SocketChannel[connected local=/10.103.1.34:45348 remote=dx-lt-yd-hebei-shijiazhuang-10-10-103-1-34/10.103.1.34:8020]
        at org.apache.hadoop.net.SocketIOWithTimeout.doIO(SocketIOWithTimeout.java:164)
        at org.apache.hadoop.net.SocketInputStream.read(SocketInputStream.java:161)
        at org.apache.hadoop.net.SocketInputStream.read(SocketInputStream.java:131)
        at java.io.FilterInputStream.read(FilterInputStream.java:133)
        at java.io.BufferedInputStream.fill(BufferedInputStream.java:246)
        at java.io.BufferedInputStream.read(BufferedInputStream.java:265)
        at java.io.FilterInputStream.read(FilterInputStream.java:83)
        at java.io.FilterInputStream.read(FilterInputStream.java:83)
        at org.apache.hadoop.ipc.Client$Connection$PingInputStream.read(Client.java:557)
        at java.io.DataInputStream.readInt(DataInputStream.java:387)
        at org.apache.hadoop.ipc.Client$IpcStreams.readResponse(Client.java:1816)
        at org.apache.hadoop.ipc.Client$Connection.receiveRpcResponse(Client.java:1173)
        at org.apache.hadoop.ipc.Client$Connection.run(Client.java:1069)
2023-10-20 02:48:41,928 INFO org.apache.hadoop.ha.HealthMonitor: Entering state SERVICE_NOT_RESPONDING
2023-10-20 02:48:41,928 INFO org.apache.hadoop.ha.ZKFailoverController: Local service NameNode at dx-lt-yd-hebei-shijiazhuang-10-10-103-1-34/10.103.1.34:8020 entered state: SERVICE_NOT_RESPONDING
2023-10-20 02:48:44,083 INFO org.apache.hadoop.hdfs.tools.DFSZKFailoverController: -- Local NN thread dump --
```

从日志中可以看出 HealthMonitor 线程检查 NameNode 状态时，发生超时 45s，超时时间的配置：

```
<property>
<name>ha.health-monitor.rpc-timeout.ms</name>
<value>45000</value>
<final>false</final>
<source>core-default.xml</source>
</property>
```

接下来排查 NameNode 的日志，可以看到全局锁 FSWirteLock 占用了 46886ms 的时间，期间不处理任何操作，这是导致切主的主要原因。

```
2023-10-20 02:47:55,315 INFO org.apache.hadoop.hdfs.server.namenode.FSNamesystem: Roll Edit Log from 10.103.2.160
2023-10-20 02:47:55,315 INFO org.apache.hadoop.hdfs.server.namenode.FSEditLog: Rolling edit logs
2023-10-20 02:47:55,315 INFO org.apache.hadoop.hdfs.server.namenode.FSEditLog: Ending log segment 13072603954, 13072632862
2023-10-20 02:47:55,720 INFO org.apache.hadoop.hdfs.server.namenode.FSEditLog: Number of transactions: 28950 Total time for transactions(ms): 273 Number of transactions batched in Syncs: 6936 Number of syncs: 22014 SyncTimes(ms): 7214 11560
2023-10-20 02:47:55,740 INFO org.apache.hadoop.hdfs.server.namenode.FileJournalManager: Finalizing edits file /opt/hadoop/data/dfs/nn/current/edits_inprogress_0000000013072603954 -> /opt/hadoop/data/dfs/nn/current/edits_0000000013072603954-0000000013072632903
2023-10-20 02:47:55,740 INFO org.apache.hadoop.hdfs.server.namenode.FSEditLog: Starting log segment at 13072632904
2023-10-20 02:48:42,048 INFO org.apache.hadoop.hdfs.server.common.Util: Combined time for file download and fsync to all disks took 46.75s. The file download took 46.75s at 150924.45 KB/s. Synchronous (fsync) write to disk of /opt/hadoop/data/dfs/nn/current/fsimage.ckpt_0000000013072585031 took 0.00s.
2023-10-20 02:48:42,056 INFO org.apache.hadoop.hdfs.server.namenode.TransferFsImage: Downloaded file fsimage.ckpt_0000000013072585031 size 7225055493 bytes.
2023-10-20 02:48:42,130 INFO org.apache.hadoop.hdfs.server.namenode.NNStorageRetentionManager: Going to retain 2 images with txid >= 13072384197
2023-10-20 02:48:42,130 INFO org.apache.hadoop.hdfs.server.namenode.NNStorageRetentionManager: Purging old image FSImageFile(file=/opt/hadoop/data/dfs/nn/current/fsimage_0000000013072183073, cpktTxId=0000000013072183073)
2023-10-20 02:48:42,258 INFO org.apache.hadoop.hdfs.server.namenode.FSNamesystem: FSNamesystem write lock held for 46886 ms via java.lang.Thread.getStackTrace(Thread.java:1559)
org.apache.hadoop.util.StringUtils.getStackTrace(StringUtils.java:1032)
org.apache.hadoop.hdfs.server.namenode.FSNamesystemLock.writeUnlock(FSNamesystemLock.java:273)
org.apache.hadoop.hdfs.server.namenode.FSNamesystemLock.writeUnlock(FSNamesystemLock.java:235)
org.apache.hadoop.hdfs.server.namenode.FSNamesystem.writeUnlock(FSNamesystem.java:1617)
org.apache.hadoop.hdfs.server.namenode.FSNamesystem.rollEditLog(FSNamesystem.java:4663)
org.apache.hadoop.hdfs.server.namenode.NameNodeRpcServer.rollEditLog(NameNodeRpcServer.java:1292)
org.apache.hadoop.hdfs.protocolPB.NamenodeProtocolServerSideTranslatorPB.rollEditLog(NamenodeProtocolServerSideTranslatorPB.java:146)
org.apache.hadoop.hdfs.protocol.proto.NamenodeProtocolProtos$NamenodeProtocolService$2.callBlockingMethod(NamenodeProtocolProtos.java:12974)
org.apache.hadoop.ipc.ProtobufRpcEngine$Server$ProtoBufRpcInvoker.call(ProtobufRpcEngine.java:523)
org.apache.hadoop.ipc.RPC$Server.call(RPC.java:991)
org.apache.hadoop.ipc.Server$RpcCall.run(Server.java:872)
org.apache.hadoop.ipc.Server$RpcCall.run(Server.java:818)
java.security.AccessController.doPrivileged(Native Method)
javax.security.auth.Subject.doAs(Subject.java:422)
org.apache.hadoop.security.UserGroupInformation.doAs(UserGroupInformation.java:1729)
org.apache.hadoop.ipc.Server$Handler.run(Server.java:2678)
        Number of suppressed write-lock reports: 0
        Longest write-lock held interval: 46886.0
        Total suppressed write-lock held time: 0.0
2023-10-20 02:48:42,282 WARN org.apache.hadoop.ipc.Server: IPC Server handler 95 on 8020, call Call#976852 Retry#0 org.apache.hadoop.hdfs.server.protocol.NamenodeProtocol.rollEditLog from 10.103.2.160:44632: output error
2023-10-20 02:48:42,299 INFO org.apache.hadoop.ipc.Server: IPC Server handler 95 on 8020 caught an exception
```

继续排查是 `NameNodeRpcServer.rollEditLog` 函数占据锁时间太久，函数执行的逻辑是进行 Editlog 的重新生成，中间包含了磁盘和 Journal 服务的调用。

从日志中还可以看到，同时 NameNode 还执行了 Fsimage 下载操作，此操作会占据磁盘 IO，持续时间 46.75s。

造成 `NameNodeRpcServer.rollEditLog` 锁占用时间太久的原因可能是磁盘 IO 太高，导致数据落盘等待，造成函数执行时间长。

可以考虑对 Fsimage 与 Editlog 进行目录分离，消除相互 IO 造成的影响，同时调整 checkpoint 间隔为 120s（默认60s，减少Fsimage检查间隔）。

```
<property>
<name>dfs.namenode.name.dir</name>
<value>/data/1/dfs/nn</value>
</property>

<property>
<name>dfs.namenode.edits.dir</name>
<value>/opt/hadoop/data/dfs/nn</value>
</property>

<property>
<name>dfs.namenode.checkpoint.check.period</name>
<value>120s</value>
</property>
```

### ZooKeeper 会话超时

ZooKeeper failover 的 session 超时设置为 20000ms （默认5000ms）。

```
<property>
<name>ha.zookeeper.session-timeout.ms</name>
<value>20000</value>
<final>false</final>
<source>core-site.xml</source>
</property>
```

## Block not COMPLETE

客户端执行 close 操作时报错。

```
任务报错信息：Caused by: java.io.IOException: Unable to close file because the last blockBP-xxxx:blk_xxxx does not have enough number of replicas.
```

NameNode 服务打开 BlockStateChange DEBUG 级别日志，过滤日志中 Block 信息，从日志中可以看到文件在 close 之前未收到 DataNode 对应 Block 的增量汇报。

```
[root@dx-lt-yd-zhejiang-jinhua-5-10-104-7-25 hadoop-hdfs]# grep blk_3251789645_2194966856 hadoop-cmf-hdfs-NAMENODE-dx-lt-yd-zhejiang-jinhua-5-10-104-7-25.log.out
2023-10-23 19:15:43,760 DEBUG org.apache.hadoop.hdfs.StateChange: DIR* FSDirectory.addBlock: /user/hive/warehouse/cachelog_ads.db/ads_static_nginx_uv_domain_is_abroad_province_type_1h/_temporary/0/_temporary/attempt_202310231907505449250112946481805_0003_m_000127_1762/dt=2023102312/part-00127-cb374881-b86c-4c23-87f6-11c95cae9c82.c000.snappy.parquet with blk_3251789645_2194966856 block is added to the in-memory file system
2023-10-23 19:15:43,760 INFO org.apache.hadoop.hdfs.StateChange: BLOCK* allocate blk_3251789645_2194966856, replicas=10.104.6.156:9866, 10.104.6.133:9866, 10.104.8.22:9866 for /user/hive/warehouse/cachelog_ads.db/ads_static_nginx_uv_domain_is_abroad_province_type_1h/_temporary/0/_temporary/attempt_202310231907505449250112946481805_0003_m_000127_1762/dt=2023102312/part-00127-cb374881-b86c-4c23-87f6-11c95cae9c82.c000.snappy.parquet
2023-10-23 19:15:43,760 DEBUG org.apache.hadoop.hdfs.StateChange: persistNewBlock: /user/hive/warehouse/cachelog_ads.db/ads_static_nginx_uv_domain_is_abroad_province_type_1h/_temporary/0/_temporary/attempt_202310231907505449250112946481805_0003_m_000127_1762/dt=2023102312/part-00127-cb374881-b86c-4c23-87f6-11c95cae9c82.c000.snappy.parquet with new block blk_3251789645_2194966856, current total block count is 1
2023-10-23 19:15:46,838 INFO org.apache.hadoop.hdfs.server.namenode.FSNamesystem: BLOCK* blk_3251789645_2194966856 is COMMITTED but not COMPLETE(numNodes= 0 <  minimum = 1) in file /user/hive/warehouse/cachelog_ads.db/ads_static_nginx_uv_domain_is_abroad_province_type_1h/_temporary/0/_temporary/attempt_202310231907505449250112946481805_0003_m_000127_1762/dt=2023102312/part-00127-cb374881-b86c-4c23-87f6-11c95cae9c82.c000.snappy.parquet
2023-10-23 19:15:47,239 INFO org.apache.hadoop.hdfs.server.namenode.FSNamesystem: BLOCK* blk_3251789645_2194966856 is COMMITTED but not COMPLETE(numNodes= 0 <  minimum = 1) in file /user/hive/warehouse/cachelog_ads.db/ads_static_nginx_uv_domain_is_abroad_province_type_1h/_temporary/0/_temporary/attempt_202310231907505449250112946481805_0003_m_000127_1762/dt=2023102312/part-00127-cb374881-b86c-4c23-87f6-11c95cae9c82.c000.snappy.parquet
2023-10-23 19:15:48,039 INFO org.apache.hadoop.hdfs.server.namenode.FSNamesystem: BLOCK* blk_3251789645_2194966856 is COMMITTED but not COMPLETE(numNodes= 0 <  minimum = 1) in file /user/hive/warehouse/cachelog_ads.db/ads_static_nginx_uv_domain_is_abroad_province_type_1h/_temporary/0/_temporary/attempt_202310231907505449250112946481805_0003_m_000127_1762/dt=2023102312/part-00127-cb374881-b86c-4c23-87f6-11c95cae9c82.c000.snappy.parquet
2023-10-23 19:15:49,640 INFO org.apache.hadoop.hdfs.server.namenode.FSNamesystem: BLOCK* blk_3251789645_2194966856 is COMMITTED but not COMPLETE(numNodes= 0 <  minimum = 1) in file /user/hive/warehouse/cachelog_ads.db/ads_static_nginx_uv_domain_is_abroad_province_type_1h/_temporary/0/_temporary/attempt_202310231907505449250112946481805_0003_m_000127_1762/dt=2023102312/part-00127-cb374881-b86c-4c23-87f6-11c95cae9c82.c000.snappy.parquet
2023-10-23 19:15:52,843 INFO org.apache.hadoop.hdfs.server.namenode.FSNamesystem: BLOCK* blk_3251789645_2194966856 is COMMITTED but not COMPLETE(numNodes= 0 <  minimum = 1) in file /user/hive/warehouse/cachelog_ads.db/ads_static_nginx_uv_domain_is_abroad_province_type_1h/_temporary/0/_temporary/attempt_202310231907505449250112946481805_0003_m_000127_1762/dt=2023102312/part-00127-cb374881-b86c-4c23-87f6-11c95cae9c82.c000.snappy.parquet
2023-10-23 19:15:54,025 DEBUG BlockStateChange: BLOCK* addStoredBlock: 10.104.6.156:9866 is added to blk_3251789645_2194966856 (size=4948)
2023-10-23 19:15:54,025 DEBUG BlockStateChange: BLOCK* block RECEIVED_BLOCK: blk_3251789645_2194966856 is received from 10.104.6.156:9866
2023-10-23 19:15:54,564 DEBUG BlockStateChange: BLOCK* addStoredBlock: 10.104.6.133:9866 is added to blk_3251789645_2194966856 (size=4948)
2023-10-23 19:15:54,564 DEBUG BlockStateChange: BLOCK* block RECEIVED_BLOCK: blk_3251789645_2194966856 is received from 10.104.6.133:9866
2023-10-23 19:16:00,090 DEBUG BlockStateChange: BLOCK* addStoredBlock: 10.104.8.22:9866 is added to blk_3251789645_2194966856 (size=4948)
2023-10-23 19:16:00,090 DEBUG BlockStateChange: BLOCK* block RECEIVED_BLOCK: blk_3251789645_2194966856 is received from 10.104.8.22:9866
```

查看 DataNode 的日志，可以看到 Block 落盘后与 Block 增量汇报之间延迟了 8s 左右，理论上应该立即汇报。

```
[root@dx-lt-yd-zhejiang-jinhua-5-10-104-6-156 hadoop-hdfs]# grep blk_3251789645_2194966856 hadoop-cmf-hdfs-DATANODE-dx-lt-yd-zhejiang-jinhua-5-10-104-6-156.log.out
2023-10-23 19:15:43,751 INFO org.apache.hadoop.hdfs.server.datanode.DataNode: Receiving BP-1182980097-10.104.5.132-1620803717801:blk_3251789645_2194966856 src: /10.104.6.159:56820 dest: /10.104.6.156:9866
2023-10-23 19:15:44,544 DEBUG org.apache.hadoop.hdfs.server.datanode.IncrementalBlockReportManager: call blockReceivedAndDeleted: [DatanodeStorage[DS-f3e3d6d1-8879-4a43-b103-21e5f162530e,DISK,NORMAL][blk_3251789655_2194966866, status: RECEIVING_BLOCK, delHint: null], DatanodeStorage[DS-4556594b-a59e-4bf3-9123-3f5ad0d4c7e1,DISK,NORMAL][blk_3251789645_2194966856, status: RECEIVING_BLOCK, delHint: null]]
2023-10-23 19:15:46,826 INFO org.apache.hadoop.hdfs.server.datanode.DataNode.clienttrace: src: /10.104.6.159:56820, dest: /10.104.6.156:9866, bytes: 4948, op: HDFS_WRITE, cliID: DFSClient_NONMAPREDUCE_565484197_56, offset: 0, srvID: 745584f6-db3e-4ce5-8f6e-4431a04ade9c, blockid: BP-1182980097-10.104.5.132-1620803717801:blk_3251789645_2194966856, duration(ns): 1610281611
2023-10-23 19:15:46,827 INFO org.apache.hadoop.hdfs.server.datanode.DataNode: PacketResponder: BP-1182980097-10.104.5.132-1620803717801:blk_3251789645_2194966856, type=HAS_DOWNSTREAM_IN_PIPELINE, downstreams=2:[10.104.6.133:9866, 10.104.8.22:9866] terminating
2023-10-23 19:15:54,010 DEBUG org.apache.hadoop.hdfs.server.datanode.IncrementalBlockReportManager: call blockReceivedAndDeleted: [DatanodeStorage[DS-71fd0fbe-f8e7-490c-b214-9385868cf3b9,DISK,NORMAL][blk_3251789010_2194966221, status: RECEIVED_BLOCK, delHint: null, blk_3251789821_2194967032, status: RECEIVED_BLOCK, delHint: null, blk_3251790060_2194967271, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-5db93274-987e-4860-aa01-62092ed03340,DISK,NORMAL][blk_3251789854_2194967065, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-a026ced1-64c6-4cce-b7a1-ad874cfcc5b5,DISK,NORMAL][blk_3251789977_2194967188, status: RECEIVED_BLOCK, delHint: null, blk_3251789191_2194966402, status: RECEIVED_BLOCK, delHint: null, blk_3251789519_2194966730, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-f3e3d6d1-8879-4a43-b103-21e5f162530e,DISK,NORMAL][blk_3251789904_2194967115, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-1cb56406-1733-4d08-8555-b92502ca05ce,DISK,NORMAL][blk_3251789163_2194966374, status: RECEIVED_BLOCK, delHint: null, blk_3251789901_2194967112, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-4556594b-a59e-4bf3-9123-3f5ad0d4c7e1,DISK,NORMAL][blk_3251789040_2194966251, status: RECEIVED_BLOCK, delHint: null, blk_3251790079_2194967290, status: RECEIVING_BLOCK, delHint: null, blk_3251789893_2194967104, status: RECEIVING_BLOCK, delHint: null, blk_3251789645_2194966856, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-21c7754d-051d-45e2-8412-5a23cd18fe1f,DISK,NORMAL][blk_3251789889_2194967100, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-6a85ce98-c7d7-4b18-b7fe-701dd05b18f0,DISK,NORMAL][blk_3251790000_2194967211, status: RECEIVING_BLOCK, delHint: null], DatanodeStorage[DS-2d369fc2-3f83-49b4-93ed-bc19ebfb139a,DISK,NORMAL][blk_3251789997_2194967208, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-cc8eebc9-ead8-4001-b095-3291f49bfe19,DISK,NORMAL][blk_3251789844_2194967055, status: RECEIVED_BLOCK, delHint: null, blk_3251790074_2194967285, status: RECEIVING_BLOCK, delHint: null], DatanodeStorage[DS-dc71a8fa-8266-4c88-ab96-6bc78d879385,DISK,NORMAL][blk_3251789852_2194967063, status: RECEIVING_BLOCK, delHint: null, blk_3251790025_2194967236, status: RECEIVING_BLOCK, delHint: null], DatanodeStorage[DS-1cdac639-5297-48f0-a674-76e82c5935f7,DISK,NORMAL][blk_3251789209_2194966420, status: RECEIVED_BLOCK, delHint: null, blk_3251790009_2194967220, status: RECEIVED_BLOCK, delHint: null, blk_3251788971_2194966182, status: RECEIVED_BLOCK, delHint: null, blk_3251789544_2194966755, status: RECEIVED_BLOCK, delHint: null]]
2023-10-23 19:15:54,010 DEBUG org.apache.hadoop.hdfs.server.datanode.IncrementalBlockReportManager: call blockReceivedAndDeleted: [DatanodeStorage[DS-71fd0fbe-f8e7-490c-b214-9385868cf3b9,DISK,NORMAL][blk_3251789010_2194966221, status: RECEIVED_BLOCK, delHint: null, blk_3251789624_2194966835, status: RECEIVED_BLOCK, delHint: null, blk_3251789821_2194967032, status: RECEIVED_BLOCK, delHint: null, blk_3251790060_2194967271, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-5db93274-987e-4860-aa01-62092ed03340,DISK,NORMAL][blk_3251789854_2194967065, status: RECEIVED_BLOCK, delHint: null, blk_3251789670_2194966881, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-f3e3d6d1-8879-4a43-b103-21e5f162530e,DISK,NORMAL][blk_3251789904_2194967115, status: RECEIVED_BLOCK, delHint: null, blk_3251789655_2194966866, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-a026ced1-64c6-4cce-b7a1-ad874cfcc5b5,DISK,NORMAL][blk_3251789977_2194967188, status: RECEIVED_BLOCK, delHint: null, blk_3251789191_2194966402, status: RECEIVED_BLOCK, delHint: null, blk_3251789519_2194966730, status: RECEIVED_BLOCK, delHint: null, blk_3251789741_2194966952, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-1cb56406-1733-4d08-8555-b92502ca05ce,DISK,NORMAL][blk_3251789429_2194966640, status: RECEIVED_BLOCK, delHint: null, blk_3251789661_2194966872, status: RECEIVED_BLOCK, delHint: null, blk_3251789163_2194966374, status: RECEIVED_BLOCK, delHint: null, blk_3251789901_2194967112, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-4556594b-a59e-4bf3-9123-3f5ad0d4c7e1,DISK,NORMAL][blk_3251789040_2194966251, status: RECEIVED_BLOCK, delHint: null, blk_3251790079_2194967290, status: RECEIVING_BLOCK, delHint: null, blk_3251789893_2194967104, status: RECEIVING_BLOCK, delHint: null, blk_3251789645_2194966856, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-21c7754d-051d-45e2-8412-5a23cd18fe1f,DISK,NORMAL][blk_3251789889_2194967100, status: RECEIVED_BLOCK, delHint: null, blk_3251789668_2194966879, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-6a85ce98-c7d7-4b18-b7fe-701dd05b18f0,DISK,NORMAL][blk_3251790000_2194967211, status: RECEIVING_BLOCK, delHint: null, blk_3251789716_2194966927, status: RECEIVED_BLOCK, delHint: null, blk_3251789531_2194966742, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-2d369fc2-3f83-49b4-93ed-bc19ebfb139a,DISK,NORMAL][blk_3251789533_2194966744, status: RECEIVED_BLOCK, delHint: null, blk_3251789764_2194966975, status: RECEIVED_BLOCK, delHint: null, blk_3251789997_2194967208, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-cc8eebc9-ead8-4001-b095-3291f49bfe19,DISK,NORMAL][blk_3251789844_2194967055, status: RECEIVED_BLOCK, delHint: null, blk_3251790074_2194967285, status: RECEIVING_BLOCK, delHint: null, blk_3251789632_2194966843, status: RECEIVED_BLOCK, delHint: null], DatanodeStorage[DS-dc71a8fa-8266-4c88-ab96-6bc78d879385,DISK,NORMAL][blk_3251789623_2194966834, status: RECEIVED_BLOCK, delHint: null, blk_3251789852_2194967063, status: RECEIVING_BLOCK, delHint: null, blk_3251789000_2194966211, status: RECEIVED_BLOCK, delHint: null, blk_3251790025_2194967236, status: RECEIVING_BLOCK, delHint: null], DatanodeStorage[DS-1cdac639-5297-48f0-a674-76e82c5935f7,DISK,NORMAL][blk_3251789809_2194967020, status: RECEIVED_BLOCK, delHint: null, blk_3251789209_2194966420, status: RECEIVED_BLOCK, delHint: null, blk_3251790009_2194967220, status: RECEIVED_BLOCK, delHint: null, blk_3251788971_2194966182, status: RECEIVED_BLOCK, delHint: null, blk_3251789544_2194966755, status: RECEIVED_BLOCK, delHint: null]
```

继续排查发现下面这行日志打印，DataNode 执行 NameNode 的命令消费了 11s 左右，Block 汇报延迟疑似和这个有关。

```
2023-10-23 19:15:54,010 INFO org.apache.hadoop.hdfs.server.datanode.DataNode: Took 11109ms to process 1 commands from NN
```

## 文件未正常关闭

文件未正常关闭，执行 recoverLease

```
[root@dx-lt-yd-zhejiang-jinhua-5-10-104-6-156 hadoop-hdfs]#  sudo -u flume hdfs debug recoverLease -path  /fucheng.wang/crudeoil.hexun.com_202211220000.3.24.k7_haidene.1669046460213.gz -retries 10
```







