#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MATRIX_SIZE 104
#define LINE_BUFFER_SIZE 1024

int is_header_line(const char *line, int *cols) {
    if (sscanf(line, "%d%d%d%d", &cols[0], &cols[1], &cols[2], &cols[3]) != 4)
        return 0;
    return (cols[1] == cols[0]+1 && cols[2] == cols[1]+1 && cols[3] == cols[2]+1);
}

long find_last_block_start(FILE *file) {
    long last_start = -1, current_pos;
    char line[LINE_BUFFER_SIZE];
    
    rewind(file);
    while (fgets(line, LINE_BUFFER_SIZE, file)) {
        int cols[4];
        if (is_header_line(line, cols) && cols[0] == 1) {
            current_pos = ftell(file) - strlen(line);
            last_start = current_pos;
        }
    }
    return last_start;
}

void process_block(FILE *src, FILE *dest, double *matrix) {
    char line[LINE_BUFFER_SIZE];
    int current_cols[4] = {0};
    
    while (fgets(line, LINE_BUFFER_SIZE, src)) {
        fputs(line, dest);

        int cols[4];
        if (is_header_line(line, cols)) {
            memcpy(current_cols, cols, sizeof(current_cols));
            continue;
        }

        int row, dummy;
        char s1[16], s2[16];
        double values[4];
        
        if (sscanf(line, "%d %d %s %s %lf %lf %lf %lf",
                  &row, &dummy, s1, s2, &values[0], &values[1], &values[2], &values[3]) == 8) {
            if (row < 1 || row > MATRIX_SIZE) continue;
            
            for (int i = 0; i < 4; i++) {
                int col_idx = current_cols[i] - 1;
                if (col_idx < 0 || col_idx >= MATRIX_SIZE) continue;
                matrix[(row-1)*MATRIX_SIZE + col_idx] = values[i];
            }
        }
    }
}

void save_optimized_csv(const double* matrix) {
    FILE *csv = fopen("matrix.csv", "w");
    if (!csv) {
        perror("Error creating CSV output");
        // free(matrix);
        // return 1;
    }

    for (int i = 0; i < MATRIX_SIZE; ++i) {
        for (int j = 0; j < MATRIX_SIZE; ++j) {
            double val = matrix[i * MATRIX_SIZE + j];
            if (fabs(val) < 1e-4 && val != 0) {
                fprintf(csv, "%.6f", val);
            } else {
                fprintf(csv, "%.8g", val);
            }
            fputc(j == MATRIX_SIZE - 1 ? '\n' : ',', csv);
        }
    }
    fclose(csv);
}

int main() {
    FILE *input = fopen("play.txt", "r");
    if (!input) {
        perror("Error opening input file");
        return 1;
    }

    long block_start = find_last_block_start(input);
    if (block_start == -1) {
        fprintf(stderr, "No valid matrix block found\n");
        fclose(input);
        return 1;
    }

    fseek(input, block_start, SEEK_SET);

    FILE *block_txt = fopen("last_block.txt", "w");
    if (!block_txt) {
        perror("Error creating text output");
        fclose(input);
        return 1;
    }

    double *matrix = calloc(MATRIX_SIZE * MATRIX_SIZE, sizeof(double));
    if (!matrix) {
        perror("Memory allocation failed");
        fclose(input);
        fclose(block_txt);
        return 1;
    }

    process_block(input, block_txt, matrix);
    
    fclose(input);
    fclose(block_txt);

    save_optimized_csv(matrix);
    
    free(matrix);
    printf("Processing completed successfully\n");
    return 0;
}