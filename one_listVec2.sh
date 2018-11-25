#~/bin/bash
bStr=" -b 1"
bCmd="java -Xmx512M -cp target:lib/ECLA.jar:lib/DTNConsoleConnection.jar core.DTNSim ${bStr} data/def.txt data/vct2.txt data/RWP50.txt "
eCmd="data/reports2.txt"

nonLinear="data/flow/nonLinear.txt"
adaptList="data/fullAdapt.txt data/2ackAdapt.txt data/1ackAdapt.txt"
ttlList="03 06"
aimdList="1 2 3 4 5 6 7 8 9"

for  ttl in ${ttlList} ; do
   for  aimd in ${aimdList} ; do
      for  adapt in ${adaptList} ; do
         # Only High for RWP 50 scenario makes sense
         # echo "${bCmd} ${nonLinear} ${adapt} data/ttl/${ttl}hrs.txt data/aImD/${aimd}.txt ${eCmd}"
         echo "${bCmd} data/flow/highSVC.txt ${nonLinear} ${adapt} data/ttl/${ttl}hrs.txt ${eCmd}"
         # echo "${bCmd} data/flow/mediumSVC.txt ${nonLinear} ${adapt} data/ttl/${ttl}hrs.txt ${eCmd}"
      done
   done
   # echo "${bCmd} data/flow/nonSVC.txt ${prefCC} data/ttl/${ttl}hrs.txt ${eCmd}"
   echo "${bCmd} data/flow/nonSVCHigh.txt ${prefCC} data/ttl/${ttl}hrs.txt ${eCmd}"
   # echo "${bCmd} data/flow/nonSVCMedium.txt ${prefCC} data/ttl/${ttl}hrs.txt ${eCmd}"
done;



