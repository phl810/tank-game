"""从坦克参考图里把每辆坦克从背景分离，生成透明 PNG。
白底图用“白色阈值”；渐变色底图用小容差 flood fill。
"""
import os, glob
import numpy as np
from PIL import Image
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, 'assets', 'tanks')

def flood_bg(a, tol):
    h, w = a.shape[:2]
    bg = np.zeros((h, w), bool); seen = np.zeros((h, w), bool); q = deque()
    def add(y, x):
        if not seen[y, x]: seen[y, x] = True; q.append((y, x))
    for x in range(w): add(0, x); add(h-1, x)
    for y in range(h): add(y, 0); add(y, w-1)
    t2 = tol*tol
    while q:
        y, x = q.popleft(); c = a[y, x]; bg[y, x] = True
        for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny, nx = y+dy, x+dx
            if 0 <= ny < h and 0 <= nx < w and not seen[ny, nx]:
                d = a[ny, nx] - c
                if d[0]*d[0]+d[1]*d[1]+d[2]*d[2] <= t2:
                    seen[ny, nx] = True; q.append((ny, nx))
    return bg

def comps(mask):
    h, w = mask.shape; lab = np.full((h, w), -1, np.int32); out = []
    for y in range(h):
        for x in range(w):
            if mask[y, x] and lab[y, x] < 0:
                cid = len(out); lab[y, x] = cid; st = [(y, x)]
                area=0; x0=x1=x; y0=y1=y
                while st:
                    cy, cx = st.pop(); area += 1
                    if cx<x0:x0=cx
                    if cx>x1:x1=cx
                    if cy<y0:y0=cy
                    if cy>y1:y1=cy
                    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny,nx=cy+dy,cx+dx
                        if 0<=ny<h and 0<=nx<w and mask[ny,nx] and lab[ny,nx]<0:
                            lab[ny,nx]=cid; st.append((ny,nx))
                out.append((area,x0,y0,x1,y1,cid))
    return out, lab

all_sprites = []
for i, f in enumerate(sorted(glob.glob(os.path.join(DIR,'src*.png'))), 1):
    im = Image.open(f).convert('RGB'); W,H = im.size
    arr = np.asarray(im).astype(np.int32)
    r,g,b = arr[...,0], arr[...,1], arr[...,2]
    if i >= 3:
        mx = np.maximum(np.maximum(r,g),b); mn = np.minimum(np.minimum(r,g),b)
        bg = (mn >= 232) & ((mx-mn) < 45)
    else:
        bg = flood_bg(arr, 14)
    fg = ~bg
    cs, lab = comps(fg)
    cs = [c for c in cs if c[0] >= 1500 and (c[4]-c[2]) >= 55]
    cs.sort(key=lambda c: (c[2], c[1]))
    print('图%d 前景组件(过滤后)= %d' % (i, len(cs)))
    for j,(area,x0,y0,x1,y1,cid) in enumerate(cs):
        pad=6; cx0=max(0,x0-pad); cy0=max(0,y0-pad); cx1=min(W,x1+pad); cy1=min(H,y1+pad)
        sub = lab[cy0:cy1, cx0:cx1]
        alpha = np.where(sub==cid, 255, 0).astype(np.uint8)
        crop = im.crop((cx0,cy0,cx1,cy1))
        rgba = np.dstack([np.asarray(crop).astype(np.uint8), alpha])
        name = 'tank_%d_%02d.png' % (i, j)
        Image.fromarray(rgba,'RGBA').save(os.path.join(DIR,name))
        all_sprites.append((name, area))
        print('    ', name, 'area', area)

cell=280; cols=6; rows=max(1,(len(all_sprites)+cols-1)//cols)
sheet = Image.new('RGBA',(cols*cell, rows*cell),(14,20,30,255))
for k,(name,*_ ) in enumerate(all_sprites):
    s=Image.open(os.path.join(DIR,name)).convert('RGBA'); s.thumbnail((cell-16,cell-24))
    cx=(k%cols)*cell+(cell-s.width)//2; cy=(k//cols)*cell+(cell-s.height)//2
    sheet.alpha_composite(s,(cx,cy))
sheet.convert('RGB').save(os.path.join(DIR,'tanks_sheet.png'))
print('总览已生成；共', len(all_sprites), '个坦克')
