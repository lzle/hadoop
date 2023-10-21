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


切主

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





