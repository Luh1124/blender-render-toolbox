#!/bin/bash  

# 脚本名称: run_example.sh  
# 描述: 执行基本的渲染脚本
# 作者: 李宏
# 日期: 2024-10-15  
# 版本: 1.0

# 主程序逻辑  
echo "开始执行脚本..."  

# 渲染脚本
~/blender/blender-3.5.1-linux-x64/blender -b -P example.py

echo "脚本执行完毕。" 