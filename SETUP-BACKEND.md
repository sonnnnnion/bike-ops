# Connecting Bike Ops to its Google Sheets

This wires the Jumpkit Check and Bike Safety Check forms so submissions land in a
spreadsheet automatically. Takes about 25 minutes, done once.

**You do not put any password into this site.** That is the whole point of the design
below: the script lives *inside* the Google account and runs as that account. The
website only learns a URL that can do exactly one thing — add a row. Read
[Why not just store the account password?](#why-not-just-store-the-account-password)
before deciding to do it another way.

---

## What you get

**Two separate spreadsheets**, matching the two that already exist in the Bike Ops
Drive folder:

| Spreadsheet | Filled in by | Who fills it |
|---|---|---|
| **Bike Jumpkit Check** | Jumpkit Check form | any member, before a ride |
| **Bike Safety Check** | Bike Safety Check form | riders before a ride; the Bike Manager weekly, for every bike |

Both record the date submitted and who submitted it (first and last name — the form
refuses to submit without them).

> **Two files, not two tabs.** An earlier version of this doc described one
> spreadsheet with an `Equipment Checks` tab and a `Bike Checks` tab. That is not what
> exists — the two checks are read by different people on different schedules, and
> keeping them separate means either one can be shared or exported on its own. You do
> the setup below **twice**, once per spreadsheet, and end up with **two Web App
> URLs**.

---

## Do this twice — once per spreadsheet

Work through Steps 1–3 completely for **Bike Jumpkit Check**, then repeat them for
**Bike Safety Check**. Keep both URLs; you need them together in Step 4.

## Step 1 — Open the spreadsheet

1. Sign in as the bike program's Google account (the shared bike ops Gmail).
2. Open **Bike Jumpkit Check** (or **Bike Safety Check**) from the Bike Ops folder.
   If it does not exist yet, create it at <https://sheets.new> and name it exactly that.
3. Leave it otherwise empty. The script creates and titles its tab on first use.

## Step 2 — Add the script

1. In that spreadsheet: **Extensions → Apps Script**.
2. Delete the sample `myFunction` stub.
3. Paste in everything from [the script below](#the-script).
4. **Set `EXPECTED_FORM` at the top of the script** — `'jumpkit'` in the Bike Jumpkit
   Check copy, `'safety'` in the Bike Safety Check copy. This is the one line that
   differs between the two, and it is what makes a swapped URL fail loudly instead of
   quietly filing safety checks into the jumpkit sheet.
5. Click the 💾 save icon.

## Step 3 — Deploy it as a Web App

1. **Deploy → New deployment**.
2. Click the gear next to "Select type" and choose **Web app**.
3. Set:
   - **Description:** `Bike Ops form intake — jumpkit` (or `— safety`)
   - **Execute as:** **Me** (the bike ops account you are signed in as) ← must be this
   - **Who has access:** **Anyone** ← must be this
4. **Deploy**. Google asks you to authorize — approve it. You will hit a
   "Google hasn't verified this app" screen: **Advanced → Go to (project name)**.
   That warning is expected for your own script.
5. Copy the **Web app URL**. It ends in `/exec`. Label which spreadsheet it came from —
   the two URLs look nearly identical and are easy to mix up.

> "Who has access: Anyone" means anyone who *has the URL* can post a row. It does not
> make the spreadsheet public, and it does not expose the Google account. See
> [How locked down is this?](#how-locked-down-is-this) for what that does and doesn't
> protect.

## Step 4 — Paste both URLs into the site

1. Open the site, click **🔒 Bike Manager**, enter the passphrase.
2. Go to **Site Settings** in the sidebar.
3. There are **two** fields, labelled with the spreadsheet names. Paste each URL into
   its matching field and save.
4. The banner stops saying the sheets are unconnected. If you fill in only one, the
   banner says **"Partly connected"** and names which half is live — that is deliberate,
   so nobody assumes the other form is being recorded.

## Step 5 — Press "Test connection"

The button is right next to Save. It asks each URL what it is and reports back:

| What it says | What it means |
|---|---|
| **Live** — expecting `jumpkit` checks, N rows | Working. |
| **Swapped** | Both URLs are real, but they are in each other's fields. Swap them. |
| **Wrong URL** | Something answered, but not this script. Usually the spreadsheet's own link was pasted instead of the Apps Script Web App URL, or the script was edited but not re-deployed as a **new version**. |
| **Unreachable** | Nothing answered. Usually "Who has access" is not set to **Anyone**, or the URL is wrong. |

This is the check that actually proves it works, and it is worth doing before you
trust a single submission — see [How locked down is this?](#how-locked-down-is-this)
for why a submitted form can look successful when nothing was written.

## Step 6 — Then send one real check through each

Submit one Jumpkit check with a deliberately unchecked item, and one Safety check.
Confirm three things:

- a row appears in **Bike Jumpkit Check**, and a row appears in **Bike Safety Check**,
- neither row landed in the *other* spreadsheet, and
- the `Missing Items` column actually lists the item you left unchecked.

---

## Optional — Google sign-in instead of the shared passcode

The code is in place and **switched off**. With `GOOGLE_CLIENT_ID` blank, the manager
unlock stays a passcode. Fill it in and the unlock becomes "Sign in with Google",
accepting only the addresses in `MANAGER_EMAILS`.

**Read this before turning it on.** Signing in identifies *who* you are, which a shared
passcode never could — a passcode gets handed around and never rotated, so this is a
real improvement. But what it unlocks is still a CSS class on a static page, so anyone
who opens devtools can still switch manager mode on. It is **better identity, not a
security boundary**. Never put anything behind this gate that would genuinely hurt if a
member saw it. What protects submitted data is the Apps Script running server-side.

To enable it:

1. <https://console.cloud.google.com/> → create a project (any name).
2. **APIs & Services → OAuth consent screen** → External → fill in app name and support
   email → Save. You do not need to publish or get it verified for your own account.
3. **APIs & Services → Credentials → Create credentials → OAuth client ID → Web
   application**.
4. Under **Authorised JavaScript origins** add both:
   - `https://sonnnnnion.github.io`
   - `http://localhost:8848`
5. Copy the **Client ID** (ends in `.apps.googleusercontent.com`).
6. In `index.html`, set `var GOOGLE_CLIENT_ID='…'` and check `MANAGER_EMAILS` holds the
   exact bike-account address. **A wrong address silently refuses the right account.**

If Google cannot be reached, the dialog offers "Use passcode instead", so a network
problem in a bike room never locks the manager out.

## The script

```javascript
// Bike Ops — form intake for the CMU EMS bike program.
// Receives submissions from the Bike Ops site and appends them to THIS spreadsheet.
//
// The same script goes into both spreadsheets. The ONLY line you change between the
// two copies is EXPECTED_FORM directly below.
//
// Every comment here is a // line comment on purpose. A /* */ block whose opening
// line gets dropped during a copy-paste turns its first line into code and throws
// a syntax error that points at prose — which is exactly what happened once.

// 'jumpkit' in the Bike Jumpkit Check spreadsheet.
// 'safety'  in the Bike Safety Check spreadsheet.
//
// This is a guard, not a preference. Without it, pasting the wrong URL into Site
// Settings would file safety checks into the jumpkit spreadsheet and create a
// stray tab to hold them — wrong, and silent, because the site cannot read the
// reply. With it, the mismatch is refused and logged where you can find it.
var EXPECTED_FORM = 'jumpkit';

var SHEETS = {
  jumpkit: {
    name: 'Jumpkit Checks',
    headers: ['Submitted At', 'First Name', 'Last Name', 'Andrew ID', 'Bag', 'Verdict',
              'Anything Missing?', 'Missing Items', 'Expiring / Expired',
              'Expiration Dates', 'Notes', 'Submission ID']
  },
  safety: {
    name: 'Bike Checks',
    headers: ['Submitted At', 'First Name', 'Last Name', 'Andrew ID', 'Verdict',
              'Anything Missing?', 'Missing Items', 'Grounded By Weather?',
              'Conditions Flagged', 'Notes', 'Submission ID']
  }
};

// Answers the "Test connection" button in Site Settings.
//
// A GET is readable cross-origin where the POST is not, so this is the only way
// the site can tell a working deployment from a dead URL. It reports which form
// this copy expects, which is what catches the two Web App URLs being swapped.
function doGet(e) {
  var conf = SHEETS[EXPECTED_FORM] || {};
  var rows = 0;
  try {
    var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(conf.name);
    if (sh) rows = Math.max(0, sh.getLastRow() - 1);   // minus the header row
  } catch (err) {
    rows = -1;
  }
  return ok2({
    ok: true,
    expects: EXPECTED_FORM,
    sheet: conf.name || '',
    rows: rows
  });
}

function ok2(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
                       .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) return ok('no body');
    var p = JSON.parse(e.postData.contents);

    var conf = SHEETS[p.form];
    if (!conf) return ok('unknown form: ' + p.form);

    if (p.form !== EXPECTED_FORM) {
      console.error('Bike Ops: this deployment expects "' + EXPECTED_FORM +
        '" but received "' + p.form + '". The wrong Web App URL is almost ' +
        'certainly pasted into Site Settings. Nothing was written.');
      return ok('wrong spreadsheet for form: ' + p.form);
    }

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
        when, p.firstName || '', p.lastName || '', p.andrewId || '', p.bag || '', p.verdict || '',
        missing.length ? 'YES — ' + missing.length + ' missing' : 'no',
        missing.join('\n'),
        expiryFlag(p.expiries),
        formatExpiries(p.expiries),
        p.notes || '',
        p.submissionId || ''
      ];
    } else {
      row = [
        when, p.firstName || '', p.lastName || '', p.andrewId || '', p.verdict || '',
        missing.length ? 'YES — ' + missing.length + ' missing' : 'no',
        missing.join('\n'),
        conditions.length ? 'YES' : 'no',
        conditions.join(', '),
        p.notes || '',
        p.submissionId || ''
      ];
    }

    if (alreadyWritten(sheet, p.submissionId)) return ok('duplicate ignored');

    sheet.appendRow(row);
    sheet.getRange(sheet.getLastRow(), 1, 1, row.length).setVerticalAlignment('top');
    highlightIfProblem(sheet, p, missing, conditions);
    addToRestock(p, missing);
    return ok('saved');

  } catch (err) {
    // Never throw: the site cannot read the response anyway, and a thrown error
    // just loses the submission silently. Log it where you can actually find it.
    console.error('Bike Ops intake failed: ' + err + ' :: ' + rawOf(e));
    return ok('error logged');
  }
}

// A submission carries an id. If the same id is already in the last column, this
// is a retry or a double-fire of one that was written, not a new check. One
// sitting produced five identical rows in the real Jumpkit sheet before this.
function alreadyWritten(sheet, submissionId) {
  if (!submissionId) return false;
  var last = sheet.getLastRow();
  if (last < 2) return false;
  var col = sheet.getLastColumn();
  var start = Math.max(2, last - 50);           // recent rows are enough
  var ids = sheet.getRange(start, col, last - start + 1, 1).getValues();
  for (var i = 0; i < ids.length; i++) {
    if (String(ids[i][0]) === String(submissionId)) return true;
  }
  return false;
}

// The equipment manager's actual job is "what do I need to put back in the bag",
// and reading that out of a comma-run inside one cell is miserable. This writes
// ONE ROW PER MISSING ITEM to a Restock tab, with a real checkbox to tick when it
// has been replaced. Nothing is auto-removed — ticking it is the record.
function addToRestock(p, missing) {
  if (!missing || !missing.length) return;
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var name = 'Restock';
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    sh.appendRow(['Restocked?', 'Item', 'Reported', 'Bag', 'Reported By', 'Submission ID']);
    sh.getRange(1, 1, 1, 6).setFontWeight('bold');
    sh.setFrozenRows(1);
    sh.setColumnWidth(2, 380);
  }
  if (alreadyWritten(sh, p.submissionId)) return;

  var when = Utilities.formatDate(new Date(),
    Session.getScriptTimeZone(), 'yyyy-MM-dd HH:mm');
  var who = ((p.firstName || '') + ' ' + (p.lastName || '')).trim();
  var rows = missing.map(function (item) {
    return [false, item, when, p.bag || '', who, p.submissionId || ''];
  });
  var first = sh.getLastRow() + 1;
  sh.getRange(first, 1, rows.length, 6).setValues(rows);
  sh.getRange(first, 1, rows.length, 1).insertCheckboxes();
}

// Creates the tab and header row the first time a form type is submitted.
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

// Red row = something needs a manager's attention.
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

// "EXPIRED: oral glucose" / "expires within 30 days" / ""
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

Do this in **both** spreadsheets. They hold independent copies of the script, so a fix
applied to one leaves the other running the old code.

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
  shows "Sent ✓" as soon as the request leaves — *even if the script errored
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

**Rows arrive but the Andrew ID column is missing.** The header row is written once,
the first time a tab is created, so a tab that already exists keeps its original
headers and the new value lands one column out of step. Fix it by deleting the tab
(right-click the tab → Delete) and submitting again — the script recreates it with the
current headers. Export anything you want to keep first.

**"Test connection" says Wrong URL even though the script is right.** The `doGet`
function is new. A deployment made before it existed does not have it — re-copy the
script and **Deploy → Manage deployments → edit → New version**.

**Apps Script says `SyntaxError: Unexpected token '*'` on line 1.** The paste started
one line too late and dropped the opening `/**` of the header comment, which turned the
prose underneath it into code. The script above no longer uses a `/* */` block anywhere,
so this cannot recur — but if you are looking at a copy that still has it, either add
`/**` back as the first line or re-copy the current script. **Select from the very first
character of the block**; clicking into the middle of a code block and pressing
Ctrl/Cmd-A selects the page, not the block.

**Nothing arrives, and Executions shows "wrong spreadsheet for form".** The two Web
App URLs are swapped in Site Settings. Open the failed execution to see which form it
received, and put that URL in the other field.

**Rows land in the wrong tab within a spreadsheet.** The tab is chosen by
`payload.form`. Don't rename tabs by hand — change `SHEETS[...].name` and re-deploy,
or the script just recreates the originals.

**I edited the script and only one spreadsheet changed.** There are two independent
copies. Every script edit has to be pasted and re-deployed in *both*, unless it is the
`EXPECTED_FORM` line, which is meant to differ.

**"Missing Items" is empty but the verdict says incomplete.** The verdict text
comes from the site; `missing` is computed from unchecked boxes. If they disagree,
the form was edited in manager mode while it was being filled in — resubmit.

**I want a QR code for a form.** Each check has its own URL. Point any QR generator
at the exact link shown on the Checks & Forms page, e.g.
`https://sonnnnnion.github.io/bike-ops/#jumpkit-check`.
