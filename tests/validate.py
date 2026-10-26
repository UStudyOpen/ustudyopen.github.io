"""Validate catalog, immutable design/tools, legal output, routes and private-file exclusion."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import argparse,hashlib,json,re,sys
import legal_distribution,licensing
from safe_paths import project_files
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from catalog import validate

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__(); self.ids=set(); self.refs=[]; self.themes=set(); self.duplicates=[]; self.main=0; self.h1=0; self.lang=False; self.title=False; self.missing_alt=[]; self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):
            ident=a['id']; native=tag=='link' and ident.startswith('quarto-')
            if ident in self.ids and not native: self.duplicates.append(ident)
            self.ids.add(ident)
        if tag=='link' and a.get('id')=='quarto-bootstrap': self.themes.add(a.get('data-mode'))
        if tag=='main': self.main+=1
        if tag=='h1': self.h1+=1
        if tag=='html': self.lang=a.get('lang','').startswith('es')
        if tag=='title': self.title=True
        if tag=='img' and 'alt' not in a: self.missing_alt.append(a.get('src'))
        for k in ('href','src','poster'):
            if k in a:self.refs.append(a[k])


def source(errors):
    validate(json.loads((ROOT/'data/catalog.json').read_text()))
    errors.extend(licensing.validate(ROOT))
    for manifest,base in [('design-vendor.json',ROOT/'_extensions/ustudyopen-design'),('platform-vendor.json',ROOT)]:
        m=json.loads((ROOT/manifest).read_text())
        for n,h in m['files'].items():
            f=base/n
            if not f.is_file() or f.is_symlink() or hashlib.sha256(f.read_bytes()).hexdigest()!=h:errors.append('modified vendor: '+n)
    pins=json.loads((ROOT/'tests/action-pins.json').read_text())
    for f in (ROOT/'.github/workflows').glob('*.yml'):
        text=f.read_text()
        for action,sha in re.findall(r'uses:\s*([^\s@]+)@([^\s#]+)',text):
            if not re.fullmatch('[0-9a-f]{40}',sha) or pins[action]['sha']!=sha:errors.append('unlocked action '+action)
        if any(x in text for x in ('pull_request_target','write-all','contents: write','secrets.')):errors.append('excessive workflow privileges')
        if f.name=='validate.yml' and ('pages: write' in text or 'id-token: write' in text):errors.append('PR has deploy privileges')
        if f.name=='deploy.yml':
            for guard in ("vars.USO_PAGES_ENABLED == 'true'","github.ref == 'refs/heads/main'",'needs: build','environment:','github-pages'):
                if guard not in text: errors.append('missing deploy guard '+guard)
            if 'pull_request:' in text: errors.append('PR deployment forbidden')
    assert 'site-url: https://ustudyopen.github.io/' in (ROOT/'_quarto.yml').read_text()


def output(errors):
    legal_distribution.output_checks(ROOT,errors)
    site=ROOT/'_site'; files=project_files(site)
    pages={f.resolve():Page(f.read_text()) for f in files if f.suffix=='.html'}
    assert {f.relative_to(site).as_posix() for f in pages}=={'index.html','proyecto.html','licencias.html'}, 'unexpected public HTML routes'
    refs=0
    for path,page in pages.items():
        assert page.main==1 and page.h1==1 and page.lang and page.title, 'invalid semantic structure '+path.name
        assert page.themes=={'light','dark'} and not page.duplicates and not page.missing_alt, 'invalid themes/IDs/alt '+path.name
        text=path.read_text()
        assert not re.search(r'file:///|/home/|/tmp/|https?://(?:localhost|127\.0\.0\.1)',text), 'private machine path'
        assert 'cdn.jsdelivr.net/npm/mathjax' not in text, 'portal has no academic formulas to typeset'
        for ref in page.refs:
            u=urlsplit(ref)
            if u.scheme or u.netloc:continue
            refs+=1
            dest=(site/unquote(u.path).lstrip('/')).resolve() if u.path.startswith('/') else (path.parent/unquote(u.path)).resolve() if u.path else path
            if dest.is_dir():dest/='index.html'
            assert dest.is_relative_to(site) and dest.is_file(), f'broken/escaping resource {path.name}: {ref}'
            if u.fragment and dest in pages: assert unquote(u.fragment) in pages[dest].ids, 'broken anchor '+ref
    for f in files:
        rel=f.relative_to(site)
        assert not f.is_symlink() and not any(n in {'.git','.github','tests','tools','data','artifacts','node_modules','.quarto','__pycache__','docs','.venv'} or n.startswith('.env') for n in rel.parts), 'private/unpublishable file '+str(rel)
        assert f.suffix not in {'.qmd','.py','.pem','.key','.zip','.bib'} and f.name not in {'AGENTS.md','README.md','PUBLISHING.md','VALIDATION.md','catalog.json'}, 'source in artifact '+str(rel)
        if f.suffix=='.css':
            for ref in re.findall(r'url\(\s*[\'\"]?([^\)\'\"]+)',f.read_text()):
                u=urlsplit(ref)
                if u.scheme or u.netloc or not u.path:continue
                dest=(f.parent/unquote(u.path)).resolve()
                assert dest.is_relative_to(site) and dest.is_file(), 'missing CSS dependency '+ref
    c=json.loads((ROOT/'data/catalog.json').read_text())
    home=(site/'index.html').read_text()
    for course in c['courses']:
        assert f'href="{course["url"]}"' in home and f'id="course-{course["slug"]}"' in home, 'missing generated course'
    assert home.count('class="course-card"')==len(c['courses']), 'catalog/render mismatch'
    print(f'PASS output: {len(pages)} pages, {refs} local references; resources, legal hashes, themes and private-file exclusion')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source-only',action='store_true');args=parser.parse_args();errors=[]
    try:
        source(errors)
        if not args.source_only:output(errors)
    except (AssertionError,OSError,ValueError,KeyError,TypeError) as e:errors.append(str(e))
    report={'errors':errors,'scope':'technical validation; no academic review inferred'}
    (ROOT/'artifacts').mkdir(exist_ok=True);(ROOT/'artifacts/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2));sys.exit(bool(errors))
