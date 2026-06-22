#!/usr/bin/env python3
"""Add contextual alternates to Source Han Serif for smart quote/ellipsis width.

Default cmap is swapped to proportional (half-width) glyphs for quotes and
ellipsis. A calt rule substitutes them back to full-width when adjacent to CJK.
"""

from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeatures
import tempfile, os, sys

PROP_MAP = {
    0x2018: ("cid63185", "cid63036"),
    0x2019: ("cid63186", "cid63037"),
    0x201C: ("cid63187", "cid63039"),
    0x201D: ("cid63188", "cid63040"),
    0x2026: ("cid00735", "cid63070"),
}

CJK_RANGES = [
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
    (0x20000, 0x2A6DF),
]

CJK_PUNCT_RANGES = [
    (0x3001, 0x3003),
    (0x300A, 0x300B),
    (0x3010, 0x3011),
    (0x30FB, 0x30FB),
    (0xFF01, 0xFF01),
    (0xFF08, 0xFF09),
    (0xFF0C, 0xFF0C),
    (0xFF1A, 0xFF1B),
    (0xFF1F, 0xFF1F),
]


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "/tmp/SourceHanSerifCN-Regular.otf"
    dst = sys.argv[2] if len(sys.argv) > 2 else "/tmp/SourceHanSerifCN-Regular-calt.otf"

    font = TTFont(src)
    cmap = font.getBestCmap()
    glyph_order = font.getGlyphOrder()

    # Collect CJK glyphs present in font for the @CJK class
    cjk_glyphs = []
    for cp, glyph in cmap.items():
        for lo, hi in CJK_RANGES + CJK_PUNCT_RANGES:
            if lo <= cp <= hi:
                cjk_glyphs.append(glyph)
                break

    # Swap default cmap to proportional glyphs
    full_glyphs = []
    prop_glyphs = []
    for cp, (full, prop) in PROP_MAP.items():
        full_glyphs.append(full)
        prop_glyphs.append(prop)
        for table in font["cmap"].tables:
            if table.isUnicode() and cp in table.cmap:
                table.cmap[cp] = prop

    # Write OpenType feature code and compile
    fea_code = _build_fea(cjk_glyphs, full_glyphs, prop_glyphs)
    fea_path = tempfile.mktemp(suffix=".fea")
    with open(fea_path, "w") as f:
        f.write(fea_code)

    try:
        addOpenTypeFeatures(font, fea_path)
    finally:
        os.unlink(fea_path)

    font.save(dst)
    print(f"Saved: {dst}")


def _build_fea(cjk_glyphs, full_glyphs, prop_glyphs):
    cjk_class = " ".join(sorted(set(cjk_glyphs)))
    prop_class = " ".join(prop_glyphs)
    full_class = " ".join(full_glyphs)

    return f"""\
@CJK = [{cjk_class}];
@PROP = [{prop_class}];
@FULL = [{full_class}];

feature calt {{
    # After CJK: use full-width
    lookup prop_to_full {{
        sub @PROP by @FULL;
    }} prop_to_full;

    lookup after_cjk {{
        sub @CJK @PROP' lookup prop_to_full;
    }} after_cjk;

    # Before CJK: use full-width
    lookup before_cjk {{
        sub @PROP' lookup prop_to_full @CJK;
    }} before_cjk;
}} calt;
"""


if __name__ == "__main__":
    main()
