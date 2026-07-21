#!/usr/bin/env python
import subprocess, sys, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# git add
r = subprocess.run(["git", "add", "-A"], capture_output=True, text=True)
print("add:", r.returncode, r.stdout, r.stderr)

# git commit
r = subprocess.run(["git", "commit", "-m", "add user memory"], capture_output=True, text=True)
print("commit:", r.returncode, r.stdout, r.stderr)

# git push
r = subprocess.run(["git", "push"], capture_output=True, text=True)
print("push:", r.returncode, r.stdout, r.stderr)

# Final status
r = subprocess.run(["git", "status"], capture_output=True, text=True)
print("status:", r.returncode, r.stdout, r.stderr)
