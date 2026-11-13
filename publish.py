"""Publish a Windows build to the update feed.

python3 publish.py windows <Setup.exe> <build> <version> --key <update-key.pem> [--notes "..."] [--force] [--min <build>]

Signs the setup with the project's Ed25519 key (the app installs only signed updates: it runs
the setup quietly), copies it under files/, and rewrites update.json. Never put the key in this repo.
"""
import argparse, json, shutil, os
from cryptography.hazmat.primitives.serialization import load_pem_private_key

RAW = "https://raw.githubusercontent.com/moraxdev/sahra_download_manager_releases/main/"
a = argparse.ArgumentParser()
a.add_argument("platform", choices=["windows"])
a.add_argument("exe"); a.add_argument("build", type=int); a.add_argument("version")
a.add_argument("--key", required=True); a.add_argument("--notes", default="")
a.add_argument("--force", action="store_true"); a.add_argument("--min", type=int, default=0)
o = a.parse_args()
here = os.path.dirname(os.path.abspath(__file__))
key = load_pem_private_key(open(o.key, "rb").read(), None)
name = f"Sahra-Download-Manager-Setup-{o.version}.exe"
shutil.copy(o.exe, os.path.join(here, "files", name))
data = open(o.exe, "rb").read()
for f in os.listdir(os.path.join(here, "files")):
    if f != name:
        os.remove(os.path.join(here, "files", f))
path = os.path.join(here, "update.json")
feed = json.load(open(path)) if os.path.exists(path) else {}
# No "url"/"onefile": versions before 0.2.1 replaced their own exe and must be reinstalled from the setup.
feed[o.platform] = {"build": o.build, "version": o.version, "notes": o.notes, "force": o.force, "minBuild": o.min,
                    "setup": {"url": RAW + "files/" + name, "signature": key.sign(data).hex(), "size": len(data)}}
json.dump(feed, open(path, "w"), indent=2)
print(f"published {o.platform} {o.version} build {o.build}")
