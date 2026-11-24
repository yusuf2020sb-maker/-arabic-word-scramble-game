# لزّقها: Design

A shop for printable PDF sticker packs, in Arabic, right to left. The look follows the owner's
reference video: a dark streetwear catalogue with one light section, heavy display type, tiny
technical labels, one hot orange accent and a ring cursor. Committed to this one dark look.

## Colour roles
| Token | Value | Role |
|---|---|---|
| `--night` | #0a0d10 | page ground |
| `--night-2`, `--night-3` | #10161b, #18222a | bands, cards |
| `--glow` | #1f4656 | cool radial light behind the hero and the bundle |
| `--paper` | #eeece7 | the light collection and file sections |
| `--snow` | #f3f4f2 | text on dark |
| `--fog` | #9aa4ab | labels on dark |
| `--ink` | #0d0f12 | text on light |
| `--hot` | #ff5a1f | the one accent: buy buttons, label dots, prices in the bundle |

## Type
- Display: Alexandria 900, very large (hero word up to 420px, section titles 100 to 150px),
  line-height .95. The hero word is skewed 8 degrees, outlined on top and filled at the bottom.
- Text: IBM Plex Sans Arabic 400 to 700. Labels 11.5px, 600, with an orange dot.

## Sections
1. Hero: the word «لزّقها» behind the 3D planet of PDF pages; labels in the corners, two buttons.
2. Numbers band: big headline, one full page picture with a moving scan light, four stats.
3. Category panels: five tall photos; hover widens one; a click filters the collection.
4. The set: four covers standing in a lineup with reflections, a side list that highlights with them.
5. Collection (light): huge title, filter tabs, covers hanging on a rail; drag to scroll.
6. File view (light): page thumbnails, the big page, name, price, specs, one orange button.
7. Bundle: a floating 3D stack of covers that fans out on hover.
8. Print guide: four editorial cards over inner pages.
9. Footer: links, newsletter, the name set across the page.

## Motion
- Section titles rise once when they enter (visible without script and under reduced motion).
- Ring cursor on fine pointers only; off under reduced motion.
- Buttons lift 2px on hover and press on click.

## Don't
- No ring around the planet, no shine on covers, no pastel or violet.
- Never more than one accent colour.
