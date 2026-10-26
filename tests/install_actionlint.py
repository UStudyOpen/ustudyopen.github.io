"""Download the exact actionlint archive; extract only its verified executable."""
from pathlib import Path
import hashlib,io,json,tarfile,urllib.request
root=Path(__file__).resolve().parents[1]
lock=json.loads((root/'tests/actionlint-lock.json').read_text())
raw=urllib.request.urlopen(lock['url'],timeout=60).read()
assert hashlib.sha256(raw).hexdigest()==lock['sha256'], 'actionlint digest mismatch'
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as tar:
    info=tar.getmember('actionlint');assert info.isfile()
    binary=tar.extractfile(info).read()
out=root/'artifacts/tools/actionlint';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(binary);out.chmod(0o755)
