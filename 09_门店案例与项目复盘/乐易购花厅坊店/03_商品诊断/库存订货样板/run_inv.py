from python_calamine import CalamineWorkbook
from datetime import date
from collections import defaultdict
import csv
base="09_门店案例与项目复盘/乐易购花厅坊店/99_原始素材/01_门店数据材料/"
inv=CalamineWorkbook.from_path(base+"库存积压报表_方便食品_20260508.xls").get_sheet_by_index(0).to_python()
flow=CalamineWorkbook.from_path(base+"方便食品_花厅坊商品明细_20260311-0612.xls").get_sheet_by_index(0).to_python()
def num(x):
    try: return float(str(x).strip())
    except: return None
def bk(x):
    s=str(x).strip(); return s[:-2] if s.endswith(".0") else s
def isbar(x):
    s=bk(x); return s.isdigit() and len(s)>=8
# 流水聚合: 货号idx3 销售日期idx8 销量idx9
qty=defaultdict(float); days=defaultdict(set)
for r in flow[7:]:
    if len(r)<10 or not isbar(r[3]): continue
    q=num(r[9])
    if q is None: continue
    k=bk(r[3]); qty[k]+=q; days[k].add(str(r[8]))
PERIOD=94
# 库存: bar4 name7 price9 cur10 psales11 psamt14 pgm15 lastsale17 cost28 backlogcost31
rows=[]; dropped={"负库存":0,"价异常":0,"空":0}
for r in inv[5:]:
    if len(r)<32 or not isbar(r[4]): dropped["空"]+=1; continue
    cur=num(r[10]); price=num(r[9]); psales=num(r[11]); psamt=num(r[14]); pgm=num(r[15])
    cost=num(r[28]); blc=num(r[31])
    if cur is None or cur<0: dropped["负库存"]+=1; continue
    if price is None or price<=0: dropped["价异常"]+=1; continue
    bar=bk(r[4]); name=str(r[7]); lastsale=str(r[17])[:10]
    dq=qty.get(bar,0.0); daily=dq/PERIOD if dq else 0
    dos=round(cur/daily,1) if daily>0 else (9999 if cur>0 else 0)
    gm=round(pgm/psamt,3) if (psamt and psamt>0) else None
    backlog=blc if blc is not None else cur*(cost or 0)
    try:
        y,m,d=[int(x) for x in lastsale.split("-")]; gap=(date(2026,5,8)-date(y,m,d)).days
    except: gap=None
    stale=(gap is not None and gap>30 and cur>0)
    rows.append(dict(bar=bar,name=name,abc="",cur=cur,price=price,psales=psales or 0,psamt=round(psamt or 0,1),
        gm=gm,daily=round(daily,3),dos=dos,dd=len(days.get(bar,set())),lastsale=lastsale,gap=gap,
        backlog=round(backlog or 0,1),stale=stale))
if not rows:
    print("无有效行"); raise SystemExit
rows.sort(key=lambda x:-x["psamt"]); tot=sum(x["psamt"] for x in rows) or 1; cum=0
for x in rows:
    cum+=x["psamt"]; rr=cum/tot; x["abc"]="A" if rr<=0.7 else("B" if rr<=0.9 else "C")
nstale=sum(1 for x in rows if x["stale"]); blacklog=sum(x["backlog"] for x in rows if x["stale"])
zero=sum(1 for x in rows if x["cur"]==0); slow=[x for x in rows if x["dos"]>90 and x["cur"]>0]
invtot=sum(x["backlog"] for x in rows)
print(f"有效SKU={len(rows)} 剔除={dropped} 库存总积压成本≈{invtot:.0f}元")
print(f"ABC: A={sum(1 for x in rows if x['abc']=='A')} B={sum(1 for x in rows if x['abc']=='B')} C={sum(1 for x in rows if x['abc']=='C')} | 当前库存=0(疑似缺货)={zero}")
print(f"呆滞(最近售>30天且有货)={nstale}款 积压成本≈{blacklog:.0f}元 | 慢周转(DOS>90)={len(slow)}款")
print("=== 呆滞TOP10(按积压成本) ===")
for x in sorted([r for r in rows if r['stale']],key=lambda x:-x['backlog'])[:10]:
    print(f"  {x['name'][:16]:<16} 库存{x['cur']:.0f} 售前{x['gap']}天 积压{x['backlog']:.0f}元 {x['abc']}类 DOS={x['dos']}")
print("=== 缺货疑似(库存=0但期间有销) ===")
for x in [r for r in rows if r['cur']==0 and r['psales']>0][:10]:
    print(f"  {x['name'][:16]:<16} 期间销{x['psales']:.0f} {x['abc']}类")
out="09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/库存订货样板/方便食品_库存订货_SKU明细_v0.1.csv"
with open(out,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("CSV:",out)
