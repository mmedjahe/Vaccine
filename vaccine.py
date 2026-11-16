from urllib.parse import parse_qs, urlparse
from urllib.parse import urlencode
from urllib.parse import quote
from inject import inject_apostrophe, inject_bool
import argparse
import json

def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("-o", default="dump_db.json")
    p.add_argument("-X", default="GET")
    args = p.parse_args()
    parsed_url = urlparse(args.url)
    if(args.X != "GET" and args.X != "POST"):
        return print("Vaccine only works with GET or POST")
    path = args.o
    params =parse_qs(parsed_url.query)
    for name, values in params.items():
        data = inject_bool(name, values[0], params, parsed_url._replace(query=""), args.X)
        if data != None:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            return
        dataa = inject_apostrophe(name, values[0], params, parsed_url._replace(query=""), args.X)
        if dataa != None:
            with open(path, "w") as f:
                json.dump(dataa, f, indent=2)
            return   

main()

