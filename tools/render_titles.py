"""把标题渲染成“极粗黑体 + 向右倾斜 + 贯穿斜切痕”的透明贴图（严格参照参考图风格）。
运行：python tools/render_titles.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CN_FONT = r'C:\Windows\Fonts\simhei.ttf'
EN_FONT = r'C:\Windows\Fonts\msyhbd.ttc'
OUT = os.path.join(ROOT, 'assets', 'titles')
os.makedirs(OUT, exist_ok=True)

TITLES = {
    'star':     '星穹战机',
    'clear':    '恭喜通关',
    'record':   '新纪录',
    'fail':     '任务失败',
    'tutorial': '新手教程',
}

BASE   = 210
PAD    = 90
STROKE = int(BASE*0.05)
SLEW   = 0.24

def render_cn(text):
    font = ImageFont.truetype(CN_FONT, BASE)
    tmp = Image.new('RGBA', (10, 10))
    td = ImageDraw.Draw(tmp)
    bbox = td.textbbox((0, 0), text, font=font, stroke_width=STROKE)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    W, H = tw + PAD*2, th + PAD*2
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((PAD-bbox[0], PAD-bbox[1]), text, font=font, fill=(255,255,255,255),
           stroke_width=STROKE, stroke_fill=(255,255,255,255))
    img = img.transform((W, H), Image.AFFINE, (1, -SLEW, SLEW*H, 0, 1, 0),
                        resample=Image.BICUBIC, fillcolor=(0,0,0,0))
    al = np.array(img.getchannel('A')).astype(np.float32)
    mask = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(mask)
    for (x1,y1,x2,y2) in [(W*0.10,H*0.86,W*0.95,H*0.20),
                          (W*0.08,H*0.62,W*0.60,H*0.10),
                          (W*0.30,H*0.97,W*1.02,H*0.55)]:
        md.line((x1,y1,x2,y2), fill=255, width=max(3, int(BASE*0.024)))
    m = np.array(mask).astype(np.float32)/255.0
    al = np.where(m > 0, al * (1 - m*0.60), al).astype(np.uint8)
    img.putalpha(Image.fromarray(al))
    return img

def render_en():
    font = ImageFont.truetype(EN_FONT, 58)
    lines = ['WE ARE', 'CHAMPIONS']
    tmp = Image.new('RGBA', (10, 10)); td = ImageDraw.Draw(tmp)
    tw = int(max(td.textlength(l, font=font) for l in lines)) + 4
    th = int(sum(td.textbbox((0, 0), l, font=font)[3] for l in lines)) + 4
    W, H = tw + 120, th + 120
    img = Image.new('RGBA', (W, H), (0,0,0,0)); d = ImageDraw.Draw(img)
    y = 60
    for l in lines:
        b = td.textbbox((0, 0), l, font=font)
        d.text((60-b[0], y-b[1]), l, font=font, fill=(255,255,255,255))
        y += b[3]-b[1]
    img = img.transform((W, H), Image.AFFINE, (1, -0.30, 0.30*H, 0, 1, 0),
                        resample=Image.BICUBIC, fillcolor=(0,0,0,0))
    return img

for key, text in TITLES.items():
    img = render_cn(text)
    img.save(os.path.join(OUT, key + '_title.png'))
    print(key, text, img.size)

acc = render_en()
acc.save(os.path.join(OUT, 'accent_en.png'))
print('accent_en', acc.size)

names = list(TITLES.keys())
cell = 460
sheet = Image.new('RGBA', (cell, cell*len(names)), (8, 14, 26, 255))
for i, k in enumerate(names):
    im = Image.open(os.path.join(OUT, k+'_title.png')).convert('RGBA')
    im.thumbnail((cell-40, cell-40))
    sheet.alpha_composite(im, ((cell-im.width)//2, i*cell+(cell-im.height)//2))
sheet.convert('RGB').save(os.path.join(OUT, 'titles_sheet.png'))
print('done')
