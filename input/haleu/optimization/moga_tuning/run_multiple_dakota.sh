for number in {0..9}
do 
  for iteration in {0..19}
  do 
    dakota.sh -input "tuning_${number}.in"
    mv finaldata1.dat "tuning_${number}_${iteration}.dat"
    rm cyclus-files/*
  done 
done  
