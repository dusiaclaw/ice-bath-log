#!/usr/bin/env python3
"""Publish lake surface temperatures from the Alplakes API in a form browsers can read.

Browsers may not call the Alplakes API directly (no CORS), so this job - run hourly by
GitHub Actions - fetches the whole-lake surface grid of EVERY 3D lake the service offers
(it asks the API which lakes exist; a built-in list is the fallback) and writes:

  OUT/index.json         one entry per lake: key, model, name, centre, bounding box
  OUT/lakes/<key>.json   thinned grid + temperatures for now and the next 48 h
  OUT/water.json         Lake Zurich only, for app versions before 1.9

Usage: python3 tools/fetch_water.py OUT_DIR"""
import json, sys, time, pathlib, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

BASE = 'https://alplakes-api.eawag.ch'
LAYER = BASE + '/simulations/layer/{model}/{lake}/{t}/0?variables=temperature'
OFFSETS_H = [0, 3, 6, 12, 24, 36, 48]
BASE_TRIES_H = [0, -1, -3, -6]     # newest hour that exists becomes "now"
MAX_CELLS = 6000                   # thin big lakes so every file stays small
MODELS = ('delft3d-flow', 'mitgcm')
FALLBACK = {'delft3d-flow': 'zurich geneva lugano biel murten greifensee hallwil ageri joux stmoritz garda caldonazzo annecy bourget'.split(),
            'mitgcm': 'neuchatel lucerne zug'.split()}
NAMES = {'ageri': 'Ägeri', 'stmoritz': 'St. Moritz', 'neuchatel': 'Neuchâtel', 'biel': 'Biel / Bienne',
         'geneva': 'Geneva', 'bourget': 'Bourget', 'joux': 'Joux'}

def get(url, tries=3):
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'ice-bath-log-data/1.1'})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except Exception as e:
            err = e; time.sleep(2 * (i + 1))
    raise err

def discover():
    """{lake key: model}. The metadata shape is not documented, so read it defensively."""
    found = {}
    try:
        meta = get(BASE + '/simulations/metadata')
        def add(model, item):
            key = item if isinstance(item, str) else (item.get('lake') or item.get('name') or item.get('key') or item.get('id')) if isinstance(item, dict) else None
            if key: found.setdefault(str(key), model)
        if isinstance(meta, dict):
            for model in MODELS:
                v = meta.get(model)
                if isinstance(v, dict):
                    for k in v: found.setdefault(k, model)
                elif isinstance(v, list):
                    for it in v: add(model, it)
        elif isinstance(meta, list):
            for it in meta:
                if isinstance(it, dict) and it.get('model') in MODELS: add(it['model'], it)
    except Exception as e:
        print('metadata failed, using built-in list:', e, file=sys.stderr)
    for model, keys in FALLBACK.items():
        for k in keys: found.setdefault(k, model)
    return found

def flat(grid):
    out = []
    for row in grid:
        out.extend(row if isinstance(row, list) else [row])
    return out

def fetch_step(model, key, t):
    j = get(LAYER.format(model=model, lake=key, t=t.strftime('%Y%m%d%H%M')), tries=2)
    ts = j.get('time') or t.isoformat()
    ms = int(datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp() * 1000)
    return flat(j['lat']), flat(j['lng']), flat(j['variables']['temperature']['data']), ms

def lake_data(key, model):
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    first = None
    for b in BASE_TRIES_H:
        try:
            first = (now + timedelta(hours=b), fetch_step(model, key, now + timedelta(hours=b))); break
        except Exception:
            continue
    if not first:
        return None
    base, (lat, lng, t0, ms0) = first
    times, temps = [ms0], [t0]
    for h in OFFSETS_H[1:]:
        try:
            la, ln, te, ms = fetch_step(model, key, base + timedelta(hours=h))
            if len(la) == len(lat):
                times.append(ms); temps.append(te)
        except Exception:
            pass
    keep = [i for i in range(len(lat)) if lat[i] is not None and lng[i] is not None and t0[i] is not None]
    if not keep:
        return None
    step = max(1, -(-len(keep) // MAX_CELLS))
    keep = keep[::step]
    r = lambda v, n: None if v is None else round(v, n)
    la = [r(lat[i], 4) for i in keep]; ln = [r(lng[i], 4) for i in keep]
    return {'model': model, 'times': times, 'lat': la, 'lng': ln, 't': [[r(s[i], 1) for i in keep] for s in temps]}

def one(item):
    key, model = item
    try:
        d = lake_data(key, model)
    except Exception as e:
        print(f'{key}: failed ({e})', file=sys.stderr); return key, None
    if d: print(f'{key}: {len(d["lat"])} cells, {len(d["times"])} times')
    else: print(f'{key}: no data', file=sys.stderr)
    return key, d

def main():
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'out')
    (out / 'lakes').mkdir(parents=True, exist_ok=True)
    lakes = discover()
    print(f'{len(lakes)} lakes to fetch: {" ".join(lakes)}')
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(one, lakes.items()))
    stamp = int(time.time() * 1000); index = []
    for key, d in results:
        if not d: continue
        d['name'] = 'Lake ' + NAMES.get(key, key.capitalize()); d['updated'] = stamp
        (out / 'lakes' / f'{key}.json').write_text(json.dumps(d, separators=(',', ':'), ensure_ascii=False))
        la, ln = d['lat'], d['lng']
        index.append({'key': key, 'model': d['model'], 'name': d['name'], 'lat': round(sum(la) / len(la), 4), 'lng': round(sum(ln) / len(ln), 4),
                      'bbox': [min(la), min(ln), max(la), max(ln)]})
        if key == 'zurich':   # compatibility with app versions 1.6-1.8
            (out / 'water.json').write_text(json.dumps({'updated': stamp, 'lakes': {'zurich': d}}, separators=(',', ':'), ensure_ascii=False))
    if not index:
        sys.exit('no lake data fetched')
    (out / 'index.json').write_text(json.dumps({'updated': stamp, 'source': 'Alplakes (EPFL, Eawag), simulated surface temperature', 'lakes': index}, separators=(',', ':'), ensure_ascii=False))

if __name__ == '__main__':
    main()
