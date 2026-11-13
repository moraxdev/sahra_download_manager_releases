"""Publish a Windows build to the update feed.

python3 publish.py windows <app.exe> <build> <version> --key <update-key.pem> [--setup <setup.exe>] [--notes "..."] [--force] [--min <build>]

Signs the one-file exe with the project's Ed25519 key (the app installs only signed builds),
copies the files under files/, and rewrites update.json. Never put the key in this repo.
"""
import argparse, json, shutil, os
from cryptography.hazmat.primitives.serialization import load_pem_private_key

RAW = "https://raw.githubusercontent.com/moraxdev/sahra_download_manager_releases/main/"
a = argparse.ArgumentParser()
a.add_argument("platform", choices=["windows"])
a.add_argument("exe"); a.add_argument("build", type=int); a.add_argument("version")
a.add_argument("--key", required=True); a.add_argument("--setup"); a.add_argument("--notes", default="")
a.add_argument("--force", action="store_true"); a.add_argument("--min", type=int, default=0)
o = a.parse_args()
here = os.path.dirname(os.path.abspath(__file__))
key = load_pem_private_key(open(o.key, "rb").read(), None)
name = f"sahra-download-manager-{o.version}.exe"
shutil.copy(o.exe, os.path.join(here, "files", name))
data = open(o.exe, "rb").read()
sig = key.sign(data).hex()
path = os.path.join(here, "update.json")
feed = json.load(open(path)) if os.path.exists(path) else {}
entry = {"build": o.build, "version": o.version, "notes": o.notes, "force": o.force, "minBuild": o.min,
         "url": RAW + "files/" + name, "signature": sig, "size": len(data),
         "onefile": {"url": RAW + "files/" + name, "signature": sig}}
if o.setup:
    sname = f"Sahra-Download-Manager-Setup-{o.version}.exe"
    shutil.copy(o.setup, os.path.join(here, "files", sname))
    entry["setup"] = RAW + "files/" + sname
# Keep only the current files.
keep = {name, f"Sahra-Download-Manager-Setup-{o.version}.exe"}
for f in os.listdir(os.path.join(here, "files")):
    if f not in keep:
        os.remove(os.path.join(here, "files", f))
feed[o.platform] = entry
json.dump(feed, open(path, "w"), indent=2)
print(f"published {o.platform} {o.version} build {o.build}")
