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
for j in {1..100}
do
    cd ./$j
    cp /mnt/d/FDU/计算学习/Si_cal/Si_bulk8-RESTART.wfn ./Si_bulk8-RESTART.wfn
    > total_energy.txt

    file_name=$(ls | grep "Si_bulk8_random_$j.inp")

    sed -i "53 c\\      # SCF_GUESS ATOMIC" ${file_name}
    sed -i "54 c\\      SCF_GUESS RESTART" ${file_name}
    sed -i "56 c\\      MAX_SCF 300" ${file_name}
    sed -i "71 c\\    # &PRINT" ${file_name}
    sed -i "77 c\\      # &AO_MATRICES" ${file_name}
    sed -i "78 c\\        # OVERLAP T" ${file_name}
    sed -i "79 c\\        # KOHN_SHAM_MATRIX T" ${file_name}
    sed -i "80 c\\      # &END AO_MATRICES" ${file_name}
    sed -i "81 c\\    # &END PRINT" ${file_name}

    for i in {0..4}
    do
        echo "Running calculation for ${tag[i]} with ${kp[i]}"

        sed -i "36 c\\${kp[i]}" ${file_name}

        time cp2k.ssmp ${file_name} > ./play.txt

        python3 /mnt/d/FDU/计算学习/Si_cal/total_energy.py
    done
    rm ./play.txt
    rm ./Si_bulk8-RESTART*
    cd ../
    echo "Finished calculation for $j"
done

echo "All calculations are done."