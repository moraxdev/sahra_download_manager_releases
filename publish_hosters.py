"""Publish the file-hoster rules (hosters.json) with its signature; apps pick it up within a day.

python3 publish_hosters.py <hosters.json> --key <update-key.pem>
Raise "version" in the file for every change. Never put the key in this repo.
"""
import argparse, json, os, shutil
from cryptography.hazmat.primitives.serialization import load_pem_private_key
a = argparse.ArgumentParser(); a.add_argument("rules"); a.add_argument("--key", required=True); o = a.parse_args()
here = os.path.dirname(os.path.abspath(__file__))
data = open(o.rules, "rb").read()
v = json.loads(data)["version"]
shutil.copy(o.rules, os.path.join(here, "hosters.json"))
open(os.path.join(here, "hosters.sig"), "w").write(load_pem_private_key(open(o.key, "rb").read(), None).sign(data).hex())
print(f"published hoster rules v{v}")
