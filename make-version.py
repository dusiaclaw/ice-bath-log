#!/usr/bin/env python3
"""Run after every release: reads APP_VERSION + CHANGELOG from index.html,
writes version.json (the in-app update signal), bumps the cache name in sw.js
and writes CHANGELOG.md."""
import json, re, pathlib
root = pathlib.Path(__file__).parent
html = (root / 'index.html').read_text(encoding='utf-8')
ver = re.search(r"const APP_VERSION='([^']+)'", html).group(1)
log = json.loads(re.search(r"/\*CHANGELOG\*/const CHANGELOG=(.*?);/\*END\*/", html, re.S).group(1))
cur = next(c for c in log if c['v'] == ver)
(root / 'version.json').write_text(json.dumps({'version': ver, 'date': cur.get('date', ''), 'notes': cur['notes']}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
sw = root / 'sw.js'
sw.write_text(re.sub(r"const CACHE='[^']*'", f"const CACHE='ice-bath-log-{ver}'", sw.read_text(encoding='utf-8')), encoding='utf-8')
md = '# Changelog\n\n' + ''.join(f"## v{c['v']} ({c.get('date','')})\n" + ''.join(f'- {n}\n' for n in c['notes']) + '\n' for c in log)
(root / 'CHANGELOG.md').write_text(md, encoding='utf-8')
print('version', ver, 'written')
