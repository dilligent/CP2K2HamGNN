import numpy as np

def atom_distance(input_file, cutoff):
    # 读取CP2K输入文件
    with open(input_file, 'r') as f:
        content = f.readlines()
    cutoff_sq = cutoff ** 2

    # 提取坐标
    cell = np.zeros((3, 3))
    atom_coords = []
    atom_lines = []
    
    in_cell_section = False
    for i, line in enumerate(content):
        line = line.strip()
        
        # 找到晶胞部分
        if '&CELL' in line:
            in_cell_section = True
            continue
        if in_cell_section and '&END CELL' in line:
            in_cell_section = False
            continue
        
        if in_cell_section and line.startswith('A'):
            parts = line.split()
            if len(parts) >= 4:
                cell[0] = [float(parts[1]), float(parts[2]), float(parts[3])]
                continue
        if in_cell_section and line.startswith('B'):
            parts = line.split()
            if len(parts) >= 4:
                cell[1] = [float(parts[1]), float(parts[2]), float(parts[3])]
                continue
        if in_cell_section and line.startswith('C'):
            parts = line.split()
            if len(parts) >= 4:
                cell[2] = [float(parts[1]), float(parts[2]), float(parts[3])]
                continue

    in_coord_section = False
    for i, line in enumerate(content):
        line = line.strip()
        
        # 找到坐标部分
        if '&COORD' in line:
            in_coord_section = True
            continue
        
        if in_coord_section and '&END COORD' in line:
            in_coord_section = False
            continue
        
        if in_coord_section and line.startswith('Si'):
            parts = line.split()
            if len(parts) >= 4:
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                atom_coords.append([x, y, z])
                atom_lines.append(i)
    
    # 转换为numpy数组
    coords = np.array(atom_coords)
    
    arr = np.arange(0, 8)
    second = np.concatenate([arr[arr != num] for num in arr])
    first = np.repeat(arr, len(arr) - 1)
    permutation = np.column_stack((first, second))
    flags = np.zeros(len(permutation), dtype=bool)

    edge_index = []
    cell_shift = []

    for i in range(len(permutation)):
        atom1 = coords[permutation[i][0]]
        atom2 = coords[permutation[i][1]]

        # 考虑周期性边界条件
        for l in [-1, 0, 1]:
            for m in [-1, 0, 1]:
                for n in [-1, 0, 1]:
                    shift = l * cell[0] + m * cell[1] + n * cell[2]
                    diff = atom2 + shift - atom1
                    distance_sq = np.dot(diff, diff)
                    if distance_sq < cutoff_sq:
                        edge_index.append([permutation[i][0], permutation[i][1]])
                        cell_shift.append([l, m, n])
    
    print(f"边的数量: {len(edge_index)}")
    np.save('edge_index.npy', edge_index)
    np.save('cell_shift.npy', cell_shift)


if __name__ == "__main__":

    input_file = "Si_bulk8.inp"
    cutoff = 4.0  # 设置cutoff值
    
    atom_distance(input_file, cutoff)