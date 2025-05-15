kp[0]="      KPOINT   0.000000   0.000000   0.000000  1"
kp[1]="      KPOINT  -0.250000  -0.250000  -0.250000  1"
kp[2]="      KPOINT  -0.250000  -0.250000   0.250000  1"
kp[3]="      KPOINT  -0.250000   0.250000  -0.250000  1"
kp[4]="      KPOINT  -0.250000   0.250000   0.250000  1"

tag[0]="000"
tag[1]="---"
tag[2]="--+"
tag[3]="-+-"
tag[4]="-++"

cd ./random_inputs
echo "Starting calculations..."
for j in {61..100}
do
    cd ./$j
    file_name=$(ls | grep "Si_bulk8_random_$j.inp")
    sed -i "53 c\\      SCF_GUESS ATOMIC" ${file_name}
    sed -i "54 c\\      # SCF_GUESS RESTART" ${file_name}
    for i in {0..4}
    do
        echo "Running calculation for${kp[i]}"

        sed -i "36 c\\${kp[i]}" ${file_name}

        cp2k.ssmp ${file_name} > ./play.txt
    done
    rm ./play.txt
    cd ../
    echo "Finished calculation for $j"
done

echo "All calculations are done."