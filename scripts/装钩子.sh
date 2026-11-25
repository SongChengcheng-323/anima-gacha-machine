#!/bin/bash
# 把 pre-commit 钩子装到本仓库（新克隆的仓库需要跑一次 ✓ 钩子不在 git 里 ✗）
cp "$(dirname "$0")/pre-commit.hook" "$(git rev-parse --git-dir)/hooks/pre-commit"
chmod +x "$(git rev-parse --git-dir)/hooks/pre-commit"
echo "✓ 钩子已装（提交时会自动检查 py/js 语法 + 拦 >5MB 文件）"
