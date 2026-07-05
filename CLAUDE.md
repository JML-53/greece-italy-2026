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

**Tabs (6):** Overview · Bookings · Full Itinerary · Interactive Map · Transportation · ⚡ Quick Ref
(Consolidated from 9 on Jul 5: Hotels→Bookings, Cruise Excursions→itinerary day cards via `excEmbedHtml()`, Tips & Packing→Quick Ref. Mobile ≤680px uses a fixed bottom nav `#bottomnav`/`navTab()` instead of top tabs. During Jul 9–Aug 1 `initTripMode()` opens today's itinerary card and shows "Day N of 24" in the header; `[data-expires]` alerts auto-hide after their date.)

**Key JavaScript (single `<script>` block):**

⚠️ **A2 single-source booking data (added Jul 5) — edit the DATA, never the rendered HTML.** Between the `/* ===== A2 DATA ===== */` and `/* ===== A2 END ===== */` markers:
- `hotels[]` — 9 entries `{ord, city, tbl, when, nights, name, addr, phone?, conf, pin?, bookedBy?, rooms?, checkin, checkout, extras[], price?, cancel?, cancelWarn?, status:'booked'|'tbd'}`. Renders BOTH the Bookings "Hotels At a Glance" table (`#bk-hoteltable`) and the hotel cards in `#bk-cards`. One edit updates both.
- `carRental` — the Hertz card.
- `tourBookings[]` — tours/tickets `{ord, payOrd, icon, title, when, body, payDate, payLabel, num, amt}`. Renders BOTH the Overview payment table (`#ov-paytable`, sorted by `payOrd`) and tour cards in `#bk-cards` (sorted by `ord`). The refund row has `noCard:true`.
- `tripTimeline[]` — 24 rows `{d, w, loc, b:''|'bb'|'bg'|'by', note}` → Overview timeline table (`#ov-timeline`).
- `needsBooking[]` — still-needed cards `{icon, title, when, tag:'ph'|'pm', tagText, body}` → `#bk-needs`.
- `ord` values use gaps of 10 — insert new bookings between existing ones without renumbering.
- When a pending booking lands (e.g. Rome hotel): update `hotels[]` status/details, remove/adjust the `needsBooking[]` entry, and check `tripTimeline[]` notes.
- **Regression test:** `tests/a2-render-regression.test.js` in the private planning repo — update its expected counts when bookings change, and run it after data edits.

- `const stops=[...]` — 59 stops: `{grp, cat, region, lat, lng, title, sub, note, wiki}`
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

## trip-stops.kml — MUST stay in sync with stops[]
`trip-stops.kml` in this repo is generated from the `stops[]` array in index.html and is linked from Quick Ref (offline My Maps backup). **Whenever stops are added/removed/edited in index.html, regenerate `trip-stops.kml` to match and commit both files together.**

## ⚠️ Mount-staleness hazard (Cowork sessions) — MANDATORY pre-commit check
The Cowork bash sandbox reads the repo through a mount that can serve STALE or TRUNCATED file content and stat metadata (observed 2026-07-05: a truncated index.html was committed and briefly broke the live site; later a stale CLAUDE.md dropped this very section).
Before EVERY commit in a Cowork session:
1. `touch <file>` before `git add` (stat cache lies; without this, edits silently fail to stage)
2. After `git add`, verify the STAGED content, not the worktree: `git show :index.html | tail -c 20` must end with `</html>`, and `git show :index.html | grep -c "wiki:'"` must equal the expected stop count. For other files, grep the staged copy for BOTH the newest change AND a known older marker — staleness shows up as the old marker missing.
3. GATE the commit on those checks — run them as separate commands and abort if wrong; do not chain check+commit with `&&`
4. If staged content is truncated/stale: STOP — do not commit. Fallback: clone fresh to /tmp with the PAT, apply the change there, verify, push from /tmp, then `cp` the pushed files back over the mount and confirm the host copy matches
5. After any incident, resync local refs: fetch + `git update-ref refs/heads/main FETCH_HEAD` (do NOT `git reset --hard` through the mount)
Claude Code cloud sessions clone directly from GitHub and are immune to this — the hazard is Cowork-local only.
