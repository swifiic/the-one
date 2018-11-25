#~/bin/bash
bStr=" -b 1"
bCmd="java -Xmx512M -cp target:lib/ECLA.jar:lib/DTNConsoleConnection.jar core.DTNSim ${bStr} data/def.txt data/vct2.txt data/RWP50.txt "
eCmd="data/reports2.txt"

nonLinear="data/flow/nonLinear.txt"
prefCC="data/prefCC.txt"
adaptList="data/fullAdapt.txt data/2ackAdapt.txt data/1ackAdapt.txt"
ttlList="12 24 36 48 60"

for  ttl in ${ttlList} ; do
   for  adapt in ${adaptList} ; do
      # five runs for Full Adapt, prefCC, nonLinear, Linear, nonSVC
      echo "${bCmd} ${nonLinear} ${adapt} ${prefCC} data/ttl/${ttl}hrs.txt ${eCmd}"
      echo "${bCmd} data/flow/highSVC.txt ${nonLinear} ${adapt} ${prefCC} data/ttl/${ttl}hrs.txt ${eCmd}"
      echo "${bCmd} data/flow/mediumSVC.txt ${nonLinear} ${adapt} ${prefCC} data/ttl/${ttl}hrs.txt ${eCmd}"
   done
   echo "${bCmd} data/flow/nonSVC.txt ${prefCC} data/ttl/${ttl}hrs.txt ${eCmd}"
   echo "${bCmd} data/flow/nonSVCHigh.txt ${prefCC} data/ttl/${ttl}hrs.txt ${eCmd}"
   echo "${bCmd} data/flow/nonSVCMedium.txt ${prefCC} data/ttl/${ttl}hrs.txt ${eCmd}"
done;



