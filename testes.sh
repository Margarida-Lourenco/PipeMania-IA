#!/bin/sh

# get all files ending with .txt from ./testes/
# and run them, comparing them with their respective .out
# if the output is the same, print "Test _ SUCCESS" in green,
# otherwise print "Test _ FAILED" in red

# COMO CORRER:
# No diretório ~/PipeMania-IA/ correr:
  # chmod +x testes.sh
  # ./testes.sh

files=$(ls ./testes/ | grep ".txt")

for file in $files
do
  echo -e "Testing $file..."
  python ./pipe.py < ./testes/"$file" > /tmp/pipe.out
  output=$(cat /tmp/pipe.out)
  output_file=$(echo "$file" | sed 's/txt/out/')
  expected_output=$(cat ./testes/"$output_file")
  if [ "$output" = "$expected_output" ]
  then
    echo -e "\e[32mTest $file SUCCESS\e[0m"
  else
    echo -e "\e[31mTest $file FAILED\e[0m"
    # diff between ./testes/$output_file and /tmp/pipe.out
    colordiff -u ./testes/"$output_file" /tmp/pipe.out
  fi
done