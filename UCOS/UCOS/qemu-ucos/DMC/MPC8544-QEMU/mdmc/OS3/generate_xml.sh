#!/bin/bash

# 检查是否有参数传入
if [ -n "$1" ]; then
    # 如果有参数，检查参数是否为有效目录
    if [ -d "$1" ]; then
        # 进入指定目录
        echo "进入指定目录: $1"
        cd "$1" || exit 1  # 如果目录不存在或无法进入，退出脚本
    else
        echo "错误：指定的目录不存在！"
        exit 1
    fi
else
    echo "未指定目录，将在当前目录下操作。"
fi

# 遍历当前目录下的所有.c文件
for c_file in *.c; do
    # 获取不带后缀的文件名
    base_name=$(basename "$c_file" .c)
    
    # 替换文件名中的 "tp_" 为 "tcf_"
    new_name=$(echo "$base_name" | sed 's/tp_/tcf_/')
    
    # 生成对应的.xml文件名
    xml_file="${new_name}.xml"
    
    # 写入指定内容到.xml文件，并确保末尾有一个换行符
    cat <<EOF > "$xml_file"
<test_set version="2">
  <test_procedure component="MOS_HM">
    <test tp_name="$base_name" tp_file_name="$c_file">
    </test>
  </test_procedure>
  <test_attributes>
    <reboot before="no" after="no" />
    <!-- max_timeout value in seconds -->
    <max_timeout value="DEFAULT" />
    <description></description>
  </test_attributes>
</test_set>
EOF

    # 确保文件末尾有一个换行符
    echo "" >> "$xml_file"

    echo "生成文件：$xml_file"
done

echo "所有.c文件对应的.xml文件已生成完毕！"
