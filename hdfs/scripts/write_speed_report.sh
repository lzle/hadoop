#!/bin/sh

HOSTNAME=$(hostname)
LAST_MINUTE=$(date -d "1 minute ago" +"%Y-%m-%d %H:%M")
LOG_FILE="/var/log/hdfs/write_speed_report.log"
HDFS_LOG_FILE="/opt/hadoop/logs/hadoop-hadoop-datanode-$HOSTNAME.log"
HDFS_VERSION="v3.1.2"
HDFS_CLUSTER="hdfs-shijiazhuang"
MALLARD_URL="http://127.0.0.1:10699/v2/push"
CONTENT_TYPE="Content-Type: application/json"

LAST_WRITE_BLOCK_CONTENT=$(grep -E "$LAST_MINUTE.*clienttrace.*HDFS_WRITE" "$HDFS_LOG_FILE")

calc_total_bytes() {
    if [ -z "$LAST_WRITE_BLOCK_CONTENT" ]; then
        echo 0
        return
    fi
    local total_bytes=$(echo "$LAST_WRITE_BLOCK_CONTENT" | awk -F 'bytes: ' '{print $2}' |
                awk -F ', ' '{ total += $1 } END { print int(total) }')
    if [ -z "$total_bytes" ]; then
        total_bytes=0
    fi
    echo "$total_bytes"
}


calc_total_duration() {
    if [ -z "$LAST_WRITE_BLOCK_CONTENT" ]; then
        echo 0
        return
    fi
    local total_duration=$(echo "$LAST_WRITE_BLOCK_CONTENT" | 
                awk -F 'duration\\(ns\\): ' '{ total += $2} END { print int(total) }')
    if [ -z "$total_duration" ]; then
        total_duration=0
    fi
    echo "$total_duration"
}


calc_total_ops() {
    if [ -z "$LAST_WRITE_BLOCK_CONTENT" ]; then
        echo 0
        return
    fi
    local total_ops=$(echo "$LAST_WRITE_BLOCK_CONTENT" | wc -l)
    echo "$total_ops"
}

log() {
    echo "$1" >>"$LOG_FILE"
}

log $LAST_MINUTE

main() {
    log "Starting script at $(date +"%Y-%m-%d %H:%M:%S")..."
    timestamp=$(date +%s)

    total_write_ops=$(calc_total_ops)
    total_write_bytes=$(calc_total_bytes)
    total_write_duration=$(calc_total_duration)

    data='[
    {
        "name": "hdfs_write_speed_report",
        "time": '$timestamp',
        "endpoint": "'"${HOSTNAME}"'",
        "tags": {
            "version": "'"${HDFS_VERSION}"'",
            "cluster": "'"${HDFS_CLUSTER}"'"
        },
        "fields": {
            "total_write_ops": '$total_write_ops',
            "total_write_bytes": '$total_write_bytes',
            "total_write_duration": '$total_write_duration'
        },
        "step": 60,
        "value": '$total_write_ops'
    }]'

    resp=$(curl -X POST "$MALLARD_URL" -H "$CONTENT_TYPE" -d "$data")
    log "Report to mallard, post data: $data, result: $resp"
}

main

# zgrep "2023-05-31 10:45" hadoop-hadoop-datanode-dx-lt-yd-hebei-shijiazhuang-10-10-103-2-45.log | grep clienttrace | awk '{print $10, $NF}' |awk -F ',' '{print $1, $2, ($1/$2*1000*1000*100/1024/1024)}'