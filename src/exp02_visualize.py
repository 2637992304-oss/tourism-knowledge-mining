"""实验2彩色统计图。Pillow绘图，不依赖在线服务或模型。"""
from collections import Counter
import csv
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from exp02_entities import ROOT,TYPES,read_json,write_json

COLORS={'POI':'#3478B9','TRANSPORT':'#E58B35','TIME':'#4B9B75'}


def font(size):
    candidates=[os.environ.get('EXP02_FONT',''),str(Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/simsun.ttc'),
                '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',
                '/System/Library/Fonts/Supplemental/Songti.ttc']
    for p in candidates:
        if p and Path(p).is_file(): return ImageFont.truetype(p,size)
    raise FileNotFoundError('缺少中文字体，请设置EXP02_FONT为字体文件路径')


def label(draw,xy,text,size=32,anchor=None):
    draw.text(xy,text,font=font(size),fill='black',anchor=anchor)


def frequency(output,path):
    im=Image.new('RGB',(1500,1420),'white'); d=ImageDraw.Draw(im)
    title='图2-1  初版词频与噪声' if output['variant']=='baseline' else '图2-2  三类实体词频（优化后）'
    label(d,(70,35),title,46)
    label(d,(70,100),'原文提及次数；同一实体按景区分别计数；每类前6项',30)
    catalog={e['entity_id']:e for e in output['entity_catalog']}
    counts=Counter(m['entity_id'] for m in output['mentions'])
    titles={'POI':'POI 景点与命名地点','TRANSPORT':'TRANSPORT 交通方式','TIME':'TIME 时间节点与时长'}
    for j,t in enumerate(TYPES):
        y=170+j*400; label(d,(70,y),titles[t],38)
        top=[(e,n) for e,n in counts.most_common() if catalog[e]['entity_type']==t][:6]
        peak=max(n for _,n in top)
        for k,(eid,n) in enumerate(top):
            yy=y+62+k*48; e=catalog[eid]; name=e['canonical_name']
            label(d,(70,yy),e['scenic_id']+' '+name,30)
            start=650; width=int(n/peak*650)
            d.rectangle((start,yy+3,start+width,yy+33),fill=COLORS[t])
            label(d,(start+width+16,yy),str(n),30)
        d.line((650,y+52,650,y+354),fill='#B8B8B8',width=2)
    label(d,(70,1380),'S001 箱根   S002 优胜美地   S003 蓝山；各类纵轴分别排序，横轴单位为次。',26)
    im.save(path,dpi=(240,240))


def compare(baseline,optimized,review,path):
    im=Image.new('RGB',(1500,840),'white'); d=ImageDraw.Draw(im)
    label(d,(70,35),'图2-3  词典与规则迭代的实测对比',46)
    label(d,(70,105),'左：相同原文范围内的提及数；右：24例开发诊断集的P / R / F1',29)
    colors=['#AAB8C6','#3478B9']; legends=['初版 v0','优化 v1']
    for j in range(2):
        d.rectangle((80+j*280,170,116+j*280,198),fill=colors[j]); label(d,(130+j*280,167),legends[j],29)
    # Count bars are on a count axis, evaluation bars on a separate percentage axis.
    for i,t in enumerate(TYPES):
        x=100+i*220; label(d,(x+65,625),t,28,anchor='mt')
        for j,s in enumerate([baseline,optimized]):
            n=s['by_type'][t]; height=n/1000*340
            xx=x+j*75; d.rectangle((xx,600-height,xx+57,600),fill=colors[j]); label(d,(xx+28,585-height),str(n),27,anchor='mb')
    label(d,(80,680),'提及数减少可来自去噪和重叠消除；增加可来自补充词典。',25)
    names=['precision','recall','f1']
    for i,name in enumerate(names):
        x=830+i*200; label(d,(x+60,625),['P','R','F1'][i],30,anchor='mt')
        for j,v in enumerate(['baseline','optimized']):
            n=review[v]['metrics'][name]; height=n*340; xx=x+j*70
            d.rectangle((xx,600-height,xx+54,600),fill=colors[j]); label(d,(xx+27,585-height),f'{n:.1%}',26,anchor='mb')
    d.line((75,600,745,600),fill='black',width=2); d.line((800,600,1440,600),fill='black',width=2)
    label(d,(70,742),'参考实体84处；严格匹配字符位置、类型与标准名称。抽样用于开发诊断，不能代表全语料质量。',27)
    label(d,(70,787),'三景区各8例；由AI辅助逐例语义核验；初版和优化版使用同一范围与同一参考标签。',27)
    im.save(path,dpi=(240,240))


def main():
    output=read_json(ROOT/'data/outputs/entities.json')
    baseline=read_json(ROOT/'results/checks/exp02_baseline_stats.json')
    optimized=read_json(ROOT/'results/checks/exp02_optimized_stats.json')
    review=read_json(ROOT/'results/checks/exp02_review.json')
    dest=ROOT/'results/figures'; dest.mkdir(exist_ok=True)
    frequency(read_json(ROOT/'results/checks/exp02_baseline_entities.json'),dest/'exp02_baseline_frequency.png')
    frequency(output,dest/'exp02_entity_frequency.png')
    compare(baseline,optimized,review,dest/'exp02_iteration_comparison.png')
    with (ROOT/'results/checks/exp02_scenic_density.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f); w.writerow(['scenic_id','scoped_chars','entity_type','mentions','mentions_per_10000_chars'])
        for s in optimized['per_scenic']:
            for t in TYPES:
                n=s['mentions_by_type'][t]; w.writerow([s['scenic_id'],s['scoped_chars'],t,n,round(n/s['scoped_chars']*10000,3)])
    print('已生成3张彩色图与按正文长度归一化的统计表。')


if __name__=='__main__': main()
