for scenario in mmr xe100 xe100_mmr mmr_voygr xe100_voygr xe100_mmr_voygr 
do 
  cyclus -i "inputs/${scenario}_1percent.xml" -o "outputs/${scenario%.xml}_1percent.sqlite"
done
