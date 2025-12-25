#!/bin/bash

# Define source and target directories
SOURCE_DIR="TP"
TARGET_DIR="$HOME/tmp/xml"
FINAL_DIR="$HOME/TestHarness/Test_Execution/all_tcf" # 定义最终目录

# 检查最终目录是否存在
if [ ! -d "$FINAL_DIR" ]; then
    echo "Error: Directory '$FINAL_DIR' does not exist."
    exit 1 # 退出脚本
fi

# 清空最终目录
rm -rf "$FINAL_DIR"/*
echo "Cleared directory: $FINAL_DIR"

# Check if the target directory exists; create it if it doesn't
if [ ! -d "$TARGET_DIR" ]; then
    mkdir -p "$TARGET_DIR"
    echo "Created directory: $TARGET_DIR"
else
    # Remove all existing .xml files in the target directory
    find "$TARGET_DIR" -type f -name "*.xml" -exec rm -f {} \;
    echo "All existing .xml files in $TARGET_DIR have been deleted."
fi

# Recursively find all .xml files in the source directory
find "$SOURCE_DIR" -type f -name "*.xml" | while read -r xml_file; do
    # Extract the filename (without path)
    file_name=$(basename "$xml_file")

    # Copy the file to the target directory
    cp "$xml_file" "$TARGET_DIR/$file_name"
    echo "Copied file: $xml_file -> $TARGET_DIR/$file_name"
done

# 删除特定文件
rm "$TARGET_DIR/tcf_TH_09_01_01_02.xml" 2>/dev/null # 添加 2>/dev/null 避免报错信息，如果文件不存在不会输出错误
rm "$TARGET_DIR/tcf_TH_09_01_01_03.xml" 2>/dev/null

# 将 TARGET_DIR 目录下的所有文件复制到 FINAL_DIR 目录
cp "$TARGET_DIR"/* "$FINAL_DIR"/
echo "All files from $TARGET_DIR have been copied to $FINAL_DIR"

echo "All .xml files have been copied to $TARGET_DIR"
