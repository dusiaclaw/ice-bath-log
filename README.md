# Ice Bath Log

A small installable web app for cold-water swimming clubs: current water and air temperature for your own spot, a daily dip suggestion, a timed dip recorder (walk-to-water countdown, in-water timer, **voice stop** so you don't need to touch the wet screen), per-person statistics and an optional shared Google Sheet.

No account, no ads, no tracking. Data stays on the phone unless you set up the Sheet.

## Install (Android / Chrome)
Open the app's web address in Chrome → menu → **Install app**. Microphone (voice stop) only works over https.

## First start
The app asks for your club name (and optional logo), your city and lake, and the club members. Everything can be changed later in **Settings**.

## Shared Google Sheet (optional)
Settings › Shared Sheet explains the one-time Apps Script setup. Anyone with the web-app URL can read and add rows, so share it only inside the club.

## Water data feed
Browsers are not allowed to read the Alplakes API directly, so `.github/workflows/water-data.yml` runs every hour, fetches the surface-temperature grid of every lake listed in `tools/lakes.txt` and publishes it as `water.json` on the `data` branch. The app reads it from `raw.githubusercontent.com/<owner>/<repo>/data/water.json`. Add a line to `tools/lakes.txt` for your lake. Forks: enable Actions once in the repo's Actions tab.

## Releasing a new version
1. Edit `APP_VERSION` and add an entry to `CHANGELOG` in `index.html`.
2. Run `python3 make-version.py` (writes `version.json`, bumps the cache name in `sw.js`, writes `CHANGELOG.md`).
3. Commit and push. Installed apps show an update pop-up at the next start.

## Data sources
Lake temperature: [Alplakes](https://www.alplakes.eawag.ch) (EPFL, Eawag; simulated data). Measuring stations: BAFU via [existenz.ch](https://api.existenz.ch). Weather and place search: [Open-Meteo](https://open-meteo.com).

## License
GPL-3.0 – see `LICENSE`. Icons: [Tabler Icons](https://tabler.io/icons) (MIT). Map: [Leaflet](https://leafletjs.com) (BSD-2, in `lib/`) with © OpenStreetMap contributors.
