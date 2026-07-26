CMU EMS crest — assets in this folder
=====================================

cmuems.png            395x395, the ORIGINAL crest as supplied. Purple/gold circle
                      on a white square. Keep this — everything else is derived
                      from it. Square PNG works best if you ever replace it.

cmuems-mark.png       128x128, the same crest with the white square around it
                      masked away (transparent corners). Used in the top bar,
                      which renders it at 38px. Deliberately not larger — a 512
                      version was 207KB for no visible gain.
favicon.ico           16/32/48/64 multi-size, browser tab icon.
favicon-32.png        PNG favicon for browsers that prefer one.
apple-touch-icon.png  180x180, flattened onto white — iOS composites
                      transparency onto BLACK, so this one must not be
                      transparent.

Regenerating the derived files
------------------------------
Only cmuems.png is hand-supplied. If you replace it, rebuild the rest with the
script in the project history (PIL/Pillow required):

    python3 mkfavicon.py     # run from the project root

IMPORTANT — do not "make white transparent" globally on this crest. The
star-of-life behind the building is ALSO white, so a global white-removal punches
holes through the middle of the logo. The script instead finds the crest circle
and masks to it, which only removes the four corners.

Silent-failure warning
----------------------
If a filename stops matching, the <img> slots fall back to a plain "EMS" /
"CMU EMS crest" tile instead of showing a broken image — so a rename fails
QUIETLY. Check the top bar after swapping any file. (This has bitten before: the
code originally expected "cmu-ems-logo.png" and fell back silently for a while.)

Where they are referenced in index.html
---------------------------------------
  cmuems-mark.png   -> top bar <img class="logo-mark">
  favicon.ico / favicon-32.png / apple-touch-icon.png -> <link> tags in <head>
  cmuems.png        -> source only; not currently loaded by the page
Search index.html for "assets/" to find them all.
