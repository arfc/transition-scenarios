for number in {0..35}
do 
  for iteration in {0..20}
  do 
    dakota.sh -input "tuning_{number}.in"
    mv "tuning_{number}.out" "tuning_{number}_{iteration}.out"
    rm cyclus-files/*
  done 
done  
