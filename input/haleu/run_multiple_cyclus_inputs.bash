for scenario in mmr xe100 xe100_mmr mmr_voygr xe100_voygr xe100_mmr_voygr 
do 
  rm "outputs/${scenario}_1percent.sqlite"
  cyclus -i "inputs/${scenario}_1percent.xml" -o "outputs/${scenario}_1percent.sqlite"
done
