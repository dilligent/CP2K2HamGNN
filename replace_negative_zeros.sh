#!/bin/bash
# 脚本功能：替换 *.csv 文件中的所有负零 (-0, -0.0) 为零 (0)

cd ./random_inputs || {
    echo "无法进入目录 random_inputs" >&2
    exit 1
}

echo "开始处理当前目录下所有 *.csv 文件..."

for t in {1..100}
do
    echo "正在处理目录 $t..."
    cd ./$t || {
        echo "无法进入目录 $t" >&2
        continue
    }

    # 用于记录处理文件数量
    processed=0

    # 遍历所有匹配模式的文件
    for file in *.csv
    do
        # 跳过当没有找到匹配文件时的情况
        [ -f "$file" ] || continue
        
        echo "正在处理 $file..."
        
        # 创建临时文件
        temp_file="$(mktemp)"
        
        # 使用 awk 处理文件并保存到临时文件
        if awk -F, 'BEGIN{OFS=","} {
            for(i=1;i<=NF;i++) 
                # 处理各种形式的负零，包括 -0、-0.0、-0.00 等
                if($i+0==0 && $i~/^-/) 
                    $i="0"
            print
        }' "$file" > "$temp_file" && 
        mv "$temp_file" "$file"; then
            echo "✓ 成功处理 $file"
            processed=$((processed + 1))
        else
            echo "✗ 处理 $file 失败" >&2
            # 清理临时文件（如果存在）
            rm -f "$temp_file" 2>/dev/null
        fi
    done

    # 报告处理结果
    if [ "$processed" -eq 0 ]; then
        echo "当前目录下没有找到匹配 '*.csv' 的文件。"
    else
        echo "处理完成。共处理了 $processed 个文件。"
    fi

    # 返回上级目录
    cd .. || {
        echo "无法返回上级目录" >&2
        exit 1
    }

done