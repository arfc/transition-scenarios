for number in 10 11 12 13 14 15 16 17 18 19 
do
  dakota.sh "tuning_${number}.in"
  rm cyclus-files/*
done
