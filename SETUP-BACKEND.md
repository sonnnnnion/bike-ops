# Connecting Bike Ops to a Google Sheet

This wires the Jumpkit Check and Bike Safety Check forms so submissions land in a
spreadsheet automatically. Takes about 15 minutes, done once.

**You do not put any password into this site.** That is the whole point of the design
below: the script lives *inside* the Google account and runs as that account. The
website only learns a URL that can do exactly one thing — add a row. Read
[Why not just store the account password?](#why-not-just-store-the-account-password)
before deciding to do it another way.

---

## What you get

Two tabs in one spreadsheet:

| Sheet tab | Filled in by | Michaela's ask |
|---|---|---|
| `Equipment Checks` | Jumpkit Check form | flags when equipment is missing or expired |
| `Bike Checks` | Bike Safety Check form | the weekly bike checks |

Both record the date submitted and who submitted it (first and last name — the form
refuses to submit without them).

---

## Step 1 — Make the spreadsheet

1. Sign in as the bike program's Google account (the shared bike ops Gmail).
2. Go to <https://sheets.new> and name it something like **Bike Ops Submissions**.
3. Leave it otherwise empty. The script creates and titles both tabs on first use.

## Step 2 — Add the script

1. In that spreadsheet: **Extensions → Apps Script**.
2. Delete the sample `myFunction` stub.
3. Paste in everything from [the script below](#the-script).
4. Click the 💾 save icon.

## Step 3 — Deploy it as a Web App

1. **Deploy → New deployment**.
2. Click the gear next to "Select type" and choose **Web app**.
3. Set:
   - **Description:** `Bike Ops form intake`
   - **Execute as:** **Me** (the bike ops account you are signed in as) ← must be this
   - **Who has access:** **Anyone** ← must be this
4. **Deploy**. Google asks you to authorize — approve it. You will hit a
   "Google hasn't verified this app" screen: **Advanced → Go to (project name)**.
   That warning is expected for your own script.
5. Copy the **Web app URL**. It ends in `/exec`.

> "Who has access: Anyone" means anyone who *has the URL* can post a row. It does not
> make the spreadsheet public, and it does not expose the Google account. See
> [How locked down is this?](#how-locked-down-is-this) for what that does and doesn't
> protect.

## Step 4 — Paste the URL into the site

1. Open the site, click **🔒 Bike Manager**, enter the passphrase.
2. Go to **Site Settings** in the sidebar.
3. Paste the URL into **Apps Script Web App URL** and save.
4. The yellow DRAFT banner stops saying the backend is unconnected.

## Step 5 — Test it before trusting it

Submit one real Jumpkit check with a deliberately unchecked item, and one Safety
check. Confirm two things:

- a row appears in each sheet tab, and
- the `Missing` column actually lists the item you left unchecked.

**Do not skip this.** Because of how the browser sends the data, the site says
"Submitted ✓" even if the script rejected it — see the warning in
[How locked down is this?](#how-locked-down-is-this).

---

## The script

```javascript
/**
 * Bike Ops — form intake for the CMU EMS bike program.
 * Receives submissions from the Bike Ops site and appends them to this spreadsheet.
 *
 * Two tabs, created automatically on first submission:
 *   Equipment Checks  <- jumpkit / bag checks
 *   Bike Checks       <- pre-ride bike safety checks
 */

var SHEETS = {
  jumpkit: {
    name: 'Equipment Checks',
    headers: ['Submitted At', 'First Name', 'Last Name', 'Bag', 'Verdict',
              'Anything Missing?', 'Missing Items', 'Expiring / Expired',
              'Expiration Dates', 'Notes']
  },
  safety: {
    name: 'Bike Checks',
    headers: ['Submitted At', 'First Name', 'Last Name', 'Verdict',
              'Anything Missing?', 'Missing Items', 'Grounded By Weather?',
              'Conditions Flagged', 'Notes']
  }
};

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) return ok('no body');
    var p = JSON.parse(e.postData.contents);

    var conf = SHEETS[p.form];
    if (!conf) return ok('unknown form: ' + p.form);

    var sheet = getSheet(conf);
    var missing = p.missing || [];
    var conditions = p.conditions || [];

    // Local timestamp, not the browser's UTC string — so "date submitted"
    // reads as the day it actually happened in Pittsburgh.
    var when = Utilities.formatDate(new Date(),
      Session.getScriptTimeZone(), 'yyyy-MM-dd HH:mm:ss');

    var row;
    if (p.form === 'jumpkit') {
      row = [
        when, p.firstName || '', p.lastName || '', p.bag || '', p.verdict || '',
        missing.length ? 'YES — ' + missing.length + ' missing' : 'no',
        missing.join(', '),
        expiryFlag(p.expiries),
        formatExpiries(p.expiries),
        p.notes || ''
      ];
    } else {
      row = [
        when, p.firstName || '', p.lastName || '', p.verdict || '',
        missing.length ? 'YES — ' + missing.length + ' missing' : 'no',
        missing.join(', '),
        conditions.length ? 'YES' : 'no',
        conditions.join(', '),
        p.notes || ''
      ];
    }

    sheet.appendRow(row);
    highlightIfProblem(sheet, p, missing, conditions);
    return ok('saved');

  } catch (err) {
    // Never throw: the site cannot read the response anyway, and a thrown error
    // just loses the submission silently. Log it where you can actually find it.
    console.error('Bike Ops intake failed: ' + err + ' :: ' + rawOf(e));
    return ok('error logged');
  }
}

/** Creates the tab and header row the first time a form type is submitted. */
function getSheet(conf) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(conf.name);
  if (!sheet) {
    sheet = ss.insertSheet(conf.name);
    sheet.appendRow(conf.headers);
    sheet.getRange(1, 1, 1, conf.headers.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }
  return sheet;
}

/** Red row = something needs a manager's attention. */
function highlightIfProblem(sheet, p, missing, conditions) {
  var v = String(p.verdict || '').toLowerCase();
  var bad = missing.length > 0 ||
            conditions.length > 0 ||
            v.indexOf('expired') >= 0 ||
            v.indexOf('not cleared') >= 0 ||
            v.indexOf('grounded') >= 0 ||
            v.indexOf('incomplete') >= 0;
  if (!bad) return;
  sheet.getRange(sheet.getLastRow(), 1, 1, sheet.getLastColumn())
       .setBackground('#fce8e6');
}

/** "EXPIRED: oral glucose" / "expires within 30 days" / "" */
function expiryFlag(expiries) {
  if (!expiries) return '';
  var today = new Date(); today.setHours(0, 0, 0, 0);
  var expired = [], soon = [];
  Object.keys(expiries).forEach(function (k) {
    if (!expiries[k]) return;
    var d = new Date(expiries[k] + 'T00:00:00');
    if (isNaN(d.getTime())) return;
    var days = Math.round((d - today) / 86400000);
    if (days < 0) expired.push(k + ' (' + expiries[k] + ')');
    else if (days <= 30) soon.push(k + ' (' + days + 'd)');
  });
  if (expired.length) return 'EXPIRED: ' + expired.join(', ');
  if (soon.length) return 'expiring soon: ' + soon.join(', ');
  return '';
}

function formatExpiries(expiries) {
  if (!expiries) return '';
  return Object.keys(expiries).map(function (k) {
    return k + '=' + (expiries[k] || 'not entered');
  }).join('; ');
}

function ok(msg) {
  return ContentService.createTextOutput(JSON.stringify({ result: msg }))
                       .setMimeType(ContentService.MimeType.JSON);
}

function rawOf(e) {
  try { return e.postData.contents.slice(0, 500); } catch (x) { return '(no body)'; }
}
```

---

## Re-deploying after you edit the script

Editing the code is not enough — you must ship a new version:

**Deploy → Manage deployments → ✏️ (edit) → Version: New version → Deploy**

The URL stays the same, so you do **not** need to update the site. If you instead
pick "New deployment" you get a *different* URL and the site keeps posting to the
old one — a common way to sit there wondering why nothing is arriving.

---

## How locked down is this?

Worth being straight about, since real submissions depend on it.

**What this design protects.** The Google account password never goes into the
website, never reaches a member's browser, and is not in the public repo. Someone
with the deployment URL can add rows. They cannot read the spreadsheet, cannot sign
in as the account, and cannot touch anything else in the Drive.

**What it does not protect.**

- **The URL is not a secret.** It ships inside a public page. Anyone who views
  source can find it and post junk rows. A shared token would not fix this — the
  token would sit in the same public page — which is why the script deliberately
  has no token check to give a false sense of security.
- **Submissions are fire-and-forget.** The site posts with `mode:'no-cors'`, which
  dodges a CORS problem but also means the browser cannot read the reply. The site
  shows "Submitted ✓" as soon as the request leaves — *even if the script errored
  or rejected it*. That is why Step 5 says to verify a real row appears.
- **The Bike Manager passphrase is not a security boundary.** It hides manager
  controls from casual visitors. Anyone who opens devtools can flip it on. Do not
  put anything genuinely sensitive behind it.

**If junk rows ever become a problem,** the fix is to stop treating the URL as
private: switch the deployment to "Anyone with a Google account", which makes each
submitter sign in with their Andrew/Google account. That is a real identity check,
at the cost of requiring members to be signed in.

## Why not just store the account password?

It was asked for; here is why the site does not do it.

`index.html` is served from a **public GitHub Pages repo**. Everything in it is
world-readable via View Source, and once committed it stays in the git history
permanently — deleting it later does not remove it. There is no "manager-only"
section of a static file: the Bike Manager gate is JavaScript running on the
visitor's own machine, and they control it. Anything hidden behind it is still
sitting in the file they already downloaded.

So storing the password there would publish it, and publishing it hands over the
whole account — the Drive, the Sheet, and every submission in it.

A static public site fundamentally cannot keep a secret. The Apps Script approach
above exists precisely to avoid needing one.

---

## Troubleshooting

**Nothing arrives in the Sheet.**
Apps Script editor → **Executions** (left sidebar). If there are no entries, the
request never landed — recheck the URL in Site Settings ends in `/exec`, and that
you re-deployed as a **new version** after editing. If entries show "Failed", open
one; `console.error` logs the reason and the raw body.

**Rows land in the wrong tab.** The tab is chosen by `payload.form`, which is
`jumpkit` or `safety`. Don't rename the tabs by hand — change `SHEETS[...].name`
and re-deploy, or the script just recreates the originals.

**"Missing Items" is empty but the verdict says incomplete.** The verdict text
comes from the site; `missing` is computed from unchecked boxes. If they disagree,
the form was edited in manager mode while it was being filled in — resubmit.

**I want a QR code for a form.** Each check has its own URL. Point any QR generator
at the exact link shown on the Checks & Forms page, e.g.
`https://sonnnnnion.github.io/bike-ops/#jumpkit-check`.
