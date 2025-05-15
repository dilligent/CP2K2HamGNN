cd ./random_inputs
echo "Starting calculations..."
for j in {1..100}
do
    cd ./$j
    /mnt/d/FDU/计算学习/Si_cal/matrix_add.o
    cd ../
    echo "Finished calculation for $j"
done

echo "All calculations are done."