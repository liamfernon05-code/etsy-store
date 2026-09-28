# Pet collection artwork (print files)

Ten sweatshirt designs, built as **vector art**, not generated images.

- `png/` transparent PNG print files, sRGB, 300 DPI (upload these to Printify). One per design per blank colour: `NN-slug_<blank>.png`, primary blank first in `REPORT.md`.
- `svg/` vector masters (text is outlined, so no font install needed to open or edit them).
- `previews/` flat sweatshirt mockups (approximate colours, for review only, not listing photos) and `contact_sheet.png`.
- `REPORT.md` sizes and contrast of each ink against its blank.

## How it was made (and what it is not)

- **Type:** outlined from open-licence Google Fonts (SIL OFL 1.1): Bowlby One, Alfa Slab One, Fraunces 900, DM Sans 700/800. Licence texts are in `fonts/`. Kerning via HarfBuzz.
- **Illustrations:** every spot illustration (tennis ball, grooming brush, husky, dachshund, paw ring, heart-and-house, leash, cat, calendar, socks, snowflakes) is constructed from hand-written vector geometry in `designs.py`, with slight deliberate edge irregularity for a cut-paper feel.
- **No image generator was used.** The `image prompts` in `designs/pet_collection_FINAL.md` are now unnecessary.
- The code and layout were written with an AI assistant (Claude). Whether and how to disclose that on Etsy is your call: read Etsy's Creativity Standards / AI-disclosure wording at listing time. These files are original work you can edit further in any vector editor (Inkscape, Illustrator, Affinity) to make them more distinctly yours; that is encouraged.

## Rebuild

```bash
pip install fonttools brotli uharfbuzz pillow
npm i playwright-core        # plus a Chromium binary (PLAYWRIGHT_BROWSERS_PATH or CHROMIUM_PATH)
python -m artwork.build      # from the repo root
```

## Known limits (check on your samples)

- Blank hex colours used for contrast and previews are **estimates**; re-measure on real samples. All text inks are >= 4.5:1 on their estimated blanks; accent inks are graphic fills only.
- Some blanks (Sand, Forest, Maroon, Ash) may not be offered by the print provider; fallback colourways are included where the plan called for them.
- Layouts run taller than the original 10 x 7-9 in sheet sizes for a few designs (#5, #8, #9) so the type stays large; all are within a normal chest print (max ~11 in tall).
- Slogans have **not** been cleared with USPTO/Etsy exact-phrase searches. Do that before listing.
- Headline cap heights: #5 and #9 headlines are slightly under the 0.9 in rule from the production sheets because of long lines; they are still 0.75 in or more. Check legibility on the sample.
