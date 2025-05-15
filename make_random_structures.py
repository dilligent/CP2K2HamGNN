'''改动./Si_bulk2x2x2.inp, 生成100个随机结构的inp文件'''
import os
import numpy as np

def perturb_si_atoms(input_file, output_file):
    """
    从CP2K输入文件中随机选择并扰动Si原子的坐标。
    扰动遵循正态分布，大部分值在-0.1到0.1之间。
    
    参数:
    -----------
    input_file : str
        CP2K输入文件的路径
    output_file : str
        输出修改后的CP2K文件的路径
    """
    # 读取CP2K输入文件
    with open(input_file, 'r') as f:
        content = f.readlines()
    
    # 提取Si坐标
    si_coords = []
    si_lines = []
    
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
                si_coords.append([x, y, z])
                si_lines.append(i)
    
    # 转换为numpy数组
    coords = np.array(si_coords)
    num_atoms = len(coords)
    
    print(f"在输入文件中找到{num_atoms}个Si原子。")
    
    # 随机选择要移动的原子数量（在1和num_atoms之间）
    num_to_move = np.random.randint(1, (num_atoms + 1))
    
    # 随机选择要移动的原子
    indices_to_move = np.random.choice(num_atoms, num_to_move, replace=False)
    
    # 生成正态分布的随机位移
    # 使用scale=0.033意味着约99.7%的值将在±0.1范围内(3个标准差)
    displacements = np.random.normal(0, 0.033, size=(num_to_move, 3))
    
    # 复制原始坐标
    perturbed_coords = coords.copy()
    
    # 对选定的原子应用位移
    perturbed_coords[indices_to_move] += displacements
    
    # 用扰动后的坐标更新内容
    for idx, line_idx in enumerate(si_lines):
        x, y, z = perturbed_coords[idx]
        content[line_idx] = f"      Si     {x:.9f}      {y:.9f}      {z:.9f}\n"
    
    # 将修改后的内容写入输出文件
    with open(output_file, 'w') as f:
        f.writelines(content)
    
    print(f"在{num_atoms}个Si原子中随机移动了{num_to_move}个原子。")
    print(f"修改后的坐标已写入{output_file}")

if __name__ == "__main__":
    # 原始输入文件路径
    input_file = "Si_bulk8.inp"
    input_file_name = "Si_bulk8"
    
    # 生成100个随机改动过的输入文件
    for i in range(1, 101):
        # 每次迭代重置随机种子，确保每次生成的扰动不同
        np.random.seed()  # 使用系统时间作为随机种子
        
        # 创建带编号的输出文件名
        output_file = f"./random_inputs/{i}/{input_file_name}_random_{i}.inp"
        
        # 调用函数生成随机改动的文件
        perturb_si_atoms(input_file, output_file)
        
        # 打印进度信息
        print(f"已生成第 {i}/100 个随机改动文件: {output_file}")
    
    print("完成! 成功生成100个随机改动的输入文件.")