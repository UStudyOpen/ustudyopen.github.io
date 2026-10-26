"""A single, offline catalog with verifiable course metadata; no visitor API calls."""
from pathlib import Path
from html import escape
import argparse
import hashlib
import json
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('name', 'slug', 'status', 'license', 'authorship', 'pages', 'planned')
STATES = {'en-desarrollo': 'En desarrollo · revisión pendiente', 'lista': 'Lista · revisión declarada'}


def projection(course):
    return {key: course[key] for key in FIELDS}


def validate(catalog):
    assert catalog['schema'] == 1 and catalog['courses'], 'empty/incompatible catalog'
    slugs = set()
    for c in catalog['courses']:
        slug = c['slug']
        assert re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', slug) and slug not in slugs, 'invalid/duplicate slug'
        slugs.add(slug)
        assert c['url'] == f'https://ustudyopen.github.io/{slug}/', 'course URL must use its own project path'
        assert c['publication'] == 'publicado', 'only published sites belong in this catalog'
        assert c['name'].strip() and c['area'].strip() and c['summary'].strip(), 'missing presentation metadata'
        src = c['source']; m = src['metadata']
        assert src['repository'] == 'UStudyOpen/' + slug, 'source repository mismatch'
        assert re.fullmatch('[0-9a-f]{40}', src['commit']), 'source must be pinned to commit'
        assert re.fullmatch('[0-9a-f]{64}', src['sha256']), 'missing source digest'
        assert (m['slug'], m['name'], m['status']) == (slug, c['name'], c['academic_status']), 'source metadata disagreement'
        assert m['license'] and m['authorship'] and m['pages'], 'missing academic/legal metadata'
        paths=set()
        for page in m['pages']:
            assert page['path'] not in paths, 'duplicate page'
            paths.add(page['path'])
            assert page['status'] in {'lista', 'en-desarrollo', 'proximamente'} and type(page['reviewed']) is bool, 'invalid page state'
            assert page['status'] != 'lista' or page['reviewed'], 'ready page requires human review'
        assert all(t['status'] == 'proximamente' for t in m['planned']), 'invalid planned state'
        required = [page for page in m['pages'] if page.get('required', True)]
        ready = bool(required) and all(x['status'] == 'lista' and x['reviewed'] for x in required) and not any(x.get('required', True) for x in m['planned'])
        assert c['academic_status'] == ('lista' if ready else 'en-desarrollo'), 'academic completion cannot follow site publication'
    return catalog


def generate(catalog):
    parts = ['```{=html}', '<div class="course-grid">']
    for i, c in enumerate(catalog['courses'], 1):
        e = {k: escape(c[k], quote=True) for k in ('slug','name','area','summary','url','academic_status')}
        parts.append(f'''<article class="course-card" aria-labelledby="course-{e['slug']}">
<div class="course-top"><span class="course-area">{e['area']}</span><span class="course-number" aria-hidden="true">{i:02}</span></div>
<h3 id="course-{e['slug']}">{e['name']}</h3><p class="course-summary">{e['summary']}</p>
<div class="course-states"><span class="published">Sitio publicado</span><span class="uso-status uso-status--{e['academic_status']}">{STATES[c['academic_status']]}</span></div>
<a class="course-link" href="{e['url']}" aria-label="Explorar el curso: {e['name']}">Explorar el curso <span aria-hidden="true">↗</span></a>
</article>''')
    parts += ['</div>', '```', '']
    (ROOT / '_catalog.qmd').write_text('\n'.join(parts))


def verify_sources(catalog):
    for c in catalog['courses']:
        s = c['source']
        url = f"https://raw.githubusercontent.com/{s['repository']}/{s['commit']}/course.yml"
        raw = urllib.request.urlopen(url, timeout=30).read()
        assert hashlib.sha256(raw).hexdigest() == s['sha256'], 'pinned course hash mismatch'
        assert projection(json.loads(raw)['course']) == s['metadata'], 'pinned academic snapshot mismatch'
        response=urllib.request.urlopen(c['url'],timeout=30)
        assert response.status == 200, 'course site unavailable'
        print(f"PASS source + public site: {c['slug']}")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--generate',action='store_true')
    parser.add_argument('--verify-sources',action='store_true')
    parser.add_argument('--import-course',type=Path,help='local clean course checkout')
    parser.add_argument('--area')
    parser.add_argument('--summary')
    args=parser.parse_args()
    path=ROOT/'data/catalog.json'; catalog=json.loads(path.read_text())
    if args.import_course:
        repo=args.import_course.resolve()
        assert args.area and args.summary, '--area and --summary are required'
        assert not subprocess.check_output(['git','status','--porcelain','--','course.yml'],cwd=repo), 'commit metadata before importing'
        raw=(repo/'course.yml').read_bytes(); m=json.loads(raw)['course']; slug=m['slug']
        entry={'slug':slug,'name':m['name'],'area':args.area,'summary':args.summary,'url':f'https://ustudyopen.github.io/{slug}/','publication':'publicado','academic_status':m['status'],'source':{'repository':'UStudyOpen/'+slug,'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'sha256':hashlib.sha256(raw).hexdigest(),'metadata':projection(m)}}
        catalog['courses']=[entry if c['slug']==slug else c for c in catalog['courses']] if any(c['slug']==slug for c in catalog['courses']) else catalog['courses']+[entry]
        validate(catalog)
        # Verify publication and pinned public provenance before changing the catalog.
        verify_sources({'courses':[entry]})
        path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    validate(catalog)
    if args.generate: generate(catalog)
    if args.verify_sources: verify_sources(catalog)
    print(f"PASS catalog: {len(catalog['courses'])} verified metadata entries")

if __name__ == '__main__': main()
