#~/bin/bash
bStr=" -b 5"
bCmd="java -Xmx512M -cp target:lib/ECLA.jar:lib/DTNConsoleConnection.jar core.DTNSim ${bStr} data/def.txt data/vct.txt "
eCmd="data/reports.txt"

nonLinear="data/flow/nonLinear.txt"
prefCC="data/prefCC.txt"
fullAdapt="data/fullAdapt.txt"
ttlList="24 36 48 12"

for  ttl in ${ttlList} ; do
      # five runs for Full Adapt, prefCC, nonLinear, Linear, nonSVC - only Full Adapt and nonSVC for now
      echo "${bCmd} ${nonLinear} ${fullAdapt} data/ttl/${ttl}hrs.txt ${eCmd}"
      # echo "${bCmd} ${nonLinear} ${prefCC}    data/ttl/${ttl}hrs.txt ${eCmd}"
      # echo "${bCmd} ${nonLinear} data/ttl/${ttl}hrs.txt ${eCmd}"

      # echo "${bCmd} data/ttl/${ttl}hrs.txt ${eCmd}"

      echo "${bCmd} data/flow/nonSVC.txt data/ttl/${ttl}hrs.txt ${eCmd}"


      # data/flow: highSVC.txt  mediumSVC.txt  nonLinear.txt  nonSVC.txt
      #             nonSVCHigh.txt  nonSVCMedium.txt
      # Now for Resulution based runs - only nonSVC and FullAdapt
      echo "${bCmd} data/flow/highSVC.txt ${nonLinear} ${fullAdapt} data/ttl/${ttl}hrs.txt ${eCmd}"

      echo "${bCmd} data/flow/mediumSVC.txt ${nonLinear} ${fullAdapt} data/ttl/${ttl}hrs.txt ${eCmd}"

      echo "${bCmd} data/flow/nonSVCHigh.txt data/ttl/${ttl}hrs.txt ${eCmd}"

      echo "${bCmd} data/flow/nonSVCMedium.txt data/ttl/${ttl}hrs.txt ${eCmd}"

      # data/nodes/: drop1.txt  drop2.txt  drop4.txt
      # Now for Nodes based runs - only nonSVC and FullAdapt
      echo "${bCmd} data/nodes/drop1.txt ${nonLinear} ${fullAdapt} data/ttl/${ttl}hrs.txt ${eCmd}"
      echo "${bCmd} data/nodes/drop2.txt ${nonLinear} ${fullAdapt} data/ttl/${ttl}hrs.txt ${eCmd}"
      echo "${bCmd} data/nodes/drop4.txt ${nonLinear} ${fullAdapt} data/ttl/${ttl}hrs.txt ${eCmd}"

      echo "${bCmd} data/nodes/drop1.txt data/flow/nonSVC.txt data/ttl/${ttl}hrs.txt ${eCmd}"
      echo "${bCmd} data/nodes/drop2.txt data/flow/nonSVC.txt data/ttl/${ttl}hrs.txt ${eCmd}"
      echo "${bCmd} data/nodes/drop4.txt data/flow/nonSVC.txt data/ttl/${ttl}hrs.txt ${eCmd}"

done;



