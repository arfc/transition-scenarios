for scenario in mmr xe100 xe100_mmr mmr_voygr xe100_voygr xe100_mmr_voygr 
do 
  rm "outputs/${scenario%.xml}_nogrowth.sqlite"
  cyclus -i "inputs/${scenario}_nogrowth.xml" -o "outputs/${scenario%.xml}_nogrowth.sqlite"
done
