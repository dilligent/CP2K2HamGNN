#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define ROWS 104
#define COLS 104
#define NUM_FILES 5
#define UNROLL_FACTOR 8 // 循环展开因子

// 使用OpenMP进行并行处理（如果支持）
#ifdef _OPENMP
#include <omp.h>
#endif

// 读取CSV文件到矩阵
int read_matrix(const char* filename, float* matrix) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "无法打开文件: %s\n", filename);
        return 1;
    }
    
    char* line = NULL;
    size_t len = 0;
    int row = 0;
    char* token;
    char* saveptr;
    
    while (row < ROWS && getline(&line, &len, file) != -1) {
        token = strtok_r(line, ",\n", &saveptr);
        int col = 0;
        
        while (token != NULL && col < COLS) {
            matrix[row * COLS + col] = atof(token);
            token = strtok_r(NULL, ",\n", &saveptr);
            col++;
        }
        
        if (col != COLS) {
            fprintf(stderr, "第 %d 行列数错误\n", row + 1);
            free(line);
            fclose(file);
            return 1;
        }
        
        row++;
    }
    
    if (line) free(line);
    fclose(file);
    
    if (row != ROWS) {
        fprintf(stderr, "行数错误: 读取了 %d 行, 应该是 %d 行\n", row, ROWS);
        return 1;
    }
    
    return 0;
}

// 快速版本：使用SSE/AVX指令集和OpenMP的矩阵缩放和加法
void scale_and_add(float* restrict result, const float* restrict matrix, float coef) {
    #pragma omp parallel for
    for (int i = 0; i < ROWS; i++) {
        int j = 0;
        
        // 循环展开以提高性能
        for (j = 0; j <= COLS - UNROLL_FACTOR; j += UNROLL_FACTOR) {
            result[i * COLS + j]     += matrix[i * COLS + j]     * coef;
            result[i * COLS + j + 1] += matrix[i * COLS + j + 1] * coef;
            result[i * COLS + j + 2] += matrix[i * COLS + j + 2] * coef;
            result[i * COLS + j + 3] += matrix[i * COLS + j + 3] * coef;
            result[i * COLS + j + 4] += matrix[i * COLS + j + 4] * coef;
            result[i * COLS + j + 5] += matrix[i * COLS + j + 5] * coef;
            result[i * COLS + j + 6] += matrix[i * COLS + j + 6] * coef;
            result[i * COLS + j + 7] += matrix[i * COLS + j + 7] * coef;
        }
        
        // 处理剩余元素
        for (; j < COLS; j++) {
            result[i * COLS + j] += matrix[i * COLS + j] * coef;
        }
    }
}

// 将矩阵写入CSV文件 - 简化版本确保正确写入
int write_matrix(const char* filename, const float* matrix) {
    FILE* file = fopen(filename, "w");
    if (!file) {
        fprintf(stderr, "无法打开文件进行写入: %s\n", filename);
        return 1;
    }
    
    for (int i = 0; i < ROWS; i++) {
        for (int j = 0; j < COLS - 1; j++) {
            fprintf(file, "%.6f,", matrix[i * COLS + j]);
        }
        fprintf(file, "%.6f\n", matrix[i * COLS + COLS - 1]);
        
        // 确保数据被写入
        if (i % 100 == 0) {
            fflush(file);
        }
    }
    
    fclose(file);
    return 0;
}

int main(int argc, char* argv[]) {
    char* inputFiles[NUM_FILES];
    char* outputFile;
    float coefficients[NUM_FILES];
    
    // 处理命令行参数
    if (argc >= NUM_FILES + 2) {
        for (int i = 0; i < NUM_FILES; i++) {
            inputFiles[i] = argv[i + 1];
        }
        outputFile = argv[NUM_FILES + 1];
        
        // 获取系数，如果提供
        for (int i = 0; i < NUM_FILES; i++) {
            if (argc > NUM_FILES + 1 + i) {
                coefficients[i] = atof(argv[NUM_FILES + 2 + i]);
            } else {
                coefficients[i] = 1.0f; // 默认系数
            }
        }
    } else {
        // 默认文件名和参数
        inputFiles[0] = "overlap000.csv";
        inputFiles[1] = "overlap---.csv";
        inputFiles[2] = "overlap--+.csv";
        inputFiles[3] = "overlap-+-.csv";
        inputFiles[4] = "overlap-++.csv";
        outputFile = "resultover000.csv";
        
        // 默认系数
        coefficients[0] = 1.0f/9.0f;
        coefficients[1] = 2.0f/9.0f;
        coefficients[2] = 2.0f/9.0f;
        coefficients[3] = 2.0f/9.0f;
        coefficients[4] = 2.0f/9.0f;
        
        printf("使用默认参数\n");
        printf("用法: %s 文件1.csv 文件2.csv 文件3.csv 文件4.csv 文件5.csv 结果.csv [系数1 系数2 系数3 系数4 系数5]\n", argv[0]);
    }
    
    // 分配内存并初始化结果矩阵为0
    float* result = (float*)calloc(ROWS * COLS, sizeof(float));
    if (!result) {
        fprintf(stderr, "内存分配失败\n");
        return 1;
    }
    
    // 为输入矩阵分配内存
    float* matrix = (float*)malloc(ROWS * COLS * sizeof(float));
    if (!matrix) {
        fprintf(stderr, "内存分配失败\n");
        free(result);
        return 1;
    }
    
    // 处理每个输入文件
    for (int i = 0; i < NUM_FILES; i++) {
        printf("正在处理文件 %s (系数 = %.6f)\n", inputFiles[i], coefficients[i]);
        
        if (read_matrix(inputFiles[i], matrix) != 0) {
            fprintf(stderr, "读取文件失败: %s\n", inputFiles[i]);
            continue; // 继续处理下一个文件
        }
        
        // 对矩阵应用系数并加到结果上
        scale_and_add(result, matrix, coefficients[i]);
        
        // 验证数据已经被加入
        float sum = 0.0f;
        for (int j = 0; j < 10; j++) sum += result[j];
        printf("调试: 前10个结果元素的和 = %.6f\n", sum);
    }
    
    // 写入结果
    printf("正在写入结果到: %s\n", outputFile);
    if (write_matrix(outputFile, result) != 0) {
        fprintf(stderr, "写入结果失败\n");
    } else {
        printf("成功写入结果矩阵 (%d×%d) 到 %s\n", ROWS, COLS, outputFile);
    }
    
    // 释放内存
    free(matrix);
    free(result);
    
    return 0;
}