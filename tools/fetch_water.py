#!/usr/bin/env python3
"""Fetch whole-lake surface temperature grids from the Alplakes API and write one
compact JSON file the app can read (browsers may not call the API directly).
Usage: python3 tools/fetch_water.py OUTPUT.json"""
import json, sys, time, pathlib, urllib.request
from datetime import datetime, timedelta, timezone

API = 'https://alplakes-api.eawag.ch/simulations/layer/{model}/{lake}/{t}/0?variables=temperature'
OFFSETS_H = [0, 3, 6, 12, 24, 36, 48]

def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'ice-bath-log-data/1.0'})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            err = e; time.sleep(3 * (i + 1))
    raise err

def flat(grid):
    out = []
    for row in grid:
        out.extend(row if isinstance(row, list) else [row])
    return out

def lake_data(key, model):
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    lat = lng = None; times = []; temps = []
    for h in OFFSETS_H:
        t = now + timedelta(hours=h)
        try:
            j = get(API.format(model=model, lake=key, t=t.strftime('%Y%m%d%H%M')))
        except Exception as e:
            print(f'{key} +{h}h failed: {e}', file=sys.stderr); continue
        la, ln, te = flat(j['lat']), flat(j['lng']), flat(j['variables']['temperature']['data'])
        if lat is None:
            lat, lng = la, ln
        elif len(la) != len(lat):
            continue
        ts = j.get('time') or t.isoformat()
        times.append(int(datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp() * 1000))
        temps.append(te)
    if lat is None:
        return None
    keep = [i for i in range(len(lat)) if lat[i] is not None and lng[i] is not None and temps[0][i] is not None]
    r = lambda v, n: None if v is None else round(v, n)
    return {'model': model, 'times': times,
            'lat': [r(lat[i], 5) for i in keep], 'lng': [r(lng[i], 5) for i in keep],
            't': [[r(series[i], 2) for i in keep] for series in temps]}

def main():
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'water.json')
    cfg = pathlib.Path(__file__).with_name('lakes.txt').read_text().splitlines()
    lakes = {}
    for line in cfg:
        line = line.split('#')[0].split()
        if len(line) == 2:
            d = lake_data(*line)
            if d: lakes[line[0]] = d; print(f'{line[0]}: {len(d["lat"])} cells, {len(d["times"])} times')
    if not lakes:
        sys.exit('no lake data fetched')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'updated': int(time.time() * 1000), 'source': 'Alplakes (EPFL, Eawag), simulated surface temperature', 'lakes': lakes}, separators=(',', ':')))

if __name__ == '__main__':
    main()
