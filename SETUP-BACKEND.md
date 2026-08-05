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

Two forms feed this: the **Jumpkit Check** (any member, before a ride) and the
**Bike Safety Check** (riders before a ride, and the Bike Manager weekly for every
bike). Each becomes a tab. Both record the date and who submitted — the form refuses
to submit without a first and last name.

A third tab, **Restock**, is written automatically: one row per missing item, so the
equipment manager reads a worklist instead of a log.

### One spreadsheet or two?

Both work. The script's `SERVES` line decides, and it is the only line you set.

| | Setup | When to pick it |
|---|---|---|
| **One spreadsheet** *(recommended)* | `SERVES = ['jumpkit','safety']`. One script, one deployment, one URL — pasted into **both** fields in Site Settings. | Almost always. Half the setup, half the things to get wrong, and both checks sit side by side. |
| **Two spreadsheets** | `SERVES = ['jumpkit']` in one, `SERVES = ['safety']` in the other. Two deployments, two URLs. | Only if one check must be shared or exported without the other. |

Nothing else changes between them — same script, same columns, same site.
Switching later means re-pasting the script and re-pointing Site Settings; the rows
already written stay where they are.

---

## Steps 1–3

If you are using **two** spreadsheets, work through Steps 1–3 completely for the
first, then repeat for the second, and keep both URLs.

## Step 1 — Open the spreadsheet

1. Sign in as the Google account that will own this. See §7 on which account —
   it should be one that will still exist next year.
2. Open the spreadsheet from the Bike Ops folder, or create one at
   <https://sheets.new>. Name it **Bike Ops Checks** for a combined setup, or
   **Bike Jumpkit Check** / **Bike Safety Check** if you are keeping them apart.
3. Leave it otherwise empty. The script creates and titles its tabs on first use.

## Step 2 — Add the script

1. In that spreadsheet: **Extensions → Apps Script**.
2. Delete the sample `myFunction` stub.
3. Paste in everything from [the script below](#the-script).
4. **Set `SERVES` at the top of the script.** For one combined spreadsheet leave it
   as `['jumpkit', 'safety']`. For two, set `['jumpkit']` in one and `['safety']` in
   the other. This is the only line you change, and it is what makes a swapped URL
   fail loudly instead of quietly filing safety checks into the jumpkit tab.
5. Click the 💾 save icon.

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
5. Copy the **Web app URL**. It ends in `/exec`. With a combined spreadsheet this one
   URL goes into **both** fields in Site Settings. With two, label which spreadsheet
   each came from — the URLs look nearly identical and are easy to mix up.

> "Who has access: Anyone" means anyone who *has the URL* can post a row. It does not
> make the spreadsheet public, and it does not expose the Google account. See
> [How locked down is this?](#how-locked-down-is-this) for what that does and doesn't
> protect.

## Step 4 — Paste both URLs into the site

1. Open the site, click **🔒 Bike Manager**, enter the passphrase.
2. Go to **Site Settings** in the sidebar.
3. There are **two** fields, labeled with the spreadsheet names. Paste each URL into
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
- the `What Was Missing` column actually lists the item you left unchecked.

---

## What the two tabs look like

**The checks tab** — for whoever reads down the log:

| Column | Why it's there |
|---|---|
| `Date` / `Time` | Split, so you can sort or filter by day without parsing a timestamp |
| `Name`, `Andrew ID` | Who did it. Andrew ID because two members can share a name |
| `Bag` / `Bike` | Which one this check was about |
| `Result` | The verdict the site reached |
| `Missing` | A **number**, so you can sort worst-first or filter to `>0` |
| `What Was Missing` | One item per line |
| `Notes` | Whatever was typed at the bottom of the check |

Date, time and name are frozen, so they stay on screen as you scroll right. A filter
is already on. Rows are shaded: green if clean, amber if something is expiring, red if
anything is missing or the bike was not cleared. The color is never the only signal —
the `Result` text says the same thing. The `Submission ID` column is hidden; it exists
so a double-tapped submit cannot become a second row.

**The Restock tab** — for the equipment manager, and it is a worklist, not a log:

| Column | |
|---|---|
| `Done` | A real checkbox. Tick it when the item is back in the bag |
| `Item` | One row per item, ever — not one row per report |
| `Times Reported` | Bold when >1, i.e. it has been asked for repeatedly |
| `First` / `Last Reported` | How long it has been outstanding |
| `Where`, `Last Reported By` | Which bag, and who to ask |

The important part: **reporting the same item again does not add a row.** It bumps the
counter and the last-reported date, so the length of the list is the length of the
actual job. Ticking `Done` grays the row and strikes it through. If that item is later
reported missing again, the row reopens by itself.

### After pasting an updated script

Run **`tidyUp`** once from the Apps Script editor (select it in the function dropdown,
press Run). That reformats a tab that already exists and repaints the restock list —
new formatting otherwise only applies to a tab created from scratch.

If your tabs already hold test rows from an older column layout, the simplest clean
start is to delete those tabs (right-click the tab → Delete) and submit once. The
script rebuilds them with the current columns and formatting.

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

To enable it, signed in as the bike account:

1. Go to <https://console.cloud.google.com/>. **Create a project first** — click
   **Select a project → New project**, name it anything ("Bike Ops"), Create, then make
   sure it is the selected project in the top bar. Every screen below is blank until a
   project is selected, which looks like a broken page but is not.
2. Open **Google Auth Platform** (search "Google Auth Platform" in the top search bar).
   If it offers **Get started**, take it — it walks the next two steps in one wizard.
3. **App information:** app name (e.g. "CMU EMS Bike Ops") and your support email.
4. **Audience: External.** This is where "External" lives now — Google replaced the old
   "OAuth consent screen" page with this, so older instructions send you looking for a
   screen that no longer exists. External simply means "not a Workspace-internal app";
   you do **not** need to publish it or pass verification to sign in as the owner.
5. **Contact information:** your email. Then agree and create.
6. Go to **Clients → Create client → Application type: Web application**.
7. Under **Authorized JavaScript origins** add both, exactly, with no trailing slash:
   - `https://sonnnnnion.github.io`
   - `http://localhost:8848`

   Leave **Authorized redirect URIs** empty — Google Identity Services returns the token
   to the page itself and never redirects.
8. Create, then copy the **Client ID**. It ends in `.apps.googleusercontent.com`.
9. In `index.html`, set `var GOOGLE_CLIENT_ID='…'` and check `MANAGER_EMAILS` holds the
   exact bike-account address. **A wrong address silently refuses the right account.**

While the app is in **Testing**, only accounts listed as test users can sign in — add
the bike account under **Audience → Test users**, or press **Publish app** on that same
page. If sign-in fails with "access_denied", that is almost always which one of those
two you have not done.

The Client ID is not a secret: it is designed to sit in a public page, and it is useless
without an origin on the list above.

If Google cannot be reached, the dialog offers "Use passcode instead", so a network
problem in a bike room never locks the manager out.

## Shared content — so edits reach everyone

Until now, everything a manager edited was saved to `localStorage`: visible in one
browser, on one device. A member opening the site saw the seeded defaults, and the
manager was the only person who would never notice, because theirs looked right.

The **jumpkit** script now also stores the site's content:

- **Reading is public.** Every visitor's browser fetches the content on load. That is
  correct — this is the text of a public website, the same words already on the page.
- **Writing requires a verified manager.** Site Settings ▸ **Publish to everyone** sends
  the content along with the Google ID token from sign-in. The script asks Google
  whether that token is genuine, whether it was issued for *this* site, and whose it is,
  and refuses unless the address is in `MANAGER_EMAILS`.

That check runs **inside Google, server-side**, where a browser cannot lie about it.
This is the first thing in the project that is an actual permission boundary rather than
hidden UI — devtools can still reveal manager buttons, but pressing Publish without a
real sign-in gets a refusal from the script.

**Only the jumpkit copy stores content** (`CONTENT_STORE`), so there is one source of
truth. Leave the config lines identical in both copies; the safety copy simply never
receives a content request.

Publishing writes to Script Properties, not to a sheet tab, so nobody can break the site
by editing a cell.

### Working with two people

There is no merge. Publishing replaces the stored copy wholesale, so if two managers
edit at once the later Publish wins. With one Bike Manager that is not a real risk;
press **Get latest** before a big editing session if it ever becomes one.

## The script

```javascript
// Bike Ops — form intake for the CMU EMS bike program.
// Receives submissions from the Bike Ops site and appends them to THIS spreadsheet.
//
// Every comment here is a // line comment on purpose. A /* */ block whose opening
// line gets dropped during a copy-paste turns its first line into code and throws
// a syntax error that points at prose — which is exactly what happened once.

// ---------------------------------------------------------------- the one setting

// Which checks THIS spreadsheet accepts:
//
//   ['jumpkit','safety']   one spreadsheet holding both. Two tabs, one script,
//                          one Web App URL pasted into both fields in Site
//                          Settings. Fewest moving parts.
//   ['jumpkit']            jumpkit checks only.
//   ['safety']             bike safety checks only.
//
// This is a guard, not a preference. Without it, pasting the wrong URL into Site
// Settings would file safety checks into a jumpkit-only spreadsheet and create a
// stray tab to hold them — wrong, and silent, because the site cannot read the
// reply. With it, the mismatch is refused and logged where you can find it.
var SERVES = ['jumpkit', 'safety'];

// Shared site content lives wherever the jumpkit checks live, so there is one
// source of truth. Derived, not set: a safety-only copy never gets a content
// request, and a combined copy is the only copy.
var CONTENT_STORE = SERVES.indexOf('jumpkit') >= 0;

// Who may publish site content. This list is what actually decides — the site's
// own list runs in a browser the visitor controls, so it only chooses which
// buttons appear.
var MANAGER_EMAILS = ['bikecmuems@gmail.com'];
var OAUTH_CLIENT_ID = '649290078556-l1p8l9qr5stjldgrs08c8eo0od6c727e.apps.googleusercontent.com';

// Column layouts. Order is "who and what happened" first, detail after, so the
// leftmost screenful answers the question an operations exec actually opens this
// to ask. Widths are set to match; anything long is clipped rather than wrapped so
// every submission stays one scannable line.
var SHEETS = {
  jumpkit: {
    name: 'Jumpkit Checks',
    headers: ['Date', 'Time', 'Name', 'Andrew ID', 'Bag', 'Radio', 'Result',
              'Missing', 'What Was Missing', 'Expiry Flag',
              'Expiration Dates', 'Notes', 'Submission ID'],
    widths:  [92, 62, 150, 92, 96, 90, 210, 74, 320, 190, 220, 260, 90]
  },
  safety: {
    name: 'Bike Checks',
    headers: ['Date', 'Time', 'Name', 'Andrew ID', 'Bike', 'Radio', 'Result',
              'Missing', 'What Was Missing', 'Weather Grounded',
              'Conditions Flagged', 'Notes', 'Submission ID'],
    widths:  [92, 62, 150, 92, 96, 90, 210, 74, 320, 130, 240, 260, 90]
  }
};

var RESTOCK = {
  name: 'Restock',
  // One row PER ITEM, not per submission. The equipment manager's question is
  // "what do I need to put back", not "what happened on Tuesday" — that is what
  // the checks tab is for. Repeat reports bump a counter instead of adding rows.
  headers: ['Done', 'Item', 'Times Reported', 'First Reported', 'Last Reported',
            'Where', 'Last Reported By'],
  widths:  [58, 380, 110, 118, 118, 110, 160]
};

// ---------------------------------------------------------------- read side

// Answers the "Test connection" button in Site Settings.
//
// A GET is readable cross-origin where the POST is not, so this is the only way
// the site can tell a working deployment from a dead URL. It reports which form
// this copy expects, which is what catches the two Web App URLs being swapped.
function doGet(e) {
  // Public read of the site's content. Unauthenticated on purpose: this is the
  // text of a public website, the same words any visitor can already see.
  if (e && e.parameter && e.parameter.content) {
    var raw = PropertiesService.getScriptProperties().getProperty('siteContent');
    return json({
      ok: true,
      content: raw ? JSON.parse(raw) : null,
      updatedAt: Number(PropertiesService.getScriptProperties().getProperty('siteContentAt') || 0)
    });
  }
  // The site asks about one form at a time. Answer about that one when this
  // spreadsheet serves it, so a combined copy satisfies both fields.
  var asked = (e && e.parameter && e.parameter.form) || '';
  var which = SERVES.indexOf(asked) >= 0 ? asked : SERVES[0];
  var conf = SHEETS[which] || {};
  var rows = 0;
  try {
    var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(conf.name);
    if (sh) rows = Math.max(0, sh.getLastRow() - 1);   // minus the header row
  } catch (err) {
    rows = -1;
  }
  return json({ ok: true, serves: SERVES, expects: which,
                sheet: conf.name || '', rows: rows });
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
                       .setMimeType(ContentService.MimeType.JSON);
}

// ---------------------------------------------------------------- write side

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) return json({ result: 'no body' });
    var p = JSON.parse(e.postData.contents);

    // Content save. THIS is the one place a real permission check happens: the
    // ID token is verified with Google server-side, where the browser cannot lie
    // about it, and the address on it has to be a manager's.
    if (p.type === 'content') {
      if (!CONTENT_STORE) return json({ result: 'content is stored by the jumpkit copy' });
      var who = verifiedEmail(p.idToken);
      if (!who) return json({ result: 'rejected: sign-in could not be verified' });
      if (MANAGER_EMAILS.indexOf(who) < 0) {
        console.warn('Content save refused for ' + who);
        return json({ result: 'rejected: ' + who + ' is not a manager' });
      }
      PropertiesService.getScriptProperties()
        .setProperty('siteContent', JSON.stringify(p.content || {}));
      PropertiesService.getScriptProperties()
        .setProperty('siteContentAt', String(Date.now()));
      console.log('Content published by ' + who);
      return json({ result: 'content saved' });
    }

    var conf = SHEETS[p.form];
    if (!conf) return json({ result: 'unknown form: ' + p.form });

    if (SERVES.indexOf(p.form) < 0) {
      console.error('Bike Ops: this spreadsheet takes "' + SERVES.join('" and "') +
        '" but received "' + p.form + '". The wrong Web App URL is almost ' +
        'certainly pasted into Site Settings. Nothing was written.');
      return json({ result: 'wrong spreadsheet for form: ' + p.form });
    }

    var sheet = ensureSheet(conf);
    if (alreadyWritten(sheet, p.submissionId, conf.headers.length)) {
      return json({ result: 'duplicate ignored' });
    }

    var missing = p.missing || [];
    var conditions = p.conditions || [];
    var now = new Date();
    var tz = Session.getScriptTimeZone();

    var row = [
      Utilities.formatDate(now, tz, 'yyyy-MM-dd'),
      Utilities.formatDate(now, tz, 'HH:mm'),
      ((p.firstName || '') + ' ' + (p.lastName || '')).trim(),
      p.andrewId || '',
      (p.form === 'jumpkit' ? (p.bag || '') : (p.bike || '')),
      (p.form === 'jumpkit' ? (p.radio || '') : ''),   // which radio was carried
      p.verdict || '',
      missing.length,                       // a NUMBER, so it sorts and filters
      missing.join('\n'),
      (p.form === 'jumpkit' ? expiryFlag(p.expiries) : (conditions.length ? 'YES' : '')),
      (p.form === 'jumpkit' ? formatExpiries(p.expiries) : conditions.join('\n')),
      p.notes || '',
      p.submissionId || ''
    ];

    sheet.appendRow(row);
    styleRow(sheet, sheet.getLastRow(), conf, missing.length, p.verdict || '');
    addToRestock(p, missing);
    return json({ result: 'saved' });

  } catch (err) {
    // Never throw: the site cannot read the response anyway, and a thrown error
    // just loses the submission silently. Log it where you can actually find it.
    console.error('Bike Ops intake failed: ' + err + ' :: ' + rawOf(e));
    return json({ result: 'error logged' });
  }
}

// Creates the tab if missing. If the header row does not match what this version
// of the script writes, it is rewritten and the formatting reapplied — otherwise
// adding a column silently shifts every later value one place left.
function ensureSheet(conf) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(conf.name);
  if (!sh) {
    sh = ss.insertSheet(conf.name);
    sh.appendRow(conf.headers);
    formatSheet(sh, conf);
    return sh;
  }
  var have = sh.getRange(1, 1, 1, Math.max(sh.getLastColumn(), 1)).getValues()[0];
  if (have.join('|') !== conf.headers.join('|')) {
    sh.getRange(1, 1, 1, conf.headers.length).setValues([conf.headers]);
    formatSheet(sh, conf);
  }
  return sh;
}

// Everything that makes the tab pleasant to read, applied once and idempotent.
function formatSheet(sh, conf) {
  var n = conf.headers.length;
  var head = sh.getRange(1, 1, 1, n);
  head.setFontWeight('bold')
      .setBackground('#8c1c2b')
      .setFontColor('#ffffff')
      .setVerticalAlignment('middle');
  sh.setFrozenRows(1);
  sh.setFrozenColumns(3);                       // date, time, name stay on screen
  conf.widths.forEach(function (w, i) { sh.setColumnWidth(i + 1, w); });
  sh.setRowHeight(1, 34);

  // Long free text is clipped, not wrapped: one submission stays one line, and the
  // full value is still there when you click the cell or widen the column.
  sh.getRange(2, 1, Math.max(sh.getMaxRows() - 1, 1), n)
    .setWrapStrategy(SpreadsheetApp.WrapStrategy.CLIP)
    .setVerticalAlignment('top');

  // The Submission ID is machinery, not information. Keep it for dedupe, hide it.
  sh.hideColumns(n);

  if (!sh.getFilter()) sh.getRange(1, 1, sh.getMaxRows(), n).createFilter();
}

// Color carries meaning here, so it is backed by the Result text rather than
// being the only signal: a clean check reads "…ready"/"Cleared", a bad one does not.
function styleRow(sh, rowIdx, conf, missingCount, verdict) {
  var n = conf.headers.length;
  var v = String(verdict).toLowerCase();
  var bad = missingCount > 0 || v.indexOf('expired') >= 0 ||
            v.indexOf('not cleared') >= 0 || v.indexOf('grounded') >= 0 ||
            v.indexOf('incomplete') >= 0;
  var soon = !bad && (v.indexOf('expiring') >= 0 || v.indexOf('missing') >= 0);
  var range = sh.getRange(rowIdx, 1, 1, n);
  range.setBackground(bad ? '#fce8e6' : (soon ? '#fef7e0' : '#e6f4ea'));
  range.setWrapStrategy(SpreadsheetApp.WrapStrategy.CLIP).setVerticalAlignment('top');
  sh.getRange(rowIdx, 7).setHorizontalAlignment('center')
    .setFontWeight(missingCount > 0 ? 'bold' : 'normal');
}

// A submission carries an id. If that id is already in the (hidden) last column,
// this is a retry or a double-fire of a row that was written, not a new check.
// One sitting produced five identical rows in the real Jumpkit sheet before this.
function alreadyWritten(sheet, submissionId, colCount) {
  if (!submissionId) return false;
  var last = sheet.getLastRow();
  if (last < 2) return false;
  var col = colCount || sheet.getLastColumn();
  var start = Math.max(2, last - 100);
  var ids = sheet.getRange(start, col, last - start + 1, 1).getValues();
  for (var i = 0; i < ids.length; i++) {
    if (String(ids[i][0]) === String(submissionId)) return true;
  }
  return false;
}

// The restock worklist. One row per ITEM. Reporting the same item again bumps its
// counter and its last-reported date rather than adding a duplicate line, so the
// list length is the length of the actual job. Ticking Done grays the row out; if
// the item is reported missing again afterwards the row reopens.
function addToRestock(p, missing) {
  if (!missing || !missing.length) return;
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(RESTOCK.name);
  if (!sh) {
    sh = ss.insertSheet(RESTOCK.name);
    sh.appendRow(RESTOCK.headers);
    sh.getRange(1, 1, 1, RESTOCK.headers.length)
      .setFontWeight('bold').setBackground('#8c1c2b').setFontColor('#ffffff');
    sh.setFrozenRows(1);
    sh.setRowHeight(1, 34);
    RESTOCK.widths.forEach(function (w, i) { sh.setColumnWidth(i + 1, w); });
    sh.getRange(1, 1, sh.getMaxRows(), RESTOCK.headers.length).createFilter();
  }

  var when = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');
  var who = ((p.firstName || '') + ' ' + (p.lastName || '')).trim();
  var where = p.bag || p.bike || '';

  var last = sh.getLastRow();
  var existing = last > 1 ? sh.getRange(2, 1, last - 1, RESTOCK.headers.length).getValues() : [];
  var index = {};
  for (var i = 0; i < existing.length; i++) index[String(existing[i][1])] = i + 2;  // item -> row

  var fresh = [];
  missing.forEach(function (item) {
    var atRow = index[String(item)];
    if (atRow) {
      var wasDone = sh.getRange(atRow, 1).getValue() === true;
      var count = Number(sh.getRange(atRow, 3).getValue()) || 0;
      // Reported missing again after being restocked: reopen it rather than
      // leaving a ticked row that is no longer true.
      sh.getRange(atRow, 1).setValue(false);
      sh.getRange(atRow, 3).setValue(wasDone ? 1 : count + 1);
      sh.getRange(atRow, 5).setValue(when);
      sh.getRange(atRow, 6).setValue(where);
      sh.getRange(atRow, 7).setValue(who);
      if (wasDone) sh.getRange(atRow, 4).setValue(when);
    } else {
      fresh.push([false, item, 1, when, when, where, who]);
    }
  });

  if (fresh.length) {
    var start = sh.getLastRow() + 1;
    sh.getRange(start, 1, fresh.length, RESTOCK.headers.length).setValues(fresh);
    sh.getRange(start, 1, fresh.length, 1).insertCheckboxes();
  }
  paintRestock(sh);
}

// A ticked row is done, so it should stop competing for attention. Outstanding
// items stay plain; the count is emphasised when something has been asked for
// more than once, because that is the one worth chasing.
function paintRestock(sh) {
  var last = sh.getLastRow();
  if (last < 2) return;
  var n = RESTOCK.headers.length;
  var vals = sh.getRange(2, 1, last - 1, n).getValues();
  for (var i = 0; i < vals.length; i++) {
    var r = i + 2;
    var done = vals[i][0] === true;
    var range = sh.getRange(r, 1, 1, n);
    range.setBackground(done ? '#f1f3f4' : '#ffffff')
         .setFontColor(done ? '#9aa0a6' : '#202124')
         .setFontLine(done ? 'line-through' : 'none');
    sh.getRange(r, 3).setHorizontalAlignment('center')
      .setFontWeight(!done && Number(vals[i][2]) > 1 ? 'bold' : 'normal');
  }
}

// Run this by hand (Run ▸ tidyUp) after pasting an updated script, to reformat
// tabs that already exist and repaint the restock list.
function tidyUp() {
  SERVES.forEach(function (f) {
    var conf = SHEETS[f];
    formatSheet(ensureSheet(conf), conf);
  });
  var rs = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(RESTOCK.name);
  if (rs) paintRestock(rs);
}

// Asks Google whether this token is real, who it belongs to, and whether it was
// issued for THIS site. Without the audience check any valid Google token from
// any app would be accepted, which is the classic way this goes wrong.
function verifiedEmail(idToken) {
  if (!idToken) return '';
  try {
    var res = UrlFetchApp.fetch(
      'https://oauth2.googleapis.com/tokeninfo?id_token=' + encodeURIComponent(idToken),
      { muteHttpExceptions: true });
    if (res.getResponseCode() !== 200) return '';
    var t = JSON.parse(res.getContentText());
    if (OAUTH_CLIENT_ID && t.aud !== OAUTH_CLIENT_ID) return '';
    if (String(t.email_verified) !== 'true') return '';
    if (Number(t.exp) * 1000 < Date.now()) return '';
    return String(t.email || '').toLowerCase();
  } catch (err) {
    console.error('Token check failed: ' + err);
    return '';
  }
}

// ---------------------------------------------------------------- helpers

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
    return k + ' = ' + (expiries[k] || 'not entered');
  }).join('\n');
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

**I edited the script and only one spreadsheet changed.** Only applies to a two-
spreadsheet setup: the copies are independent, so every edit has to be pasted and
re-deployed in *both*, except the `SERVES` line, which is meant to differ. A combined
setup has one copy and cannot drift.

**Saving the script changed nothing.** Saving updates the editor, not what the URL
serves. **Deploy → Manage deployments → ✏️ → Version: New version → Deploy.** Same
URL, new code. This has been the cause every time so far.

**"Missing Items" is empty but the verdict says incomplete.** The verdict text
comes from the site; `missing` is computed from unchecked boxes. If they disagree,
the form was edited in manager mode while it was being filled in — resubmit.

**I want a QR code for a form.** Each check has its own URL. Point any QR generator
at the exact link shown on the Checks & Forms page, e.g.
`https://sonnnnnion.github.io/bike-ops/#jumpkit-check`.
