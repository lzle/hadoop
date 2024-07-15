# Flume

## 目录

* [编译](#编译)
* [部署](#部署)
* [启动](#启动)
* [安装 lina](#安装-lina)
* [生成测试文件](#生成测试文件)


## 编译

编译 flume-hdfs-sink

```bash
$ cd flume-1.9/flume-ng-sinks/flume-hdfs-sink

$ mvn install -DskipTests -X

$ mvn test -Dtest=TestBucketWriter -X
$ mvn install -Dcheckstyle.skip=true -DskipTests -X
```


## 部署

```bash
$ wget ss.bscstorage.com/breakwang-public/flume-ng.tgz
$ tar -xzf flume-ng.tgz
```

配置文件

```bash
$ cat /root/fucheng.wang/flume/conf/flume-collection-1st.properties

flume-collection-1st.sources =  s_tengine_1
flume-collection-1st.channels = c_tengine_1
flume-collection-1st.sinks = k_tengine_1

####################### To JinHua ########################################

# ======== Sources
############# source: nginx log stream #############

flume-collection-1st.sources.s_tengine_1.interceptors = i1
flume-collection-1st.sources.s_tengine_1.interceptors.i1.type = com.baishanyun.www.DomainInterceptor$Builder
flume-collection-1st.sources.s_tengine_1.interceptors.i1.filePrefixHeader = fileprefix
flume-collection-1st.sources.s_tengine_1.interceptors.i1.intervalHeader = interval
flume-collection-1st.sources.s_tengine_1.interceptors.i1.domainHeader = domain
flume-collection-1st.sources.s_tengine_1.interceptors.i1.sizeHeader = size
flume-collection-1st.sources.s_tengine_1.interceptors.i1.maxDelay = 86400
flume-collection-1st.sources.s_tengine_1.interceptors.i1.setBytesSentToHeader = true
flume-collection-1st.sources.s_tengine_1.interceptors.i1.bytesSentHeaderName = bytesSent

flume-collection-1st.sources.s_tengine_1.type=avro
flume-collection-1st.sources.s_tengine_1.bind=0.0.0.0
flume-collection-1st.sources.s_tengine_1.port=5201
flume-collection-1st.sources.s_tengine_1.threads=150
flume-collection-1st.sources.s_tengine_1.compression-type=deflate
flume-collection-1st.sources.s_tengine_1.compression-level=6
flume-collection-1st.sources.s_tengine_1.channels=c_tengine_1
flume-collection-1st.sources.s_tengine_1.ssl=true
flume-collection-1st.sources.s_tengine_1.keystore=/var/lib/flume-ng/server.jks
flume-collection-1st.sources.s_tengine_1.keystore-type=JKS
flume-collection-1st.sources.s_tengine_1.keystore-password=baishancloud


# ======== Channels

flume-collection-1st.channels.c_tengine_1.type=memory
flume-collection-1st.channels.c_tengine_1.capacity=2000000
flume-collection-1st.channels.c_tengine_1.transactionCapacity=200000
flume-collection-1st.channels.c_tengine_1.byteCapacity=5120000000
flume-collection-1st.channels.c_tengine_1.keep-alive=30

# ======== Sinks

flume-collection-1st.sinks.k_tengine_1.type = hdfs
flume-collection-1st.sinks.k_tengine_1.hdfs.path = /separated_tengine/%{domain}
flume-collection-1st.sinks.k_tengine_1.hdfs.filePrefix = %{fileprefix}.fog.9_haidene
flume-collection-1st.sinks.k_tengine_1.hdfs.maxOpenFiles = 8000
flume-collection-1st.sinks.k_tengine_1.hdfs.rollInterval = 1200
flume-collection-1st.sinks.k_tengine_1.hdfs.closeTries = 5
flume-collection-1st.sinks.k_tengine_1.hdfs.rollSize = 1572864000
flume-collection-1st.sinks.k_tengine_1.hdfs.rollCount = 0
flume-collection-1st.sinks.k_tengine_1.hdfs.fileType = CompressedStream
flume-collection-1st.sinks.k_tengine_1.hdfs.codeC = gzip
flume-collection-1st.sinks.k_tengine_1.hdfs.batchSize = 5000
flume-collection-1st.sinks.k_tengine_1.hdfs.idleTimeout = 60
flume-collection-1st.sinks.k_tengine_1.hdfs.callTimeout = 60000
flume-collection-1st.sinks.k_tengine_1.hdfs.threadsPoolSize = 200
flume-collection-1st.sinks.k_tengine_1.hdfs.rollTimerPoolSize = 4
flume-collection-1st.sinks.k_tengine_1.hdfs.minBlockReplicas = 1
flume-collection-1st.sinks.k_tengine_1.hdfs.useLineCountInSuffix = true
flume-collection-1st.sinks.k_tengine_1.hdfs.lineCountInSuffixTag = l
flume-collection-1st.sinks.k_tengine_1.hdfs.useExtCountInSuffix = true
flume-collection-1st.sinks.k_tengine_1.hdfs.extCountInSuffixTag = t
flume-collection-1st.sinks.k_tengine_1.hdfs.extCountHeaderName = bytesSent
flume-collection-1st.sinks.k_tengine_1.channel = c_tengine_1
flume-collection-1st.sinks.k_tengine_1.hdfs.appendEmptyGzip = true
```

替换 jar 包

```bash
$  cd /root/fucheng.wang/flume/lib/
$ wget http://ss.bscstorage.com/lzl/flume-hdfs-sink-1.9.0.jar
$ cp flume-hdfs-sink-1.9.0.jar flume-hdfs-sink-1.9.0.bs4.jar
```

## 启动

```bash
$ /root/fucheng.wang/flume

$ /root/fucheng.wang/flume/bin/flume-ng agent -n flume-collection-1st -c  /root/fucheng.wang/flume/conf:/var/lib/flume-ng -f /root/fucheng.wang/flume/conf/flume-collection-1st.properties

$ tail -f /root/fucheng.wang/flume/logs/flume.log
```

## 安装 lina

```bash
$ cd /root/fucheng.wang/
$ wget ss.bscstorage.com/breakwang-public/lina.tgz
$ tar -xzf lina.tgz

$ cd lina/
$ java -Djava.net.preferIPv4Stack=true -Xmx512m -XX:-UseGCOverheadLimit -XX:+UseConcMarkSweepGC -Dlog4j.logger.com.example=DEBUG -jar /root/fucheng.wang/lina/Lina.jar application_nginx_jh.conf
```

## 生成测试文件

```bash
$ echo 'local 183.252.238.169 www.wengmq.top "image/webp" [07/Dec/2023:14:13:02 +0800] "GET https://qnyb00.cdn.ipalfish.com/0/img/12/6f/852e0adec20bfde2b40280b8244a?x-oss-process=image/resize,m_mfit,h_315/format,webp HTTP/1.1" 200 5851 "-" "reading/3.2.40841+(iPad;+iOS+12.5.3;+Scale/2.00)" 1 5080 "5080" "-@-" "-" 112.48.168.138:6168@112.48.168.139:18004@-@BC67_dx-lt-yd-shandong-jinan-5-cache-8,+BC139_yd-fujian-xiamen-11-cache-1@Mon,+23+Sep+2019+06:21:47+GMT@24e20c5bf727cb42b41eca6153c8d4ae@1898@- -@-@0@-@-@0@0@0@-@https@-@1@1898@0@1898@N@-@ssd@- "-" - TCP_HIT NONE -' >> /tmp/test.log;

$ time=`date +%s`;fn=`printf "/root/fucheng.wang/lina_test_data/work/tengine_20240126154520-%d%09d.log" $time 1`; mv /tmp/test.log $fn
```
