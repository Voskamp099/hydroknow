#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业知识与智能服务助手 — CLI 入口（兼容旧路径）

批量跑预设问题，终端打印答案 + 生成静态 demo.html。
Web 模式请运行: python app.py

用法:
  python run.py
  python run.py --question "沐光氢能成立于哪一年？"
"""

import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# 直接复用 run_cli 的完整实现
from run_cli import main

if __name__ == "__main__":
    main()
