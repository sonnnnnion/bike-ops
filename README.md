# CMU EMS · Bike Ops

Internal hub for the CMU EMS Bike Manager role: bike readiness, issue tracking,
jumpkit & pre-ride checks (with QR codes), an out-of-service decision tool,
video tutorials, repair contacts, and inventory.

**Status:** DRAFT TEMPLATE. Content is placeholder pending an office walkthrough
(real bikes, current jumpkit form fields, out-of-service criteria).

## What's here

```
index.html   the entire app — static, single file, vanilla HTML/CSS/JS
              (Carbon theme, borrowed from the Orgo Planner / summerPlan site)
README.md     this file
```

## Structure (planned)

- **Dashboard** — bike readiness at a glance
- **Bikes & Issues** — running problem log per bike, feeds service status
- **Out-of-Service Tool** — check symptoms → consistent in-service / out-of-service verdict
- **Checks & Forms** — jumpkit check, pre-ride safety check, weekly readiness (each with a QR)
- **Tutorials** — video library (webmaster can add)
- **Repairs & Fixes** — shop contacts + in-office how-to guides
- **Inventory** — tools, parts, locks/keys, order list
- **Docs & Bylaws** — role, operating boundaries

## Access model (draft)

**No login to enter** — the whole site is open to anyone. A **Bike Manager mode**
(top-bar unlock) reveals the manager-only controls: add videos, resolve issues,
edit docs/inventory, run the weekly check, apply a verdict to a bike.

The unlock is a soft passcode prompt only. On a *public* site a client-side
passcode is cosmetic — real gating needs a backend (see "Open decisions").
Until then, keep genuinely sensitive content out of the site.

## Open decisions (see chat)

1. **Hosting / visibility** — public GitHub Pages (free, live URL, content world-readable)
   vs private (nothing exposed, no free live URL).
2. **Data backend** — repo-only JSON like the 21-254 site (reports via email) vs
   Google Sheets + Apps Script (live saving of reports, checks, and added videos).

## Conventions borrowed from 21-254 Practice Lab

- Single static `index.html`, everything served from the repo (offline-capable)
- QR codes baked in as inline SVG (no external library)
- Motion tokens: `--ease-out: cubic-bezier(.16,1,.3,1)`, `viewIn` transition,
  `prefers-reduced-motion` respected
