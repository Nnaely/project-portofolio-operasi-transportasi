"""Refresh the dashboard and produce a portable portfolio without raw trip data.

Run after the analysis and PDF builder: python package_project.py
The package intentionally excludes host-specific Site identity and credentials.
"""
from pathlib import Path
import argparse
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dashboard' / 'dist'
metrics = json.loads((ROOT / 'outputs' / 'metrics.json').read_text(encoding='utf-8'))
DIST.mkdir(parents=True, exist_ok=True)
(DIST / 'data.js').write_text('window.ANALYSIS_DATA = ' + json.dumps(metrics, ensure_ascii=False, allow_nan=False) + ';\n', encoding='utf-8')
downloads = DIST / 'downloads'
downloads.mkdir(exist_ok=True)
memo = ROOT / 'reports' / 'EXECUTIVE_MEMO.pdf'
if not memo.exists():
    raise FileNotFoundError('Build reports/EXECUTIVE_MEMO.pdf before packaging.')
shutil.copy2(memo, downloads / memo.name)
memo_id = ROOT / 'reports' / 'RINGKASAN_EKSEKUTIF_ID.pdf'
if memo_id.exists():
    shutil.copy2(memo_id, downloads / memo_id.name)

archive = ROOT.parent / 'taxi-shift-economics.zip'
included = []
for path in sorted(ROOT.rglob('*')):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT)
    if any(part in {'.git', '.openai', '.vercel', '__pycache__', '.venv', '.ipynb_checkpoints', 'previews', 'tmp'} for part in rel.parts):
        continue
    if rel.parts[:2] in [('data','raw'),('data','processed')]:
        continue
    if path.suffix in {'.zip','.gz','.duckdb','.wal','.log'} or path.name == 'taxi.css':
        continue
    included.append((path, rel))
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=7) as z:
    for path, rel in included:
        z.write(path, Path('taxi-shift-economics') / rel)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert not any('/data/raw/' in name or '/.openai/' in name for name in z.namelist())
    assert any(name.endswith('EXECUTIVE_MEMO.pdf') for name in z.namelist())
shutil.copy2(archive, downloads / 'analysis-project.zip')

# Separate hosting bundle: only public assets and static-host configuration.
web_archive = ROOT.parent / 'airport-or-city-web.zip'
with zipfile.ZipFile(web_archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=7) as z:
    for path in sorted(DIST.rglob('*')):
        if path.is_file():
            z.write(path, Path('dist') / path.relative_to(DIST))
    for name in ['vercel.json', '.vercelignore']:
        z.write(ROOT / 'dashboard' / name, name)
with zipfile.ZipFile(web_archive) as z:
    assert z.testzip() is None
    assert 'dist/index.html' in z.namelist()
    assert 'dist/downloads/analysis-project.zip' in z.namelist()
    assert not any(part in {'.git', '.openai', '.vercel'} for name in z.namelist() for part in Path(name).parts)
print(json.dumps({'archive': str(archive), 'files': len(included), 'bytes': archive.stat().st_size, 'web_archive': str(web_archive), 'web_bytes': web_archive.stat().st_size}))

parser = argparse.ArgumentParser(description='Buat paket portofolio dan, bila diminta, paket lengkap dengan CSV mentah.')
parser.add_argument('--include-raw-csv', action='store_true')
args = parser.parse_args()
if args.include_raw_csv:
    manifest = json.loads((ROOT / 'data/raw_csv_manifest.json').read_text(encoding='utf-8'))
    full_archive = ROOT.parent / 'taxi-shift-economics-lengkap.zip'
    raw_paths = [ROOT / 'data/raw' / p['file'] for p in manifest['parts']]
    raw_paths.append(ROOT / 'data/raw/taxi_zone_lookup.csv')
    with zipfile.ZipFile(full_archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=4) as z:
        for path, rel in included:
            z.write(path, Path('taxi-shift-economics') / rel)
        for path in raw_paths:
            z.write(path, Path('taxi-shift-economics') / path.relative_to(ROOT))
    with zipfile.ZipFile(full_archive) as z:
        assert z.testzip() is None
        assert sum(n.endswith('.csv') and '/data/raw/' in n for n in z.namelist()) == len(raw_paths)
    print(json.dumps({'full_archive': str(full_archive), 'raw_csv_files': len(raw_paths), 'bytes': full_archive.stat().st_size}))
