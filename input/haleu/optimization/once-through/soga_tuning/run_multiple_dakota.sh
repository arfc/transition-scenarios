for number in 0 1 2 3 4 5 6 7 8 9 
do
  dakota.sh "tuning_${number}.in"
  rm cyclus-files/*
done
