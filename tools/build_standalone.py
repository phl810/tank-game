"""把 index.html 的所有 assets 图片内嵌为 base64，生成可单文件运行/托管的 pilotwar_standalone.html。
运行：python tools/build_standalone.py
"""
import os, re, base64

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'pilotwar_standalone.html')

html = open(SRC, encoding='utf-8').read()

def repl(m):
    path = m.group(0)
    fp = os.path.join(ROOT, *path.split('/'))
    if os.path.exists(fp):
        data = base64.b64encode(open(fp, 'rb').read()).decode()
        return 'data:image/png;base64,' + data
    return path

# 替换所有 assets/xxx.png 的字符串
html = re.sub(r'assets/[A-Za-z0-9_./\-\u4e00-\u9fff]+\.png', repl, html)

# 处理动态拼接的标题贴图路径
title_src = {}
for k in ['star','clear','record','fail','tutorial']:
    fp = os.path.join(ROOT, 'assets','titles', k+'_title.png')
    if os.path.exists(fp):
        title_src[k] = 'data:image/png;base64,' + base64.b64encode(open(fp,'rb').read()).decode()
needle = "im.src = 'assets/titles/' + TITLE_MAP[k] + '_title.png';"
repl_js = "im.src = (" + str(title_src) + ")[TITLE_MAP[k]];"
html = html.replace(needle, repl_js)

open(OUT, 'w', encoding='utf-8').write(html)
print('生成', OUT, '大小(KB)=', round(os.path.getsize(OUT)/1024))
