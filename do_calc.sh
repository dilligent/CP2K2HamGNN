kp[0]="      KPOINT   0.000000   0.000000   0.000000  1"
kp[1]="      KPOINT  -0.250000  -0.250000  -0.250000  1"
kp[2]="      KPOINT  -0.250000  -0.250000   0.250000  1"
kp[3]="      KPOINT  -0.250000   0.250000  -0.250000  1"
kp[4]="      KPOINT  -0.250000   0.250000   0.250000  1"
# kp[5]="      KPOINT   0.250000  -0.250000  -0.250000  1"
# kp[6]="      KPOINT   0.250000  -0.250000   0.250000  1"
# kp[7]="      KPOINT   0.250000   0.250000  -0.250000  1"
# kp[8]="      KPOINT   0.250000   0.250000   0.250000  1"

tag[0]="000"
tag[1]="---"
tag[2]="--+"
tag[3]="-+-"
tag[4]="-++"
# tag[5]="+--"
# tag[6]="+-+"
# tag[7]="++-"
# tag[8]="+++"

cd ./random_inputs
echo "Starting calculations..."
for j in {1..100}
do
    cd ./$j
    cp /mnt/d/FDU/计算学习/Si_cal/Si_bulk8-RESTART.wfn ./Si_bulk8-RESTART.wfn
    file_name=$(ls | grep "Si_bulk8_random_$j.inp")
    for i in {0..4}
    do
        echo "Running calculation for ${tag[i]} with ${kp[i]}"

        sed -i "36 c\\${kp[i]}" ${file_name}

        time cp2k.ssmp ${file_name} > ./play.txt

        /mnt/d/FDU/计算学习/Si_cal/read_last_KS_matrix_yuanbao.o
        mv ./matrix.csv ./matrix${tag[i]}.csv
    done
    rm ./last_block.txt
    rm ./play.txt
    rm ./Si_bulk8-RESTART*
    cd ../
    echo "Finished calculation for $j"
done

echo "All calculations are done."
