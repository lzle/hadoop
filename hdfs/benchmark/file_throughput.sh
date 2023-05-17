#!/bin/bash


HOSTNAME=$(hostname)
FILESIZE="4K"
UPLOAD_DIR="/stress/throughput"
LOCAL_FILE="/home/hadoop/$FILESIZE.file"
TIMESTAMP=$(date +%s)
CURRENT_PID=$$

log() {
    echo "$1"
}


prepare_work() {
    # create hdfs availability uploaded dir
    if ! $(hdfs dfs -test -d "$UPLOAD_DIR/${HOSTNAME}_${CURRENT_PID}"); then
        hdfs dfs -mkdir "$UPLOAD_DIR/${HOSTNAME}_${CURRENT_PID}"
        log "Create hdfs dir $UPLOAD_DIR/${HOSTNAME}_${CURRENT_PID}"
    fi

    # create test file to put
    if [ ! -f $LOCAL_FILE ]; then
        dd if=/dev/zero of=$LOCAL_FILE bs=$FILESIZE count=1 >/dev/null 2>&1
        log "Create file $LOCAL_FILE"
    fi
}


put_file() {
    local resp=$(hdfs dfs -put $LOCAL_FILE $UPLOAD_FILE)
    if [ $? -eq 0 ]; then
        log "Put file $UPLOAD_FILE successfully!!"
    elif [ $? -eq 143 ]; then
        log "Failed to put file $UPLOAD_FILE!! resp message timeout"
    else
        log "Failed to put file $UPLOAD_FILE!! resp message $resp"
    fi
}


get_file() {
    local resp=$(hdfs dfs -cat $UPLOAD_FILE)
    if [ $? -eq 0 ]; then
        log "Get file $UPLOAD_FILE successfully!!"
    elif [ $? -eq 143 ]; then
        log "Failed to get file $UPLOAD_FILE!! resp message timeout"
    else
        log "Failed to get file $UPLOAD_FILE!! resp message $resp"
    fi
}


main() {
    prepare_work
    count=0
    while true
    do
        count=$((count+1))
        UPLOAD_FILE="${UPLOAD_DIR}/${HOSTNAME}_${CURRENT_PID}/${TIMESTAMP}_${count}.file"
        put_file
        # Generate a random number between 0 and 9
#        random_num=$((RANDOM % 10))
#        if [ $random_num -lt 5 ]
#        then
#            get_file
#        fi
#        get_file
    done
}

main
