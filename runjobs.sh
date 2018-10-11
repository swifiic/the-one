#!/bin/bash
commandFile=$1
numJobs=$2
pattern=DTNSim
count=0

mkdir -p out

if [ "$#" -gt 2 ] ; then
    pattern=$3
fi

if [ "$#" -lt 2 ] ; then
    echo "Need the <command list> and <# of jobs in paralell>"
    exit 1
fi

while read -r line; do
    numCommands=`ps -aef | grep ${pattern} | wc -l`
    while [ "${numCommands}" -gt ${numJobs} ] ; do
            sleep 5
            numCommands=`ps -aef | grep ${pattern} | wc -l`
    done
    count=$[${count}+1]
    echo -n " ${count} scheduling ${line}  	 "; date
    outFile="out/${commandFile}_$(printf "%03d" ${count}).out"
    bash -c "${line}" > ${outFile} 2>&1 &
    sleep 2
done < "$commandFile"
