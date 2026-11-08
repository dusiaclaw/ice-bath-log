# Changelog

## v2.0 (2026-11-08)
- Settings › Water temperature source: choose Automatic, lake model, measuring station, average of both, or typed by hand, with the current readings side by side.
- Advanced conditions (button on Conditions): 48-hour water, air and wind curves, readings of all sources, whole-lake coldest/average/warmest, temperature by depth, sunrise, sunset, UV and rain.
- Settings › Permissions & tests: allow and test microphone, voice recognition, sound, screen-on and camera. Offered once after first-time setup.
- Measuring stations are now read through the data feed (the direct call was blocked by browsers).
- Fixed: the dip wrap-up screen no longer jumps back to the top when you tap a feeling or Standing/Swimming.
- Fixed: voice keyword now asks for microphone access first, so Chrome shows the permission prompt.

## v1.9 (2026-11-08)
- Water temperature now works for every lake of the Alplakes service, not only Lake Zurich: the hourly data job publishes all lakes and the app picks the ones near your swimming spot. Lakes outside the service can still be used with hand-entered temperatures.

## v1.8 (2026-11-08)
- Fixed: on the dip wrap-up screen the feeling icons no longer push the page out of the window.

## v1.7 (2026-11-08)
- Privacy: Test connection no longer contains a built-in example location; without a saved spot it tests the middle of Lake Zurich.

## v1.6 (2026-11-08)
- Water temperature fixed: phones may not read the lake service directly, so an hourly job in the GitHub repo now publishes the lake temperatures and the app reads them from there. Spots saved as "lake not listed" are linked to their lake again.

## v1.5 (2026-11-08)
- New app icon (lake at dawn). It is also shown in the top bar and in About when no club logo is set.

## v1.4 (2026-11-08)
- Settings › Test connection: calls every data source from your phone and shows the exact answer or error.
- Settings › Install app on this phone.

## v1.3 (2026-11-08)
- Water temperature: the lake model is now linked reliably (the app uses the nearest model point and tells you how far it is); a spot saved without a lake is repaired automatically; measuring stations without temperature data are no longer used.

## v1.2 (2026-11-08)
- Swimming spot: a map with a draggable pin (or tap the map) to place your exact spot; weather and lake data follow the pin.

## v1.1 (2026-11-08)
- Top bar shows the app name with its version; burger menu stays at the top right.

## v1.0 (2026-11-08)
- First release: water and air temperature for your own swimming spot, daily dip suggestions, timed dips with a walk-to-water countdown and voice stop, standing or swimming per person, photos, statistics, optional shared Google Sheet.
- First-time setup for club name, logo, city and lake, and members.
- Themes, light/dark mode, icon style, backups, license and changelog in Settings. Update pop-up when a new version is available.

