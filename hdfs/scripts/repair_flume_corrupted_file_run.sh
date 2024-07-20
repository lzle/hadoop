#/bin/bash
# author: zhilei.lian@baishan.com
# update 2024.05.25 16:20

LOG_FILE="./repair_file.log"
CURRENT_TIME=$(date)

log() {
    echo "$1" >> "$LOG_FILE"
}

# # extract corrupted files from azshara.log
get_file_list() {
    sudo -u flume /opt/hadoop/bin/hdfs dfs -cat $1 > corrupted_files
}

repair_file() {
    # make original dir && create empty gzip file
    backup_dir="original"
    if [ ! -d $backup_dir ]; then
        mkdir $backup_dir
    fi
    empty_gzip_file="./empty_gzip.gz"
    rm -f $empty_gzip_file; touch empty_gzip && gzip -n empty_gzip
    empty_gzip_content=`cat $empty_gzip_file | hexdump`

    # repair corrupted files
    for file_path in $(cat corrupted_files); do
        log "Checking file ${file_path}"
        file_name=`basename $file_path`

        # check if the file exists in hdfs
        if ! sudo -u flume /opt/hadoop/bin/hdfs dfs -test -e $file_path; then
            log "The file ${file_path} does not exist in HDFS"
            continue
        fi

        file_end_content=`sudo -u flume /opt/hadoop/bin/hdfs dfs -cat $file_path  | tail -c 20 | hexdump`

        if [ "$empty_gzip_content" != "$file_end_content" ]; then
            log "The file ${file_path} is corrupted, try repairing it"
            # backup the corrupted file
            sudo -u root /opt/hadoop/bin/hdfs dfs -get -f $file_path $backup_dir/$file_name
            # repair the corrupted file
            cat $backup_dir/$file_name | gzip -d 2> /dev/null |head -n -1| gzip > $file_name
            cat $empty_gzip_file >> $file_name
            # check if the repaired file is valid
            gzip -t ./$file_name 2> /dev/null
            if [ $? -ne 0 ]; then
                log "The file ${file_path} repair failed"
                rm -f ./$file_name
                continue
            fi
            # put the repaired file back to hdfs
            sudo -u flume /opt/hadoop/bin/hdfs dfs -put -f ./$file_name $file_path
            rm -f $file_name
            log "The file ${file_path} is repaired"
        else
            log "The file ${file_path} is complete and not corrupted"
        fi
    done
}

main() {
    log "Start $CURRENT_TIME"
    get_file_list
    repair_file
    log "Finish"
}

main

# hdfs dfs -ls /separated_tengine/v9-rp.tiktokcdn.com/20240716* | grep -v tmp | awk '{print $NF}' > file_list

