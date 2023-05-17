#!/bin/sh

for i in $(seq 1 30)
do
  echo "Loop iteration: $i"
  # Add any additional commands here
#  /bin/sh ./file_throughput.sh &
   nohup python file_operation.py &
done