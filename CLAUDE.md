# Greece & Italy 2026 — Trip Site

Single-file trip-planning website for a 4-person Greece & Italy trip, **July 9 – August 1, 2026**.

**Live site:** https://jml-53.github.io/greece-italy-2026/
**This repo is PUBLIC and served by GitHub Pages from the `main` branch root — every file added here becomes publicly downloadable. Never add receipts, planning documents, or any personal/health information about travelers.** Working documents live in the private companion repo `JML-53/greece-italy-planning`.

## Travelers
Joe (trip organizer) and his wife **Teri**; their friends **Lorene and Carla, who are sisters** (not a couple, and not related to Joe/Teri).
⚠️ Common AI error from past sessions: swapping Teri and Lorene. **Teri is Joe's wife.**

## Workflow
1. Edit `index.html` directly — it is the entire site. **No build step, no dependencies.**
2. Commit and push via plain `git` CLI to `main` (`git add` / `git commit` / `git push origin main`). No GitHub Desktop, no `gh`.
3. GitHub Pages redeploys automatically (~1 min). Joe reviews on the live site.
4. Keep commit messages meaningful and short.

## File Architecture — `index.html`
~133 KB self-contained HTML with inline CSS and JS.

**Tabs:** Overview · Must-Book Now · Full Itinerary · Interactive Map · Hotels · Cruise Excursions · Transportation · Tips & Packing · ⚡ Quick Ref
(A consolidation to ~6 tabs is planned — see the private planning repo, Site-Evolution-Plan.)

**Key JavaScript (single `<script>` block):**
- `const stops=[...]` — 52 stops: `{grp, cat, region, lat, lng, title, sub, note, wiki}`
- `catStyles`, `_regions`, `_types`, `_regionStops` — map pin styling + filter config
- `_doInitMap()` / `_gmCard(s)` / `_fetchWikiPhoto(article)` — map init, info cards, Wikipedia photos
- `_buildFilters()` / `gmTreeFilter()` — sidebar filter tree
- `showTab(id,el)` — tab switching + lazy map init (note: it is wrapped/extended near the end of the script)
- `renderItinDays()`-style code builds day cards into `#itin-days`

**Stop categories (`cat`):** `hotel-booked`, `hotel-tbd`, `tour-booked`, `cruise`, `stop`, `alternate`, `transport`

## Google Maps API
Key in the script tag is **domain-locked to `https://jml-53.github.io/*`** — it will not work on localhost or other domains (by design; safe to be visible in source).
Init pattern: API calls `initGoogleMap()` → `_gmLoaded=true` → `_doInitMap()` when map tab opens.

## Wikipedia photos
Fetched on pin click via the `pageimages` API using each stop's `wiki` field (empty string = no photo).

## Pending / Known Items
- **Rome hotel** — not yet booked (3 nights Jul 29–31, needs parking)
- **Optional bookings:** Vatican Scavi, Pantheon, Orvieto Underground, Assisi Mass reservation
- **During trip (Jul 9–Aug 1):** Claude Code cloud sessions handle itinerary updates by phone prompt; keep changes small and V&V'd
- **Post-trip:** interactive Trip Log tab (GPS tracks + photos + journal) — design in private planning repo

## V&V Protocol — run after ANY edit to index.html
1. `grep -c "wiki:'" index.html` → must equal 52 (or the updated stop count; update this file if stops are added)
2. Verify key functions still present: `_fetchWikiPhoto`, `gmTreeFilter`, `showTab`, `_doInitMap`
3. Spot-check the edited content landed (grep for the new text)
4. Watch JS apostrophe escaping inside single-quoted strings — past bug source
5. Confirm the page has no obvious truncation: file should end with `</html>`
