# Bike Ops — project notes

Single-file static site (`index.html`, no build step) deployed to GitHub Pages at
<https://sonnnnnion.github.io/bike-ops/> from `github.com/sonnnnnion/bike-ops`.

## Dev server

Port **8848**, configured in `.claude/launch.json`:

```
preview_start name="bike-ops"   →  http://localhost:8848/index.html
```

**Serve over HTTP, not `file://`.** The preview pane renders `file://` paths outside the
project folder as *frozen snapshots* — it silently ignores edits, drops query strings,
and reports stale values (this cost real debugging time: a `todayISO()` fix and a hash
route both appeared broken when they were already correct on disk). Add a cache-busting
query (`?v=2`) after editing, and confirm anything surprising against disk with `grep`
before believing the browser.

## Editing discipline

The file is ~92KB / ~1540 lines. Grep for an anchor and Read with `offset`/`limit`
rather than reading it whole; re-read the exact region immediately before each Edit.

## Architecture

- `DEFAULTS` — all seed content. `DB` + `loadDB()`/`saveDB()` persist to localStorage
  under `bikeops_db_v3`; `loadDB()` falls back to defaults per-key on corrupt/mismatched
  data.
- Views are `<section class="view" data-view="…">`; `go(view)` toggles `.active` and
  syncs `location.hash`, so every view is deep-linkable for QR codes.
- Manager-only controls use class `webonly`, shown by `setWeb(on)` toggling `.is-web`
  on `<body>`. **Reuse this pattern — do not add a second mechanism.**
- Bikes are keyed by `id` (`curtain`/`ceiling`/`oosbike` — the storage location).
  `name` is manager-editable, so **never match a bike by name**; `DB.issues[].bike`
  and `DB.checkLog[].bike` both hold ids.
- Dialogs go through `uiAlert` / `uiConfirm` / `uiPrompt` / `uiForm` (promise-based,
  in `openModal`). **No `window.alert/confirm/prompt`** — the native ones render as
  "sonnnnnion.github.io says", which reads as a browser warning, not as the site.
- Two backends, not one: `DB.api.jumpkit` and `DB.api.safety` point at two separate
  spreadsheets. `DB.apiUrl` is legacy and is migrated on load.

## Things that bite

- `.topbar` must span `grid-column:1/-1`, not `1/3` — a hard-coded 2-column span
  conjures an implicit second column back into the single-column mobile layout.
- Never use `new Date().toISOString().slice(0,10)` for a local calendar date; it
  returns *tomorrow* after 8pm EDT. Use `todayISO()`.
- The sidebar must not be `display:none` on mobile. QR codes are scanned on phones,
  so hiding nav strands anyone who lands on a form deep link.
- `.webonly{display:none}` is declared early, so **any later rule setting `display` at
  equal specificity leaks manager controls into member view**. After any gating change,
  sweep all views in member view for `.webonly` elements with `offsetParent !== null`.
  Expected: 0.
- The global `label{}` rule is uppercase/tracked/faint. Any `<label>` holding a
  sentence (e.g. `.mcheck`) must undo `text-transform` and `letter-spacing`.

## Constraints

- Raw source material in this folder is gitignored and contains PII (a phone number
  and a physical lock combination). Only sanitized, transcribed content goes on the
  site. Never commit those files or paste their contents anywhere.
- The site is public: it cannot hold a secret. The Bike Manager passcode hides manager
  controls from casual visitors; it is not a security boundary. See `SETUP-BACKEND.md`.
- Bike names: **Diane** (curtain), **Kevin** (ceiling), **Cheryl** (OOS bike), assigned
  by Michaela 2026-07-25 and editable in manager mode. Do not invent *new* ones.
- **No DRAFT notices anywhere.** Michaela removed them all (2026-07-25): she is the one
  in charge and decides what is provisional. Do not reintroduce a "draft"/"pending
  ratification" label on weather thresholds, the banner, or anything else.
  The "sheets not connected" banner is *not* a draft notice — it is what stops a member
  believing a submission was filed. It stays.
- Two roles, two bodies of bylaws: `DB.bylaws` (Bike Manager) and `DB.bylawsResponse`
  (Bike Response — every member trained to ride). Both render through `renderBylawSet`.
- `DB.boundaries` and `DB.contacts` are manager-editable key/value lists rendered by
  `renderKV`. Do not hardcode rows back into the HTML.
