

```
hadoop jar /opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-3.1.2-tests.jar nnbench -operation create_write -maps 12 -reduces 6 -blockSize 1 -bytesToWrite 0 -numberOFiles 1000 -replicationFactorPerFile 3 -readFileAfterOpen true 
hadoop jar /opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-3.1.2-tests.jar TestDFSIO -write -nrFiles 2000 -size 128MB
```

```
hadoop jar /opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-3.1.2-tests.jar SliveTest -writeSize 1024 -create 100
```

```
hadoop jar /opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-3.1.2-tests.jar SliveTest \
-maps 400 -reduces 200 -ops 250000 -files 100000000 -dirSize 100 -blockSize 134217728,134217728 \
-writeSize 4096,4096 -ls 0 -truncate 0 -append 0 -rename 0 -read 0 -mkdir 0 -delete 0 -replication 3,3 -cleanup true
```

```
hadoop jar /opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-3.1.2-tests.jar SliveTest \
-maps 500 -reduces 10 -ops 200 -files 100000000 -dirSize 50 -blockSize 134217728,134217728 \
-writeSize 40,40 -ls 0 -truncate 0 -append 0 -rename 0 -read 0 -mkdir 0 -delete 0 -replication 3,3 
```
