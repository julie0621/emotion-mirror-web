#!/usr/bin/env python
import subprocess, os, urllib.request, json, base64

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(ROOT, "push_log.txt")

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

log("=== STARTING ===")

# Read the current file
with open(os.path.join(ROOT, "api", "index.py"), "r", encoding="utf-8") as f:
    content = f.read()

# Try git push first
os.chdir(ROOT)
log("cwd: " + os.getcwd())

# Check git status
r = subprocess.run(["git", "status"], capture_output=True, text=True)
log("status: rc=" + str(r.returncode))
log("stdout: " + r.stdout)
log("stderr: " + r.stderr)

# Add and commit
r = subprocess.run(["git", "add", "-A"], capture_output=True, text=True)
log("add: rc=" + str(r.returncode) + " err=" + r.stderr)

r = subprocess.run(["git", "commit", "-m", "add user memory"], capture_output=True, text=True)
log("commit: rc=" + str(r.returncode) + " out=" + r.stdout + " err=" + r.stderr)

# Push
r = subprocess.run(["git", "push"], capture_output=True, text=True)
log("push: rc=" + str(r.returncode) + " out=" + r.stdout + " err=" + r.stderr)

log("=== DONE ===")
