from decimal import Decimal as D
P=["Оля","Макс","Аня","Дима","Катя"]
RATE={"11.09":D("30.00"),"12.09":D("30.50"),"13.09":D("30.50")}
A=P
# (чек, сообщения, дата, что, кто платил, сумма, валюта, возврат, на кого делим)
E=[
("R01 + R01-refund","M01,M02,M30,M32","11.09","Квартира Airbnb","Аня",D(60000),"RUB",D(5000),A),
("R02","M05","11.09","Сим-карты","Макс",D(75),"GEL",0,A),
("R03","M06","11.09","Такси из аэропорта","Макс",D(100),"GEL",0,A),
("R04","M08","11.09","Супермаркет Nikora","Дима",D(150),"GEL",0,A),
("R13","M11","11.09","Машина в Мцхету","Макс",D(278),"GEL",0,A),
("R05","M13","11.09","Ужин Barbarestan","Оля",D(400),"GEL",0,A),
("R06","M15","12.09","Экскурсия Казбеги","Макс",D(500),"GEL",0,A),
("R07","M16","12.09","Обед, хачапури","Катя",D(150),"GEL",0,A),
("R08","M17,M18,M20","12.09","Винный магазин (1 чек)","Дима",D(120),"GEL",0,A),
("R09","M21,M23","12.09","Ужин Шави Ломи","Аня",D(320),"GEL",0,["Оля","Макс","Аня","Дима"]),
("R10 + R10-refund","M25-M28","13.09","Серные бани","Катя",D(200),"GEL",D(40),["Оля","Макс","Аня","Катя"]),
("R11","M29","13.09","Завтрак","Оля",D(110),"GEL",0,A),
("R12","M33","13.09","Такси в аэропорт","Оля",D(90),"GEL",0,A),
]
TRANSFERS=[("M09,M10","Оля","Аня",D(6250))]
paid={p:D(0) for p in P}; owe={p:D(0) for p in P}; total=D(0); out=[]
f=lambda x: f"{x:,.0f}".replace(","," ")
for r,m,d,what,payer,amt,cur,ref,sh in E:
    rate=RATE[d] if cur=="GEL" else D(1); rub=(amt-ref)*rate; share=rub/len(sh); total+=rub
    paid[payer]+=rub
    for s in sh: owe[s]+=share
    cells=[f(share) if p in sh else "0" for p in P]
    out.append(f"| {r} | {m} | {d} | {what} | {payer} | {f(amt)} {cur}"+(f" - {f(ref)} возврат" if ref else "")+f" | {rate} | {f(rub)} | "+" | ".join(cells)+" |")
tr={p:D(0) for p in P}
for m,a,b,x in TRANSFERS: tr[a]+=x; tr[b]-=x
bal={p:paid[p]-owe[p]+tr[p] for p in P}
# план: сначала точные пары, потом жадно крупнейший должник -> крупнейший кредитор
b=dict(bal); plan=[]
for x in P:
    for y in P:
        if b[x]<0 and b[x]==-b[y]: plan.append((x,y,-b[x])); b[x]=b[y]=D(0)
while True:
    dr=min(P,key=lambda p:b[p]); cr=max(P,key=lambda p:b[p])
    if b[cr]<=0: break
    x=min(-b[dr],b[cr]); plan.append((dr,cr,x)); b[dr]+=x; b[cr]-=x
# проверки контрольных фактов
exp={"Оля":-2245,"Макс":2245,"Аня":31915,"Дима":-17215,"Катя":-14700}
assert all(bal[p]==exp[p] for p in P), bal
assert sum(bal.values())==0 and total==129315 and len(plan)<=len(P)-1
assert set(plan)=={("Оля","Макс",2245),("Дима","Аня",17215),("Катя","Аня",14700)}
hdr="| Чек | Сообщения | Дата | Трата | Платил | Сумма | Курс | ₽ | "+" | ".join(P)+" |\n|"+"---|"*(8+len(P))
with open("03_table.md","w") as o:
    o.write("# Таблица расчётов\n\n## Траты и доли (₽)\n\n"+hdr+"\n"+"\n".join(out)+f"\n| **Итого** | | | | | | | **{f(total)}** | "+" | ".join(f(owe[p]) for p in P)+" |\n\n")
    o.write("## Балансы\n\n| Участник | Заплатил | Доля | Перевод в поездке | Баланс |\n|---|---|---|---|---|\n")
    for p in P: o.write(f"| {p} | {f(paid[p])} | {f(owe[p])} | {('+' if tr[p]>0 else '')+f(tr[p]) if tr[p] else '0'} (M09) | **{('+' if bal[p]>0 else '')+f(bal[p])}** |\n".replace(" (M09)","" if not tr[p] else " (M09)"))
    o.write(f"| **Сумма** | {f(sum(paid.values()))} | {f(sum(owe.values()))} | 0 | **{f(sum(bal.values()))}** |\n\n## План переводов\n\n| # | Кто | Кому | Сумма |\n|---|---|---|---|\n")
    for i,(x,y,z) in enumerate(plan,1): o.write(f"| {i} | {x} | {y} | {f(z)} ₽ |\n")
import csv
with open("03_table.csv","w",newline="") as c:
    w=csv.writer(c); w.writerow(["Чек","Сообщения","Дата","Трата","Платил","Сумма","Валюта","Возврат","Курс","RUB"]+P)
    for r,m,d,what,payer,amt,cur,ref,sh in E:
        rate=RATE[d] if cur=="GEL" else D(1); rub=(amt-ref)*rate
        w.writerow([r,m,d,what,payer,amt,cur,ref,rate,rub]+[rub/len(sh) if p in sh else 0 for p in P])
print("ALL CONTROL FACTS PASS; total",total,"plan",plan)
