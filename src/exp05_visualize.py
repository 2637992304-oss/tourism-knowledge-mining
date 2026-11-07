"""实际条件类型/游客类型分组统计；unspecified不等于general。"""
import argparse
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from mining_io import ROOT,read_json


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--font',default=os.environ.get('MINING_FONT','C:/Windows/Fonts/msyh.ttc'));args=p.parse_args()
    f=ImageFont.truetype(args.font,26);title=ImageFont.truetype(args.font,38)
    data=read_json(ROOT/'data/outputs/advice.json');stats=data['statistics']
    im=Image.new('RGB',(1600,1000),'#f6f8fc');d=ImageDraw.Draw(im)
    d.text((60,35),'实验5 · 条件建议分类统计',font=title,fill='#183344')
    d.text((60,95),f"18篇相关范围 / {stats['advice']}条 / v1；多标签人群按标签计数",font=f,fill='#536476')
    groups=[('condition_types',['weather','visitor_type','time','crowding','other'],160),('visitor_types',['elderly','family','couple','general','other','unspecified'],560)]
    for key,labels,y0 in groups:
        d.text((60,y0),'条件类型' if key=='condition_types' else '适用人群（unspecified=原文未明确）',font=f,fill='#183344')
        maxv=max(stats[key].values(),default=1)
        for i,label in enumerate(labels):
            y=y0+55+i*48;value=stats[key].get(label,0);w=1100*value/maxv
            d.text((60,y),label,font=f,fill='#183344');d.rectangle((290,y,290+w,y+31),fill='#3d81b2' if key=='condition_types' else '#49977d')
            d.text((305+w,y),str(value),font=f,fill='#183344')
    d.text((60,945),'统计不代表抽取准确率；来源与失败例见 exp05_review.md。',font=f,fill='#536476')
    out=ROOT/'results/figures/exp05_advice_statistics.png';out.parent.mkdir(exist_ok=True,parents=True);im.save(out);print(out.name)


if __name__=='__main__':main()
