import subprocess
import os
from pathlib import Path

def run(cmd):
  return subprocess.check_output(cmd).decode("utf-8").strip()

with open("system_service_template", "r") as f:
  template = f.read()

python_interp = run(["poetry", "run", "which", "python3"])

pwd = Path(run(["pwd"]))
script = pwd / ".." / "flatten.py"
script = script.resolve()
user = run(["whoami"])

xauth = os.getenv("XAUTHORITY")
disp = os.getenv("DISPLAY")

system_script = template.replace('{PYTHON_INTERPRETER}', '"' + python_interp + '"')
system_script = system_script.replace('{PYTHON_SCRIPT}', '"' + str(script) + '"')
system_script = system_script.replace('{SERVICE_USER}', user)
system_script = system_script.replace('{DISPLAY}', disp)
system_script = system_script.replace('{XAUTHORITY}', xauth)

with open("spotify_folder_flattener.service", "w") as f:
  f.write(system_script)
