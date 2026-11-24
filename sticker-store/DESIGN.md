# لزّقها: Design

A shop for printable PDF sticker packs, in Arabic, right to left. Structure follows the
`design-taste-frontend` skill (product page); this file is written in the shape of the
`awesome-design-md` specs.

## Visual theme
Old paper and ink, taken from the client's own PDF covers: dusty rose paper, brown ink, a burgundy
seal colour. Flat grounds, no gradients or glows. The product is always the real page images.

## Colour roles (light / dark)
| Token | Light | Dark | Role |
|---|---|---|---|
| `--bg` | #f6ebe3 | #1d1512 | page ground |
| `--surface` | #fbf4ef | #261c18 | modal ground |
| `--ink` | #3a2216 | #f6e9df | all body text (7:1 or more) |
| `--muted` | #6e5244 | #cdb2a4 | labels and meta only |
| `--accent` | #8c2f3a | #e5939a | primary button, brand band, mark |
| `--line` | #e3cfc2 | #44322a | rules |
| `--inv-bg` | #2b1a12 | #120c0a | closing and footer |

## Type
- Display: Aref Ruqaa 700 (h1 72/40px, h2 56/36px). Ruqaa needs line-height 1.2 or more.
- Text: IBM Plex Sans Arabic 400 to 600, body 17px, lead 20px.

## Layout
- One `.wrap`, 1200px wide, gutters 16 / 24 / 64px. 12 columns, 24px gaps.
- Splits use one pair of lines: the heading on 7 columns, the side on the other 5.
- Each section is one or two screens on a desktop; phones grow with content.
- Order: hero (3D planet of the pages), collections (pinned photo chapters), the range
  (15 files, 6 columns), details (specs and FAQ), bundle (brand band), closing and footer.

## Components
- Buttons: one pill, primary (accent fill) and secondary (ink outline), 48px and 44px.
  Hover lifts 2px, press scales to .98.
- Range card: the cover in a 595:842 frame, name, designs and pages, price, add button.
  Hover lifts the card 2px and zooms the cover to 1.03 inside its frame. No tilt.

## Motion
- The hero enters once on load. The planet turns slowly, follows a drag, and a tap on a page
  opens that file's preview. Under reduced motion it stands still.
- One scroll moment: photo-chapters in `#collections`.

## Don't
- No tilted pictures, no stacked "page" decorations, no marquee, no shine effects.
- No ring or orbit around the planet.
- Never show one picture twice outside the preview.
