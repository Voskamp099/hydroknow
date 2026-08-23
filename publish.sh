#!/bin/bash
# ============================================================
# 氢知 HydroKnow · 一键发布脚本
# 用法: bash publish.sh   （在仓库根目录下运行）
#
# 做什么:
#   1. 重新构建纯前端静态版（读取 data/ 下 PDF → 语料 → dist/index.html）
#   2. 更新 gh-pages 分支并推送到 GitHub
#   3. GitHub Pages 自动重新构建，约 1-3 分钟后在线更新
#
# 链接（长期稳定）:
#   https://voskamp099.github.io/hydroknow/
# ============================================================
set -e
cd "$(dirname "$0")"

PY=/Users/raelynn/.workbuddy/binaries/python/envs/default/bin/python

echo "== 1/3 重新构建静态版 =="
$PY build_static.py

echo "== 2/3 推送到 gh-pages =="
CUR=$(git branch --show-current)
git checkout -q gh-pages
cp dist/index.html index.html
if ! git diff --quiet index.html; then
  git add index.html
  git commit -q -m "update: online demo refresh $(date '+%m-%d %H:%M')"
  git push -q origin gh-pages
  echo "  （已推送新版本）"
else
  echo "  （内容无变化，跳过推送）"
fi
git checkout -q "$CUR"

echo "== 3/3 完成 =="
echo "在线 Demo 约 1-3 分钟后更新："
echo "  https://voskamp099.github.io/hydroknow/"
