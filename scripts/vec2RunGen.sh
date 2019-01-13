#~/bin/bash
bStr=" -b 1"
bCmd="java -Xmx512M -cp target:lib/ECLA.jar:lib/DTNConsoleConnection.jar core.DTNSim ${bStr} data/def.txt data/vct2.txt data/RWP50.txt "
eCmd="data/reports2.txt"

nonLinear="data/flow/nonLinear.txt"
adaptList="data/1dtAdapt.txt data/2dtAdapt.txt data/4dtAdapt.txt"
# adaptList="data/1dtAdapt.txt"
ttlList="03"
aimdList="1 2 3 4 5 6 7 8"
# aimdList="9 10 11 12 13 14 15 16"

for  ttl in ${ttlList} ; do
   for  ai in ${aimdList} ; do
   for  md in ${aimdList} ; do
      for  adapt in ${adaptList} ; do
         # Only High for RWP 50 scenario makes sense
         # echo "${bCmd} ${nonLinear} ${adapt} data/ttl/${ttl}hrs.txt data/aImD/${aimd}.txt ${eCmd}"
         echo "${bCmd} data/flow/highSVC4x.txt ${nonLinear} ${adapt} data/ttl/${ttl}hrs.txt data/aI/${ai}.txt data/mD/${md}.txt ${eCmd}"
         # echo "${bCmd} data/flow/mediumSVC.txt ${nonLinear} ${adapt} data/ttl/${ttl}hrs.txt data/aImD/${aimd}.txt ${eCmd}"
      done
      done
   done
   # echo "${bCmd} data/flow/nonSVC.txt ${prefCC} data/ttl/${ttl}hrs.txt ${eCmd}"
   echo "${bCmd} data/flow/nonSVCHigh4x.txt ${prefCC} data/ttl/${ttl}hrs.txt ${eCmd}"
   # echo "${bCmd} data/flow/nonSVCMedium.txt ${prefCC} data/ttl/${ttl}hrs.txt ${eCmd}"
done;



