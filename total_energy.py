import numpy as np

def get_energy(input_file, output_file):
    # 读取文件
    with open(input_file, 'r') as f:
        content = f.readlines()
    
    for line in content:
        if line.startswith(' ENERGY| Total '):
            energy = float(line.split()[-1])
    
    # 将能量写入输出文件
    with open(output_file, 'a+') as f:
        f.write(f'{energy}, ')


if __name__ == '__main__':

    input_file = "play.txt"
    
    output_file = 'total_energy.txt'
    
    # 调用函数生成随机改动的文件
    get_energy(input_file, output_file)