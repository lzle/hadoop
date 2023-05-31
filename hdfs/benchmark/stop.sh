
#ps -ef | grep file_throughput.sh | grep -v grep | awk '{print $2}' | xargs kill -9



ps -ef | grep file_operation.py | grep -v grep | awk '{print $2}' | xargs kill -9
ps -ef | grep file_qps.py | grep -v grep | awk '{print $2}' | xargs kill -9
