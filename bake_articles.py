#!/usr/bin/env python3
"""
将导出 JSON 中的文章数据回写入 blog.html 的 DEFAULT_ARTICLES 常量，
使部署到 GitHub Pages 时其他人无需手动导入即可看到内容。

用法：
    python bake_articles.py blog.html articles-export.json
    python bake_articles.py blog.html  # 不带参数则读取 blog-articles.json
"""
import sys
import json
import re
from pathlib import Path

def main():
    html_path = Path(sys.argv[1] if len(sys.argv) > 1 else 'blog.html')
    json_path = Path(sys.argv[2] if len(sys.argv) > 2 else 'blog-articles.json')

    if not html_path.exists():
        print(f'❌ 文件不存在: {html_path}')
        return
    if not json_path.exists():
        print(f'❌ 文章 JSON 不存在: {json_path}')
        return

    html = html_path.read_text(encoding='utf-8')
    articles = json.load(json_path.open(encoding='utf-8'))

    # 规范化：支持 {articles: [...]} 或直接是数组
    if isinstance(articles, dict) and 'articles' in articles:
        articles = articles['articles']

    articles_json = json.dumps(articles, ensure_ascii=False, indent=2)
    # 缩进对齐：把 json.dumps 的 4 空格缩进转成 blog.html 里 4 空格缩进
    lines = articles_json.splitlines()
    padded = ['  ' + line for line in lines]
    articles_indented = '\n'.join(padded)

    new_default = f'const DEFAULT_ARTICLES = {articles_indented}];'

    # 用正则替换 DEFAULT_ARTICLES = [...]] 到第一个 ] 结束
    pattern = r'const DEFAULT_ARTICLES = \[[\s\S]*?\n\];'
    match = re.search(pattern, html)
    if not match:
        print('❌ 未找到 DEFAULT_ARTICLES 块，请检查 blog.html 格式')
        return

    old_block = match.group(0)
    new_html = html.replace(old_block, new_default)

    html_path.write_text(new_html, encoding='utf-8')
    print(f'✅ 已将 {len(articles)} 篇文章写入 DEFAULT_ARTICLES')
    print(f'   → {html_path}')
    print(f'   → 使用前请重新 git push 部署到 GitHub Pages')
    print()
    print('   流程：')
    print('   1. 本地 blog.html 更新内容、测试OK')
    print('   2. 管理面板 → 备份 → 导出全部数据')
    print(f'   3. 运行: python bake_articles.py blog.html {json_path.name}')
    print('   4. git push，GitHub Pages 自动部署')
    print('   5. 其他人打开即可看到你的内容 ✓')

if __name__ == '__main__':
    main()
