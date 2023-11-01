for scenario in mmr xe100 xe100_mmr mmr_voygr xe100_voygr xe100_mmr_voygr limited_TRISO limited_noTRISO continuous
do 
  for growth in nogrowth 1percent
  do rm "outputs/${scenario}_${growth}.sqlite"
     cyclus -i "inputs/${scenario}_${growth}.xml" -o "outputs/${scenario}_${growth}.sqlite"
  done
done
