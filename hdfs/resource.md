# 源码分析


## 目录

* [NameNode](#NameNode)
    * [文件操作](#文件操作)
      * [创建文件](#创建文件)
    * [块操作](#块操作)
      * [创建数据块](#创建数据块)


# NameNode

## 文件操作

接下来主要介绍 Namenode 文件操作的相关实现，包括创建文件、追加写文件、创建新的数据块、放弃数据块以及关闭文件等操作。

### 创建文件

客户端通过调用 ClientProtocol.create() 方法创建一个新的文件，这个调用由 NamenodeRpcServer.create() 方法响应。
create() 方法会调用 FSNamesystem.startFileInt()，startFileInt() 方法会级联调用 FSDirWriteFileOp.startFile() 来创
建一个新的文件。

文件一旦被创建，它对其他客户端是可见的，并且可以被读取。然而，在文件完成或者因为租约到期而明确标记为完成之前，
其他客户端不能删除、重新创建或重命名该文件。

```java
// ClientProtocol.java

/**
 * Create a new file entry in the namespace.
 * <p>
 * This will create an empty file specified by the source path.
 * The path should reflect a full path originated at the root.
 * The name-node does not have a notion of "current" directory for a client.
 * <p>
 * Once created, the file is visible and available for read to other clients.
 * Although, other clients cannot {@link #delete(String, boolean)}, re-create
 * or {@link #rename(String, String)} it until the file is completed
 * or explicitly as a result of lease expiration.
 * <p>
 * Blocks have a maximum size.  Clients that intend to create
 * multi-block files must also use
 * {@link #addBlock}
 */

@AtMostOnce
HdfsFileStatus create(String src, FsPermission masked,
    String clientName, EnumSetWritable<CreateFlag> flag,
    boolean createParent, short replication, long blockSize,
    CryptoProtocolVersion[] supportedVersions, String ecPolicyName)
    throws IOException;
```

主要参数：

* flag 标记位 CREATE|APPEND|OVERWRITE，overwrite 表示文件存在时是否覆盖；
* replication 表示副本数；
* blockSize 表示块的大小；
* createParent 用于指示目标文件的父目录不存在时，是否创建目录。

基本流程如下：
```
1、获取全局锁 FSNamesystemLock 和 目录锁 dirLock；

2、判断文件是否存在，如果存在并要覆盖写文件，会执行 FSDirectory.delete() 从文件系统 fsDirectory 和 inodeMap 中删除这个文件，
然后调用 fsn.removeLeasesAndINodes 方法删除租约；

3、在目标文件路径上创建一个新的 Node，添加到 fsDirectory 和 inodeMap 中，在租约管理器中添加租约。
```

NamenodeRpcServer.create() 方法：

``` java
@Override // ClientProtocol
public HdfsFileStatus create(String src, FsPermission masked,
    String clientName, EnumSetWritable<CreateFlag> flag,
    boolean createParent, short replication, long blockSize,
    CryptoProtocolVersion[] supportedVersions, String ecPolicyName)
    throws IOException {
  checkNNStartup();
  String clientMachine = getClientMachine();
  if (stateChangeLog.isDebugEnabled()) {
    stateChangeLog.debug("*DIR* NameNode.create: file "
        +src+" for "+clientName+" at "+clientMachine);
  }
  if (!checkPathLength(src)) {
    throw new IOException("create: Pathname too long.  Limit "
        + MAX_PATH_LENGTH + " characters, " + MAX_PATH_DEPTH + " levels.");
  }
  namesystem.checkOperation(OperationCategory.WRITE);
  CacheEntryWithPayload cacheEntry = RetryCache.waitForCompletion(retryCache, null);
  if (cacheEntry != null && cacheEntry.isSuccess()) {
    return (HdfsFileStatus) cacheEntry.getPayload();
  }

  HdfsFileStatus status = null;
  try {
    PermissionStatus perm = new PermissionStatus(getRemoteUser()
        .getShortUserName(), null, masked);
    status = namesystem.startFile(src, perm, clientName, clientMachine,
        flag.get(), createParent, replication, blockSize, supportedVersions,
        ecPolicyName, cacheEntry != null);
  } finally {
    RetryCache.setState(cacheEntry, status != null, status);
  }

  metrics.incrFilesCreated();
  metrics.incrCreateFileOps();
  return status;
}
```

FSNamesystem.startFileInt 方法：

```java
/**
  * Create a new file entry in the namespace.
  * 
  * For description of parameters and exceptions thrown see
  * {@link ClientProtocol#create}, except it returns valid file status upon
  * success
  */
HdfsFileStatus startFile(String src, PermissionStatus permissions,
    String holder, String clientMachine, EnumSet<CreateFlag> flag,
    boolean createParent, short replication, long blockSize,
    CryptoProtocolVersion[] supportedVersions, String ecPolicyName,
    boolean logRetryCache) throws IOException {

  HdfsFileStatus status;
  try {
    status = startFileInt(src, permissions, holder, clientMachine, flag,
        createParent, replication, blockSize, supportedVersions, ecPolicyName,
        logRetryCache);
  } catch (AccessControlException e) {
    logAuditEvent(false, "create", src);
    throw e;
  }
  logAuditEvent(true, "create", src, status);
  return status;
}

private HdfsFileStatus startFileInt(String src,
    PermissionStatus permissions, String holder, String clientMachine,
    EnumSet<CreateFlag> flag, boolean createParent, short replication,
    long blockSize, CryptoProtocolVersion[] supportedVersions,
    String ecPolicyName, boolean logRetryCache) throws IOException {
  if (NameNode.stateChangeLog.isDebugEnabled()) {
    StringBuilder builder = new StringBuilder();
    builder.append("DIR* NameSystem.startFile: src=").append(src)
        .append(", holder=").append(holder)
        .append(", clientMachine=").append(clientMachine)
        .append(", createParent=").append(createParent)
        .append(", replication=").append(replication)
        .append(", createFlag=").append(flag)
        .append(", blockSize=").append(blockSize)
        .append(", supportedVersions=")
        .append(Arrays.toString(supportedVersions));
    NameNode.stateChangeLog.debug(builder.toString());
  }
  ...
  INodesInPath iip = null;
  boolean skipSync = true; // until we do something that might create edits
  HdfsFileStatus stat = null;
  BlocksMapUpdateInfo toRemoveBlocks = null;

  checkOperation(OperationCategory.WRITE);
  final FSPermissionChecker pc = getPermissionChecker();
  // 获取全局锁
  writeLock();
  try {
    checkOperation(OperationCategory.WRITE);
    checkNameNodeSafeMode("Cannot create file" + src);

    iip = FSDirWriteFileOp.resolvePathForStartFile(
        dir, pc, src, flag, createParent);
    ...
    skipSync = false; // following might generate edits
    toRemoveBlocks = new BlocksMapUpdateInfo();
    // 获取目录锁
    dir.writeLock();
    try {
      stat = FSDirWriteFileOp.startFile(this, iip, permissions, holder,
          clientMachine, flag, createParent, replication, blockSize, feInfo,
          toRemoveBlocks, shouldReplicate, ecPolicyName, logRetryCache);
    } catch (IOException e) {
      skipSync = e instanceof StandbyException;
      throw e;
    } finally {
      // 释放目录锁
      dir.writeUnlock();
    }
  } finally {
    // 释放全局锁
    writeUnlock("create");
    // There might be transactions logged while trying to recover the lease.
    // They need to be sync'ed even when an exception was thrown.
    if (!skipSync) {
      getEditLog().logSync();
      if (toRemoveBlocks != null) {
        removeBlocks(toRemoveBlocks);
        toRemoveBlocks.clear();
      }
    }
  }

  return stat;
}
```

FSDirWriteFileOp.startFile 方法：

```java
static HdfsFileStatus startFile(
      FSNamesystem fsn, INodesInPath iip,
      PermissionStatus permissions, String holder, String clientMachine,
      EnumSet<CreateFlag> flag, boolean createParent,
      short replication, long blockSize,
      FileEncryptionInfo feInfo, INode.BlocksMapUpdateInfo toRemoveBlocks,
      boolean shouldReplicate, String ecPolicyName, boolean logRetryEntry)
      throws IOException {
    assert fsn.hasWriteLock();
    boolean overwrite = flag.contains(CreateFlag.OVERWRITE);
    boolean isLazyPersist = flag.contains(CreateFlag.LAZY_PERSIST);

    final String src = iip.getPath();
    FSDirectory fsd = fsn.getFSDirectory();

    if (iip.getLastINode() != null) {
      //  如果文件存在并覆盖，则首先删除这个文件、文件对应的数据块以及租约
      if (overwrite) {
        List<INode> toRemoveINodes = new ChunkedArrayList<>();
        List<Long> toRemoveUCFiles = new ChunkedArrayList<>();
        // 对文件进行删除，ret 删除文件的个数，toRemoveBlocks 待删除的block
        long ret = FSDirDeleteOp.delete(fsd, iip, toRemoveBlocks,
                                        toRemoveINodes, toRemoveUCFiles, now());
        if (ret >= 0) {
          iip = INodesInPath.replace(iip, iip.length() - 1, null);
          FSDirDeleteOp.incrDeletedFileCount(ret);
          fsn.removeLeasesAndINodes(toRemoveUCFiles, toRemoveINodes, true);
        }
      } else {
        // If lease soft limit time is expired, recover the lease
        fsn.recoverLeaseInternal(FSNamesystem.RecoverLeaseOp.CREATE_FILE, iip,
                                 src, holder, clientMachine, false);
        throw new FileAlreadyExistsException(src + " for client " +
            clientMachine + " already exists");
      }
    }
    fsn.checkFsObjectLimit();
    INodeFile newNode = null;
    INodesInPath parent =
        FSDirMkdirOp.createAncestorDirectories(fsd, iip, permissions);
    if (parent != null) {
      iip = addFile(fsd, parent, iip.getLastLocalName(), permissions,
          replication, blockSize, holder, clientMachine, shouldReplicate,
          ecPolicyName);
      // 生成 node，添加 node 到 inodeMap 和 fsDirectory 中
      newNode = iip != null ? iip.getLastINode().asFile() : null;
    }
    if (newNode == null) {
      throw new IOException("Unable to add " + src +  " to namespace");
    }
    // 添加租约，holder = DFSClient_NONMAPREDUCE_264085454_193
    fsn.leaseManager.addLease(
        newNode.getFileUnderConstructionFeature().getClientName(),
        newNode.getId());
    if (feInfo != null) {
      FSDirEncryptionZoneOp.setFileEncryptionInfo(fsd, iip, feInfo,
          XAttrSetFlag.CREATE);
    }
    setNewINodeStoragePolicy(fsd.getBlockManager(), iip, isLazyPersist);
    // 在 editlog 中记录这个操作
    fsd.getEditLog().logOpenFile(src, newNode, overwrite, logRetryEntry);
    if (NameNode.stateChangeLog.isDebugEnabled()) {
      NameNode.stateChangeLog.debug("DIR* NameSystem.startFile: added " +
          src + " inode " + newNode.getId() + " " + holder);
    }
    return FSDirStatAndListingOp.getFileInfo(fsd, iip, false, false);
}
```

注意：不支持两个客户端并发上传同一个文件，会抛出异常 `java.io.FileNotFoundException`。


## 块操作

### 创建数据块

成功创建 INode 对象后，DFSClient 会调用 ClientProtocol.addBlock()请求分配新的数据块，
Namenode 会调用 FSNamesystem.getAdditionalBlock()方法响应分配请求并返回新申请的数据块，
以及存储这个数据块副本的 Datanode 信息。

```java
LocatedBlock addBlock(String src, String clientName,
    ExtendedBlock previous, DatanodeInfo[] excludeNodes, long fileId,
    String[] favoredNodes, EnumSet<AddBlockFlag> addBlockFlags)
    throws IOException;
```

具体实现流程在 getAdditionalBlock() 方法中，主要包括下面三部分：

```
1、FSDirWriteFileOp.validateAddBlock 检查文件状态，是否发生请求重传、异常等操作，
返回实例 ValidateAddBlockResult，包含要申请 block 的信息；

2、FSDirWriteFileOp.chooseTargetForNewBlock 分配数据节点；

3、FSDirWriteFileOp.storeAllocatedBlock 完成添加一个新的数据块，这个操作会进行加锁，
并且会再次执行 analyzeFileState 方法进行检查。
```

代码

```java
LocatedBlock getAdditionalBlock(
      String src, long fileId, String clientName, ExtendedBlock previous,
      DatanodeInfo[] excludedNodes, String[] favoredNodes,
      EnumSet<AddBlockFlag> flags) throws IOException {
    final String operationName = "getAdditionalBlock";
    NameNode.stateChangeLog.debug("BLOCK* getAdditionalBlock: {}  inodeId {}" +
        " for {}", src, fileId, clientName);

    LocatedBlock[] onRetryBlock = new LocatedBlock[1];
    FSDirWriteFileOp.ValidateAddBlockResult r;
    checkOperation(OperationCategory.READ);
    final FSPermissionChecker pc = getPermissionChecker();
    readLock();
    try {
      checkOperation(OperationCategory.READ);
      // 第一部分 在读取锁定的文件状态下分析，以确定客户端是否可以添加新的数据块
      r = FSDirWriteFileOp.validateAddBlock(this, pc, src, fileId, clientName,
                                            previous, onRetryBlock);
    } finally {
      readUnlock(operationName);
    }

    if (r == null) {
      assert onRetryBlock[0] != null : "Retry block is null";
      // This is a retry. Just return the last block.
      return onRetryBlock[0];
    }
    // 分配数据节点
    DatanodeStorageInfo[] targets = FSDirWriteFileOp.chooseTargetForNewBlock(
        blockManager, src, excludedNodes, favoredNodes, flags, r);

    checkOperation(OperationCategory.WRITE);
    writeLock();
    LocatedBlock lb;
    try {
      checkOperation(OperationCategory.WRITE);
      //
      lb = FSDirWriteFileOp.storeAllocatedBlock(
          this, src, fileId, clientName, previous, targets);
    } finally {
      writeUnlock(operationName);
    }
    getEditLog().logSync();
    return lb;
}
```


#### 1、分析状态——analyzeFileState()

validateAddBlock 主要功能在于 analyzeFileState()方法，analyzeFileState首先进行一系列判断操作，判断是否有写操作权限，
判断 Namenode 是否处于安全模式中，检查文件系统中保存的对象是否太多，检查文件的租约。然后 analyzeFileState() 会将 Client 通过 ClientProtocol.addBlock() 方法汇报
的最后一个数据块 previousBlock 与 Namenode 内存中记录的文件最后一个数据块 lastBlockInFile 进行比较。

```
1、previousBlock、lastBlockInFile 都为null，文件生成第一个 block，这种情况什么都不需要做。

2、如果 previousBlock==null，也就是 addBlock()方法并未携带文件最后一个数据块的信息。
  这种情况可能是 Client 调用 ClientProtocol.append()方法申请追加写文件，而文件的最后一个数据块正好写满，
  Client 就会调用 addBlock()方法申请新的数据块。这时方法无须执行任何操作。

3、如果 previousBlock 信息与 penultimateBlock 信息匹配，penultimateBlock 是 Namenode记录的文件倒数第二个数据块的信息。
  这种情况是 Namenode 已经成功地为 Client 分配了数据块，但是响应信息并未送回 Client，所以 Client 重发了请求。
  对于这种情况，由于 Namenode 已经成功地分配了数据块，并且 Client 没有向新分配的数据块写入任何数据，
  所以 analyzeFileState()方法会将分配的数据块保存至 onRetryBlock 参数中，
  getAdditionalBlock()方法可以直接将 onRetryBlock 中保存的数据块再次返回给 Client，而无须构造新的数据块。
  
4、previousBlock 信息与 lastBlockInFile 信息不匹配，这是异常的情况，不应该出现，直接抛出异常。
```

代码

```java
  private static FileState analyzeFileState(
      FSNamesystem fsn, INodesInPath iip, long fileId, String clientName,
      ExtendedBlock previous, LocatedBlock[] onRetryBlock)
      throws IOException {
    assert fsn.hasReadLock();
    String src = iip.getPath();
    checkBlock(fsn, previous);
    onRetryBlock[0] = null;
    fsn.checkNameNodeSafeMode("Cannot add block to " + src);

    // have we exceeded the configured limit of fs objects.
    fsn.checkFsObjectLimit();

    Block previousBlock = ExtendedBlock.getLocalBlock(previous);
    final INodeFile file = fsn.checkLease(iip, clientName, fileId);
    BlockInfo lastBlockInFile = file.getLastBlock();
    // 如果是文件第一次申请block，previousBlock和lastBlockInFile都为null
    if (!Block.matchingIdAndGenStamp(previousBlock, lastBlockInFile)) {
      BlockInfo penultimateBlock = file.getPenultimateBlock();
      if (previous == null &&
          lastBlockInFile != null &&
          lastBlockInFile.getNumBytes() >= file.getPreferredBlockSize() &&
          lastBlockInFile.isComplete()) {
        // Case 1
        if (NameNode.stateChangeLog.isDebugEnabled()) {
           NameNode.stateChangeLog.debug(
               "BLOCK* NameSystem.allocateBlock: handling block allocation" +
               " writing to a file with a complete previous block: src=" +
               src + " lastBlock=" + lastBlockInFile);
        }
      } else if (Block.matchingIdAndGenStamp(penultimateBlock, previousBlock)) {
        if (lastBlockInFile.getNumBytes() != 0) {
          throw new IOException(
              "Request looked like a retry to allocate block " +
              lastBlockInFile + " but it already contains " +
              lastBlockInFile.getNumBytes() + " bytes");
        }

        // Case 2
        // Return the last block.
        NameNode.stateChangeLog.info("BLOCK* allocateBlock: caught retry for " +
            "allocation of a new block in " + src + ". Returning previously" +
            " allocated block " + lastBlockInFile);
        long offset = file.computeFileSize();
        BlockUnderConstructionFeature uc =
            lastBlockInFile.getUnderConstructionFeature();
        onRetryBlock[0] = makeLocatedBlock(fsn, lastBlockInFile,
            uc.getExpectedStorageLocations(), offset);
        return new FileState(file, src, iip);
      } else {
        // Case 3
        throw new IOException("Cannot allocate block in " + src + ": " +
            "passed 'previous' block " + previous + " does not match actual " +
            "last block in file " + lastBlockInFile);
      }
    }
    return new FileState(file, src, iip);
  }
```

**2、分配数据节点——chooseTarget4NewBlock()**

略过

**3、提交上一个数据块——commitOrCompleteLastBlock()**

再执行提交上一个数据块操作之前，会再次执行 analyzeFileState 方法对文件状态进行分析，主要为了防止失败重试后的并发操作，
这个操作会进行加锁，所以不会出现两个线程同时申请覆盖的问题。

commitOrCompleteLastBlock 执行逻辑如下：

```
1、执行 commitBlock 方法，讲 block 状态改为 BlockUCState.COMMITTED。

2、执行 convertToCompleteBlock 方法，将 BlockInfoUnderConstruction 对象转换为普通的 BlockInfo 对象，也就是隐式地将
BlockInfo 的状态变成了 COMPLETED，因为 BlockInfo.getBlockUCState()方法是始终返回 COMPLETED 状态的。
```

代码

```java
public boolean commitOrCompleteLastBlock(BlockCollection bc,
      Block commitBlock, INodesInPath iip) throws IOException {
    if(commitBlock == null)
      return false; // not committing, this is a block allocation retry
    BlockInfo lastBlock = bc.getLastBlock();
    if(lastBlock == null)
      return false; // no blocks in file yet
    if(lastBlock.isComplete())
      return false; // already completed (e.g. by syncBlock)
    if(lastBlock.isUnderRecovery()) {
      throw new IOException("Commit or complete block " + commitBlock +
          ", whereas it is under recovery.");
    }
    
    final boolean committed = commitBlock(lastBlock, commitBlock);
    if (committed && lastBlock.isStriped()) {
      // update scheduled size for DatanodeStorages that do not store any
      // internal blocks
      lastBlock.getUnderConstructionFeature()
          .updateStorageScheduledSize((BlockInfoStriped) lastBlock);
    }

    // Count replicas on decommissioning nodes, as these will not be
    // decommissioned unless recovery/completing last block has finished
    NumberReplicas numReplicas = countNodes(lastBlock);
    int numUsableReplicas = numReplicas.liveReplicas() +
        numReplicas.decommissioning() +
        numReplicas.liveEnteringMaintenanceReplicas();

    if (hasMinStorage(lastBlock, numUsableReplicas)) {
      if (committed) {
        addExpectedReplicasToPending(lastBlock);
      }
      completeBlock(lastBlock, iip, false);
    } else if (pendingRecoveryBlocks.isUnderRecovery(lastBlock)) {
      // We've just finished recovery for this block, complete
      // the block forcibly disregarding number of replicas.
      // This is to ignore minReplication, the block will be closed
      // and then replicated out.
      completeBlock(lastBlock, iip, true);
      updateNeededReconstructions(lastBlock, 1, 0);
    }
    return committed;
}
```

**4、添加一个新的数据块**

完成了上述所有操作之后，getAdditionalBlock()方法就可以进行分配新的数据块操作了。
getAdditionalBlock()首先调用 createNewBlock()创建一个 Block 对象，并赋予一个新的时间戳。
然后调用 saveAllocatedBlock()方法将 Block 对象转换为一个 BlockInfoUnderConstruction 对象，
放入 INode.blocks 字段以及 BlockManager.blocksMap 字段中，最后调用 persistNewBlock()方法将操作记录在 editlog 中。
完成了添加新的数据块操作之后，getAdditionalBlock()方法会调用 makeLocatedBlock()方法将新添加的数据块，
以及分配的保存这个数据块副本的数据节点列表通过一个 LocatedBlock 对象返回给 Client。

```java
static LocatedBlock storeAllocatedBlock(FSNamesystem fsn, String src,
      long fileId, String clientName, ExtendedBlock previous,
      DatanodeStorageInfo[] targets) throws IOException {
    
    ......
    
    // commit the last block and complete it if it has minimum replicas
    fsn.commitOrCompleteLastBlock(pendingFile, fileState.iip,
                                  ExtendedBlock.getLocalBlock(previous));

    // allocate new block, record block locations in INode.
    final BlockType blockType = pendingFile.getBlockType();
    // allocate new block, record block locations in INode.
    Block newBlock = fsn.createNewBlock(blockType);
    INodesInPath inodesInPath = INodesInPath.fromINode(pendingFile);
    saveAllocatedBlock(fsn, src, inodesInPath, newBlock, targets, blockType);

    persistNewBlock(fsn, src, pendingFile);
    offset = pendingFile.computeFileSize();

    // Return located block
    return makeLocatedBlock(fsn, fsn.getStoredBlock(newBlock), targets, offset);
}
```












