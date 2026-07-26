"""Build favicons from the CMU EMS crest.

The crest is a purple/gold circle inscribed in a white square. The white we want
gone is only the four corners OUTSIDE that circle — the star-of-life inside the
crest is also white and must be kept. So: find the circle, mask to it, crop.
A global "make white transparent" would punch holes through the middle.
"""
from PIL import Image, ImageDraw
import os

SRC = "assets/cmuems.png"
OUT = "assets"
SS = 8  # supersample factor for a smooth mask edge

im = Image.open(SRC).convert("RGB")

# Bounding box of everything that isn't near-white -> the crest circle.
mask_nonwhite = im.convert("L").point(lambda p: 0 if p > 242 else 255)
bbox = mask_nonwhite.getbbox()
x0, y0, x1, y1 = bbox
cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
r = max(x1 - x0, y1 - y0) / 2.0
print("source %s  non-white bbox=%s  center=(%.1f,%.1f)  r=%.1f" % (im.size, bbox, cx, cy, r))

# Circular alpha mask, drawn big then downsampled so the edge is antialiased.
big = Image.new("L", (im.width * SS, im.height * SS), 0)
ImageDraw.Draw(big).ellipse(
    [(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], fill=255
)
alpha = big.resize(im.size, Image.LANCZOS)

rgba = im.convert("RGBA")
rgba.putalpha(alpha)

# Crop tight to the circle so the icon fills the tab square edge to edge.
pad = 1
crop = rgba.crop((int(cx - r) - pad, int(cy - r) - pad,
                  int(cx + r) + pad + 1, int(cy + r) + pad + 1))
print("cropped to %s" % (crop.size,))

# Transparent mark for the top bar. Rendered at 38px, so 128 covers 3x displays
# with room to spare — a 512 master here was 207KB for no visible benefit, and
# cmuems.png is already the full-resolution source if a bigger one is ever needed.
crop.resize((128, 128), Image.LANCZOS).save(os.path.join(OUT, "cmuems-mark.png"))

# Multi-size .ico for the browser tab
ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
crop.save(os.path.join(OUT, "favicon.ico"), format="ICO", sizes=ico_sizes)

# PNG favicon for browsers that prefer it
crop.resize((32, 32), Image.LANCZOS).save(os.path.join(OUT, "favicon-32.png"))

# Apple touch icon: iOS composites transparency onto black, so flatten to white
# and inset the crest slightly, matching how the topbar already presents it.
touch = Image.new("RGBA", (180, 180), (255, 255, 255, 255))
inset = crop.resize((164, 164), Image.LANCZOS)
touch.paste(inset, (8, 8), inset)
touch.convert("RGB").save(os.path.join(OUT, "apple-touch-icon.png"))

for f in ("cmuems-mark.png", "favicon.ico", "favicon-32.png", "apple-touch-icon.png"):
    p = os.path.join(OUT, f)
    print("  wrote %-22s %6d bytes" % (f, os.path.getsize(p)))
