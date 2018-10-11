#!/bin/bash

ttlList="720 1440 2160 2880 3600"
flowList="low medium high"
contorlList="nonSVC sAdptAndCC"
nodeList="base drop1 drop2 drop4"

echo "for different video qualities"
for ctrl in ${contorlList} ; do
  for  ttl in ${ttlList} ; do
     for  label in ${flowList} ; do
          data=`grep -c "L0 " ${ctrl}_Nbase_R${label}_*_100*ttl${ttl}*Delivered* | awk -F':' -c '{print $2}' | paste -sd "," -`
	  echo "${ctrl}, ${label}, ${ttl}, ${data}"
     done
done; done;

echo "for different node counts"
for ctrl in ${contorlList} ; do
  for  ttl in ${ttlList} ; do
     for node in ${nodeList} ; do
          data=`grep -c "L0 " ${ctrl}_N${node}_Rlow*_100*ttl${ttl}*Delivered*| awk -F':' -c '{print $2}' | paste -sd "," -`
	  echo "${ctrl}, ${node}, ${ttl}, ${data}"
     done
done; done;



