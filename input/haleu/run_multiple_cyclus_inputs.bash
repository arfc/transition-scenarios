for scenario in 2 3 4 5 6 7 8 9 10 11 12 13
do 
  rm "outputs/scenario${scenario}.sqlite"
    cyclus -i "inputs/scenario${scenario}.xml" -o "outputs/scenario${scenario}.sqlite"
done
