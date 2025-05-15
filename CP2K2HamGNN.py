# 注意CP2K中长度单位是埃
# CP2K中Si原子轨道顺序是3s, 4s, 4py, 4pz, 4px, 5py, 5pz, 5px, 3d-2, 3d-1, 3d0, 3d+1, 3d+2

import os
import numpy as np
import torch
from torch_geometric.data import Data
from pymatgen.core.structure import Structure
from pymatgen.core.periodic_table import Element

################################ 输入参数设置 ####################
nao_max = 13  # 最大轨道数
output_dir = './graph_data/'  # 输出目录
h_dat_files = ['matrix000.csv', 'matrix---.csv', 'matrix--+.csv', 'matrix-+-.csv', 'matrix-++.csv']  # 哈密顿矩阵文件名
s_dat_files = ['overlap000.csv', 'overlap---.csv', 'overlap--+.csv', 'overlap-+-.csv', 'overlap-++.csv']  # 重叠矩阵文件名
poscar_file = 'POSCAR'  # 晶体结构文件名
start_dir = 1  # 起始目录编号
end_dir = 60  # 结束目录编号
################################ 输入参数结束 ####################

# 基于文件中的轨道信息，这里是13个轨道(3s, 4s, 4py, 4pz, 4px, 5py, 5pz, 5px, 3d-2, 3d-1, 3d0, 3d+1, 3d+2)
basis_def = { 14: np.arange(0, 13, dtype=int) }  # Si原子的轨道索引

kps = np.array([[0, 0, 0], [-0.25, -0.25, -0.25], [-0.25, -0.25, 0.25], [-0.25, 0.25, -0.25], [-0.25, 0.25, 0.25]], dtype=np.float64) # k点坐标, 单位2Pi/Bohr

def read_structure(poscar_file):
    '''读取POSCAR文件获取晶体结构'''
    struct = Structure.from_file(poscar_file)
    # 将A单位转换为Bohr单位
    ang2au = 1.8897259886
    lattice_bohr = struct.lattice.matrix * ang2au
    positions_bohr = struct.cart_coords * ang2au
    return struct.species, lattice_bohr, positions_bohr

def get_submatrix(matrix, i, j):
    '''获取子矩阵'''
    # 输入矩阵为832x832, 子矩阵应为13x13
    return matrix[13*i:(13*i+13), 13*j:(13*j+13)]

def format_matrices_for_graph(Hon, Hoff, Son, Soff, z, edge_index, nao_max):
    '''将哈密顿矩阵和重叠矩阵格式化为graph_data所需格式'''
    num_atoms = len(Hon)
    num_edges = len(Hoff)
    # 转换为nao_max x nao_max大小的矩阵，其中实际使用的轨道部分填充实际值
    H = np.zeros((num_atoms + num_edges, nao_max**2))
    S = np.zeros((num_atoms + num_edges, nao_max**2))
    # 处理原子内矩阵
    for i in range(num_atoms):
        tH = np.zeros((nao_max, nao_max))
        tS = np.zeros((nao_max, nao_max))

        idx = basis_def[z[i]]  # 碳原子的轨道索引
        tH[idx[:, None], idx[None, :]] = Hon[i]
        tS[idx[:, None], idx[None, :]] = Son[i]
        H[i] = tH.flatten()
        S[i] = tS.flatten()
    # 处理原子间矩阵
    for i in range(num_edges):
        tH = np.zeros((nao_max, nao_max))
        tS = np.zeros((nao_max, nao_max))
        src, dst = basis_def[z[edge_index[0, i]]], basis_def[z[edge_index[1, i]]]
        tH[src[:, None], dst[None, :]] = Hoff[i]
        tS[src[:, None], dst[None, :]] = Soff[i]
        H[num_atoms + i] = tH.flatten()
        S[num_atoms + i] = tS.flatten()
    return H, S

def process_directory(dir_path, edges, cell_shift):
    '''处理单个目录并返回图数据'''
    poscar_path = os.path.join(dir_path, poscar_file)
    h_dat_paths = [os.path.join(dir_path, h_dat_file) for h_dat_file in h_dat_files]
    s_dat_paths = [os.path.join(dir_path, s_dat_file) for s_dat_file in s_dat_files]
    energy_path = os.path.join(dir_path, 'total_energy.txt')

    if not os.path.exists(energy_path) or not os.path.exists(poscar_path):
        print(f'在目录 {dir_path} 中找不到必要文件')
        return None
    
    print(f'处理目录: {dir_path}')
    
    # 读取当前目录下的矩阵数据, 每个目录重复一次
    h_matrices = [np.loadtxt(h_dat_path, delimiter=',') for h_dat_path in h_dat_paths]
    h_0 = np.loadtxt(os.path.join(dir_path, 'result000.csv'), delimiter=',')
    s_matrices = [np.loadtxt(s_dat_path, delimiter=',') for s_dat_path in s_dat_paths]
    s_0 = np.loadtxt(os.path.join(dir_path, 'resultover000.csv'), delimiter=',')

    # 读取晶体结构
    species, lattice, positions = read_structure(poscar_path)
    z = np.array([Element(sp.symbol).Z for sp in species])

    num_atoms = len(z)

    num_edges = len(edges)

    edge_index = edges.T

    cell_shift = cell_shift.astype(int)

    total_energy = np.mean(np.loadtxt(energy_path, delimiter=','))

    nbr_shift = np.zeros((num_edges, 3), dtype=float)
    # for i in range(num_edges):
    #     nbr_shift[i] = (positions[edge_index[1, i]] - positions[edge_index[0, i]]) % lattice
    for i, shift in enumerate(cell_shift):
        nbr_shift[i] = shift[0] * lattice[0] + shift[1] * lattice[1] + shift[2] * lattice[2]

    
    # 找到逆边索引
    inv_edge_idx = -np.ones(num_edges, dtype=int)
    for i in range(num_edges):
        for j in range(num_edges):
            if edge_index[0, i] == edge_index[1, j] and edge_index[1, i] == edge_index[0, j] and np.array_equal(cell_shift[i], -cell_shift[j]):
                inv_edge_idx[i] = j
                break
    

    Hon = []
    Son = []
    for i in range(num_atoms):
        Hon.append(get_submatrix(h_0, i, i))
        Son.append(get_submatrix(s_0, i, i))

    Hoff = []
    Soff = []
    for i in range(num_edges):
        h_temp = np.zeros((13, 13))
        s_temp = np.zeros((13, 13))
        src, dst = edge_index[0, i], edge_index[1, i]
        vector = positions[dst] + nbr_shift[i] - positions[src]
        h_temp += get_submatrix(h_matrices[0], src, dst)
        h_temp += get_submatrix(h_matrices[1], src, dst)*2*np.cos(np.dot(kps[1], vector))
        h_temp += get_submatrix(h_matrices[2], src, dst)*2*np.cos(np.dot(kps[2], vector))
        h_temp += get_submatrix(h_matrices[3], src, dst)*2*np.cos(np.dot(kps[3], vector))
        h_temp += get_submatrix(h_matrices[4], src, dst)*2*np.cos(np.dot(kps[4], vector))
        Hoff.append(h_temp/9)
        s_temp += get_submatrix(s_matrices[0], src, dst)
        s_temp += get_submatrix(s_matrices[1], src, dst)*2*np.cos(np.dot(kps[1], vector))
        s_temp += get_submatrix(s_matrices[2], src, dst)*2*np.cos(np.dot(kps[2], vector))
        s_temp += get_submatrix(s_matrices[3], src, dst)*2*np.cos(np.dot(kps[3], vector))
        s_temp += get_submatrix(s_matrices[4], src, dst)*2*np.cos(np.dot(kps[4], vector))
        Soff.append(s_temp/9)
    
    # 格式化矩阵为需要的形式
    H, S = format_matrices_for_graph(Hon, Hoff, Son, Soff, z, edge_index, nao_max)
    
    # 生成H0（全零矩阵）
    H0 = np.zeros_like(H)
    
    # 创建PyTorch Geometric数据对象
    graph_data = Data(
        z=torch.LongTensor(z),
        cell=torch.Tensor(lattice[None, :, :]),
        total_energy=torch.Tensor([total_energy]),
        pos=torch.FloatTensor(positions),
        node_counts=torch.LongTensor([len(z)]),
        edge_index=torch.LongTensor(edge_index),
        inv_edge_idx=torch.LongTensor(inv_edge_idx),
        nbr_shift=torch.FloatTensor(nbr_shift),
        cell_shift=torch.LongTensor(cell_shift),
        hamiltonian=torch.FloatTensor(H),
        overlap=torch.FloatTensor(S),
        Hon=torch.FloatTensor(H[:num_atoms, :]),
        Hoff=torch.FloatTensor(H[num_atoms:, :]),
        Hon0=torch.FloatTensor(H0[:num_atoms, :]),
        Hoff0=torch.FloatTensor(H0[num_atoms:, :]),
        Son=torch.FloatTensor(S[:num_atoms, :]),
        Soff=torch.FloatTensor(S[num_atoms:, :])
    )
    
    return graph_data


def main():
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 存储所有图数据的字典
    all_graphs = {}
    graph_index = 0

    # 预制好的边索引, 对所有数据都是恒定的
    edges = np.load('edge_index.npy')
    cell_shift = np.load('cell_shift.npy')
    
    # 处理所有目录
    for dir_num in range(start_dir, end_dir + 1):
        dir_path = f'./random_inputs/{dir_num}'  # 目录名称
        
        # 处理当前目录
        graph_data = process_directory(dir_path, edges, cell_shift)
        
        if graph_data is not None:
            all_graphs[graph_index] = graph_data
            graph_index += 1
            print(f'成功处理目录 {dir_path}, 图数据索引: {graph_index-1}')
        else:
            print(f'跳过目录 {dir_path}')
    
    # 保存合并后的数据
    output_file = os.path.join(output_dir, 'graph_data.npz')
    np.savez(output_file, graph=all_graphs)
    print(f'所有图数据已保存到 {output_file}，共处理了 {graph_index} 个图')

if __name__ == '__main__':
    main()