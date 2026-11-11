"""Report-ready, readable graph panels with exact IDs and no crossed links."""
from PIL import Image,ImageDraw,ImageFont
from mining_io import ROOT,read_json,write_json,sha256

FONT='C:/Windows/Fonts/msyh.ttc'
def wrap(draw,text,font,width):
    lines=[];line=''
    for ch in text:
        if ch=='\n' or draw.textlength(line+ch,font=font)>width:
            lines.append(line);line='' if ch=='\n' else ch
        else:line+=ch
    return lines+[line]

def panel(path,title,subtitle,blocks):
    f=ImageFont.truetype(FONT,38);big=ImageFont.truetype(FONT,48)
    draw=ImageDraw.Draw(Image.new('RGB',(1,1)))
    groups=[wrap(draw,text,f,1620) for text in blocks]
    heights=[len(lines)*54+50 for lines in groups]
    height=250+sum(heights)+30*len(groups)
    im=Image.new('RGB',(1800,height),'white');d=ImageDraw.Draw(im)
    d.text((70,35),title,font=big,fill='#183344')
    d.text((70,100),subtitle,font=f,fill='#405c6a');y=180
    for lines,h in zip(groups,heights):
        d.rounded_rectangle((60,y,1740,y+h),radius=16,fill='#edf4f7',outline='#9db6c4',width=2)
        for i,line in enumerate(lines):d.text((85,y+25+54*i),line,font=f,fill='#183344')
        y+=h+30
    im.save(path)
    return dict(file=path.relative_to(ROOT).as_posix(),size=list(im.size),sha256=sha256(path),labels_truncated=False)

def main():
    out=ROOT/'results/figures/report_panels';out.mkdir(exist_ok=True)
    graph=read_json(ROOT/'data/outputs/graph.json');routes=read_json(ROOT/'data/outputs/routes.json')['routes']
    cat={e['entity_id']:e['canonical_name'] for e in read_json(ROOT/'data/outputs/entities.json')['entity_catalog']}
    rows=[];captions=[]
    for route in routes:
        for offset in range(0,len(route['steps']),5):
            chosen=route['steps'][offset:offset+5];blocks=[]
            for s in chosen:
                role='交通活动（未具名站点，不建虚假POI）' if s.get('step_kind')=='transport_activity' else '候选活动' if s.get('step_kind')=='candidate_activity' else '路线活动'
                blocks.append(f"步骤{s['step_no']} / {s['time_text'] or '时间未知'} / {s['poi_name']}\n{role}；{s['activity']}\n证据："+'；'.join(f"{e['doc_id']}[{e['start']},{e['end']})" for e in s['evidence']))
            name=f"route_{route['route_id']}_{offset//5+1}.png";caption=f"图6-分{len(rows)+1} {route['route_name']}，步骤{chosen[0]['step_no']}—{chosen[-1]['step_no']}"
            meaning='候选活动按原文顺序排列，非必经链' if route.get('sequence_semantics')=='source_order_only' else '按原文叙述顺序；时间不是实时班次'
            record=panel(out/name,'路线与交通活动分图',meaning,blocks);record.update(route_id=route['route_id'],step_numbers=[s['step_no'] for s in chosen]);rows.append(record);captions.append((caption,name))
    advice=read_json(ROOT/'data/outputs/advice.json')['advice']
    labels={'condition_reference':'条件涉及','suggestion_reference':'建议正文涉及','comparison_reference':'比较对象（非推荐）','supporting_context':'补充上下文'}
    for offset in range(0,len(advice),2):
        chosen=advice[offset:offset+2];blocks=[]
        for a in chosen:
            roles='；'.join(labels[r['role']]+'：'+cat[r['entity_id']]+('〔子句含否定〕' if r['polarity']=='negative' else '') for r in a['entity_roles']) or '无可对齐实体'
            blocks.append(a['advice_id']+'\n条件 → 建议：'+a['condition_text']+' → '+a['suggestion_text']+'\n实体角色：'+roles+'\n证据：'+'；'.join(f"{e['doc_id']}[{e['start']},{e['end']})" for e in a['evidence']))
        name=f'advice_{offset//2+1}.png';caption=f'图6-分{len(rows)+1} 条件建议与实体角色，记录{offset+1}—{offset+len(chosen)}'
        record=panel(out/name,'条件建议与实体角色分图','关联不等于必访或交通许可；历史信息须另行核实',blocks);record['advice_ids']=[a['advice_id'] for a in chosen];rows.append(record);captions.append((caption,name))
    index=['# 报告分图索引','','所有33个路线/交通步骤和21条建议均列入分图。分图展示完整图谱中的路线链与条件建议关系，未声称每页都是全图；原全图另保留。PNG宽1800像素，文字不截断，可按页插入Word。HTML副本是静态图与可检索关系表，不是可拖动网络。','']
    for caption,name in captions:index += [caption,'',f'![{caption}]({name})','']
    (out/'README.md').write_text('\n'.join(index),encoding='utf-8')
    write_json(ROOT/'results/checks/exp06_report_panels.json',dict(graph_sha256=sha256(ROOT/'data/outputs/graph.json'),panels=rows,route_steps=sum(len(r['steps']) for r in routes),advice=len(advice)))
    print('报告分图',len(rows),'张；步骤和建议全覆盖。')

if __name__=='__main__':main()
