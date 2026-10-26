"""Build only declared portal sources in isolation; never touch course checkouts."""
from pathlib import Path
import os, shutil, subprocess, tempfile
from safe_paths import project_files, replace_directory
ROOT=Path(__file__).resolve().parents[1]
SKIP={'.git','.quarto','_site','artifacts','node_modules','.venv','__pycache__'}
assert subprocess.check_output(['quarto','--version'],text=True).strip()=='1.10.18'
project_files(ROOT,SKIP,exclude_env=True)
subprocess.run(['python3','tests/validate.py','--source-only'],cwd=ROOT,check=True)
with tempfile.TemporaryDirectory(prefix='uso-portal-') as tmp:
    work=Path(tmp)/'portal'
    shutil.copytree(ROOT,work,ignore=lambda directory,names:[n for n in names if n in SKIP or n.startswith('.env')])
    subprocess.run(['python3','tools/catalog.py','--generate'],cwd=work,check=True)
    subprocess.run(['quarto','render'],cwd=work,env=dict(os.environ,XDG_CACHE_HOME=str(Path(tmp)/'cache')),check=True)
    subprocess.run(['python3','tests/validate.py'],cwd=work,check=True)
    replace_directory(work/'_site',ROOT,'_site')
print('PASS isolated portal render; exact validated artifact promoted')
