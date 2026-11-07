"""主展示景区完整图谱PNG和可检索的静态HTML；不遗漏条件/建议节点。"""
import argparse
import html
import math
import os
from collections import Counter
from PIL import Image,ImageDraw,ImageFont
from mining_io import ROOT,read_json,write_json,sha256

COLORS={'SCENIC':'#194b70','ROUTE':'#376b96','STEP':'#e5f0f7','POI':'#dceee1','TIME':'#fff0ce','TRANSPORT':'#e9e1f6','CONDITION':'#f9e0d6','ADVICE':'#d8edf0'}
RELATIONS={'HAS_ROUTE':'#476a88','HAS_STEP':'#7c99ae','NEXT_STEP':'#c68a26','VISITS':'#43805c','AT_TIME':'#bb942f','USES_TRANSPORT':'#8b6fa6','HAS_ADVICE':'#67a2ac','TRIGGERS':'#c16b4d','APPLIES_TO':'#218d9d'}


def wrapped(draw,text,font,width):
    lines=[];line=''
    for char in text:
        if char=='\n':
            lines.append(line);line='';continue
        if draw.textlength(line+char,font=font)>width and line:lines.append(line);line=''
        line+=char
    return lines+[line]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--font',default=os.environ.get('MINING_FONT','C:/Windows/Fonts/msyh.ttc'));args=p.parse_args()
    data=read_json(ROOT/'data/outputs/graph.json');nodes=[n for n in data['nodes'] if n['scenic_id']=='S001'];ids={n['node_id'] for n in nodes}
    edges=[e for e in data['edges'] if e['source'] in ids and e['target'] in ids]
    font=ImageFont.truetype(args.font,23);small=ImageFont.truetype(args.font,18);title=ImageFont.truetype(args.font,44)
    groups=[['SCENIC'],['ROUTE'],['STEP'],['POI'],['TIME','TRANSPORT'],['CONDITION'],['ADVICE']]
    width=4500;box_width=520;gap=640
    dummy=ImageDraw.Draw(Image.new('RGB',(1,1)))
    labels={};heights={}
    for n in nodes:
        text=n['name']
        if n['node_type']=='STEP':text=f"{'官方' if 'OFF' in n['attributes']['route_id'] else '游客'} 步骤{n['attributes']['step_no']} / {n['attributes']['time_text'] or 'unknown'}\n"+text
        if n['node_type']=='ROUTE':text=n['attributes']['route_id']+'\n'+text
        labels[n['node_id']]=wrapped(dummy,text,font,box_width-34)
        heights[n['node_id']]=max(84,36+31*len(labels[n['node_id']]))
    columns=[[n for n in nodes if n['node_type'] in g] for g in groups]
    height=max(sum(heights[n['node_id']]+32 for n in col) for col in columns)+480
    im=Image.new('RGB',(width,height),'#f8fafc');draw=ImageDraw.Draw(im)
    draw.text((55,30),'实验6 · 箱根完整程序性知识图谱',font=title,fill='#183344')
    draw.text((55,95),f"graph {data['graph_version']} / {len(nodes)}节点 / {len(edges)}边 / 条件与建议已融合；所有箱根节点均展示",font=font,fill='#536476')
    positions={}
    for col,items in enumerate(columns):
        total=sum(heights[n['node_id']]+32 for n in items);y=330+(height-440-total)/2
        for n in items:
            h=heights[n['node_id']];positions[n['node_id']]=(320+col*gap,y+h/2);y+=h+32
    for e in edges:
        x,y=positions[e['source']];tx,ty=positions[e['target']]
        if x==tx:
            x-=box_width/2+12;tx=x;start=(x,y);end=(tx,ty-15)
        elif x<tx:start=(x+box_width/2,y);end=(tx-box_width/2,ty)
        else:start=(x-box_width/2,y);end=(tx+box_width/2,ty)
        color=RELATIONS[e['relation']];draw.line((start,end),fill=color,width=3)
        angle=math.atan2(end[1]-start[1],end[0]-start[0]);ex,ey=end
        draw.polygon([(ex,ey),(ex-12*math.cos(angle-.4),ey-12*math.sin(angle-.4)),(ex-12*math.cos(angle+.4),ey-12*math.sin(angle+.4))],fill=color)
    for n in nodes:
        x,y=positions[n['node_id']];h=heights[n['node_id']];kind=n['node_type'];dark=kind in {'SCENIC','ROUTE'}
        draw.rounded_rectangle((x-box_width/2,y-h/2,x+box_width/2,y+h/2),radius=13,fill=COLORS[kind],outline='#a8bbc7',width=2)
        for i,line in enumerate(labels[n['node_id']]):draw.text((x-box_width/2+17,y-h/2+16+i*31),line,font=font,fill='white' if dark else '#183344')
    for i,(kind,color) in enumerate(COLORS.items()):
        x=55+i*540;draw.rectangle((x,162,x+26,188),fill=color);draw.text((x+38,158),kind,font=font,fill='#183344')
    for i,(rel,color) in enumerate(RELATIONS.items()):
        x=55+(i%5)*870;y=220+(i//5)*42;draw.line((x,y+13,x+45,y+13),fill=color,width=5);draw.text((x+55,y),rel,font=font,fill='#183344')
    draw.text((55,height-70),'APPLIES_TO = 条件证据涉及的实体；不表示必访、允许使用或整体人群适用。来源与完整ID见同名HTML。',font=font,fill='#536476')
    out=ROOT/'results/figures';im.save(out/'exp06_hakone_graph.png')
    # Companion is a self-contained inspectable table with all edges and anchors; no hosted dependencies.
    rows=['<!doctype html><html lang="zh"><meta charset="utf-8"><title>箱根完整知识图谱</title><style>body{font:16px system-ui;margin:30px;color:#183344}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd7df;padding:10px;text-align:left}pre{white-space:pre-wrap}a{color:#14758b}</style><h1>箱根完整知识图谱</h1><p>所有节点、边及来源；浏览器查找可搜索ID。APPLIES_TO表示证据相关。</p><img src="exp06_hakone_graph.png" style="width:100%"><h2>节点</h2><table><tr><th>节点</th><th>内容与来源</th></tr>']
    for n in nodes:rows.append(f'<tr id="{html.escape(n["node_id"])}"><td>{html.escape(n["node_type"]+" / "+n["node_id"])}</td><td><pre>{html.escape(n["name"])}</pre>{html.escape(str(n["source_refs"]))}</td></tr>')
    rows.append('</table><h2>边</h2><table><tr><th>关系</th><th>起点</th><th>终点</th></tr>')
    for e in edges:rows.append('<tr><td>'+html.escape(e['relation'])+'</td>'+''.join(f'<td><a href="#{html.escape(e[k])}">{html.escape(e[k])}</a></td>' for k in ['source','target'])+'</tr>')
    rows.append('</table></html>');(out/'exp06_hakone_graph.html').write_text('\n'.join(rows),encoding='utf8')
    write_json(ROOT/'results/checks/exp06_visualization.json',{'graph_sha256':sha256(ROOT/'data/outputs/graph.json'),'scenic_id':'S001','nodes':len(nodes),'edges':len(edges),'node_types':dict(Counter(n['node_type'] for n in nodes)),'all_nodes_positioned':set(positions)==ids,'image_size':[width,height],'labels_truncated':False})
    print(f'saved full S001 graph: {len(nodes)} nodes, {len(edges)} edges, {width}x{height}')


if __name__=='__main__':main()
