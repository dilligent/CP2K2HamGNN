import os
import numpy as np

def input_to_poscar(input_file, output_file):
    # 读取CP2K输入文件
    with open(input_file, 'r') as f:
        content = f.readlines()
    
    # 提取坐标
    cell = []
    atom_coords = []
    atom_lines = []

    in_cell_section = False
    for i, line in enumerate(content):
        line = line.strip()
        
        # 找到晶格向量部分
        if '&CELL' in line:
            in_cell_section = True
            continue
        
        if in_cell_section and '&END CELL' in line:
            in_cell_section = False
            continue
        
        if in_cell_section and line.startswith('A') or line.startswith('B') or line.startswith('C'):
            parts = line.split()
            if len(parts) >= 4:
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                cell.append([x, y, z])
                atom_lines.append(i)
    
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
    cell = np.array(cell)
    coords = np.array(atom_coords)
    num_atoms = len(coords)

    with open(output_file, 'w') as f:
        
        f.write("Si8\n1.0\n")

        # 写入晶格向量
        for i in range(3):
            f.write(f"{cell[i][0]} {cell[i][1]} {cell[i][2]}\n")
        
        # 写入原子类型和数量
        f.write("Si\n8\nCartesian\n")
        
        # 写入原子坐标
        for i in range(num_atoms):
            f.write(f"{coords[i][0]} {coords[i][1]} {coords[i][2]} Si\n")

    
if __name__ == '__main__':
  
    # 生成100个POSCAR文件
    for i in range(1, 101):

        # 原始输入文件路径
        input_file = f"./random_inputs/{i}/Si_bulk8_random_{i}.inp"
        
        # 创建带编号的输出文件名
        output_file = f'./random_inputs/{i}/POSCAR'
        
        # 调用函数生成随机改动的文件
        input_to_poscar(input_file, output_file)
        
        # 打印进度信息
        print(f'已生成第 {i}/100 个POSCAR文件')
    
    print('完成! 成功生成100个POSCAR文件.')