---
name: happening-this-week
description: >
  Creates a new "Happening This Week" weekly events slide in Canva for spARK Labs, 
  based on the established brand template. Use this skill whenever the user wants to 
  create, generate, or update a weekly events announcement, "what's happening this week," 
  a weekly events post, or spARK Labs weekly schedule slide. Also trigger when the user 
  mentions adding events to Canva, generating a new week's slide, or producing social/
  internal content for upcoming spARK Labs events.
---

# Happening This Week — Canva Slide Creator

This skill creates a new "Happening This Week" weekly events slide for spARK Labs by copying the exact-count reference template for the number of events that week, then filling in the event content. Each template has only as many card slots as needed — no empty boxes, no cleanup required.

## Reference Templates

Each template is a specific page within a source design. Use `copy-design` with `page_numbers` to pull only that page.

| Events | Source Design ID | Page | Notes |
|--------|-----------------|------|-------|
| 1 | *(not yet defined — use 2-event and delete Card 2 text)* | — | See note below |
| 2 | `DAHBad02D3k` | 2 | Two cards, vertically centered |
| 3 | `DAHBad02D3k` | 3 | Three cards |
| 4 | `DAHBad02D3k` | 12 | Four cards |
| 5 | `DAHBad02D3k` | 1 | Five cards |
| 6 | `DAHMAqWcXsw` | 1 | Six cards, 2-column grid layout |
| 7+ | Split into two slides | — | Group as 4 + remainder, or 3 + 4 |

> **1-event note:** There is no dedicated 1-event template yet. Until one is created, copy the 2-event template (page 2 of `DAHBad02D3k`) and delete all of Card 2's elements: text elements, lightning bolt, AND both card background SHAPE elements (deletable via `delete_element` — shapes appear in the transaction's element list with empty `regions`). No manual cleanup needed.

**Brand**: spARK Labs | www.sp-ark-labs.com  
**Folder**: "Happening This Week" in Canva

---

## Step 1 — Gather Information

Collect all info needed before touching Canva. Either ask the user or parse it from whatever they provide (email, calendar, Slack message). For each event:

- Event type / title (e.g., "Lunch N Learn", "Weekly Member Brainstorm")
- Day number and month (e.g., "16 JUN")
- Speaker/host if any (e.g., "w/ Jane Smith, CEO of Acme")
- Location (default: "3rd Floor, Colorful Corner"; others below)
- Time (e.g., "12:00 PM – 1:00 PM")
- **Members-only or public** (see Badge Rules below)
- Short description if applicable

Also confirm the **week date range** (e.g., "Jun.15 Jun.19").

**Common recurring events — use these defaults if the user gives only the event name:**

| Event | Description | Location | Time | Badge |
|-------|-------------|----------|------|-------|
| Weekly Member Brainstorm | "Bring ideas, questions, and a desire to connect!" | 3rd Floor, Colorful Corner | 3:30 PM – 5:00 PM | MEMBERS |
| Monthly Happy Hour | "Celebrating the innovators and team powering spARK Labs!" | 3rd Floor, Colorful Corner | 4:00 PM – 6:00 PM | MEMBERS |
| Lunch N Learn | *(speaker-dependent)* | 3rd Floor, Colorful Corner | 12:00 PM – 1:00 PM | MEMBERS |
| AIR Supply Session | *(speaker-dependent)* | 3rd Floor, Colorful Corner | *(varies)* | MEMBERS |
| GOLDEN spARKS | "Hosted by CodeBoxx" | 3rd Floor, Vu Studio | 4:00 PM – 5:30 PM | MEMBERS |
| AI Salon | *(topic-dependent)* | 2nd Floor, Innovation Foundation Hall | 6:00 PM – 8:00 PM | PUBLIC |
| Cursor Meetup / community events | — | — | — | PUBLIC |
| UBS x spARK Labs panels | — | — | — | PUBLIC |

---

## Member vs Public Card Treatment

The established design system (verified against past slides, e.g. pages 9 and 13 of `DAHBad02D3k`):

- **Members-only event** = white card, orange "⚡ MEMBERS" ribbon top-right, pink title text, dark body text.
- **Public event** = **entire card is pink (`#E52E71`)**, all text white, **no ribbon, no lightning bolt**. (Not a "pink badge" — the whole card changes color. `#E52E71` is the verified card pink sampled from the actual designs; do not use `#E8185A`.)

**Default**: treat any event as MEMBERS unless the user specifies public, or it matches a known public event type above.

### Members-only events
- Leave the card, ribbon, and lightning bolt untouched
- Badge label text: `    MEMBERS ` (keep leading/trailing spaces)

### Public events — fully automated, no manual fixes (all operations verified to work)

Apply ALL of these in the bulk `perform-editing-operations` call for that card:

1. **Delete the white front card shape** with `delete_element`. Card SHAPE elements ARE returned by `start-editing-transaction` (in the `richtexts` array with empty `regions`) and ARE deletable. Each card has two SHAPEs: the **front white card is the wider one (~521.7 wide)**, offset up-right; the back outline card is ~514.8 wide, offset down-left. Delete the ~521.7-wide one.
2. **Delete the lightning bolt** image fill for that card with `delete_element` (asset ID `MAG19Wbu25E`). Its `editable: false` flag only blocks `update_fill`; deletion works.
3. **Blank the badge text**: `replace_text` → `""`. This makes the whole orange ribbon disappear (the ribbon renders only when the badge text is non-empty).
4. **Recolor to white** (`format_text`, `color: #FFFFFF`): title, speaker/description, location, day number, and month. Leave the time chip alone (it is already white-on-dark).

Result with current templates: a dark outlined card with white text — cleanly differentiated and 100% automated. Once the templates are upgraded to image-based card backgrounds (see "Template Upgrade Path" at the bottom), replace step 1 with a single `update_fill` to the pink card asset `MAHMTsS_E9I` for the exact brand-pink look.

### Canva API facts (tested 2026-06-11 — trust these over guesses)
- Shape **fill colors cannot be changed**, but shapes **can be deleted, repositioned, and resized**.
- `format_text` color changes, `replace_text`, `update_fill` (on `editable: true` image elements), `resize_element`, and `position_element` all work.
- `insert_fill` always inserts **on top of everything** — never use it to put a colored card behind text.
- Pre-made card background assets already in the Canva library: **pink/public `MAHMTsS_E9I`**, **white/members `MAHMTmJnxFQ`** (2086×438, rounded corners, transparent background, sized for the 521.7×109.6 card slot).

---

## Step 2 — Pre-truncate All Text Content

**Do this before touching Canva.** Apply hard character limits now — do NOT rely on thumbnail inspection after the fact.

| Field | Hard limit | Rule |
|-------|-----------|------|
| Event title | 22 chars | Abbreviate words; shorten "and" → "&", drop subtitles |
| Speaker / description | 45 chars | "w/ [First Last], [Company]" — drop role/title if needed |
| Location | 38 chars | Use approved abbreviations below — never write out full venue name |
| Time | no limit | Always fits |
| Month | 3 chars | JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC |
| Day number | 2 chars | Always fits |

**If speaker + description would exceed 45 chars combined**, keep only `w/ [First Last]` and drop everything else.

**If an event title still exceeds 22 chars after abbreviation**, include a `format_text` operation in the same bulk call, setting `font_size` to 28 on that title element.

**Approved location strings (use exactly as written):**

| Venue | Approved string |
|-------|----------------|
| Colorful Corner Coworking Lounge | `3rd Floor, Colorful Corner` |
| Innovation Foundation Hall | `2nd Floor, Innovation Foundation Hall` |
| Vu Studio | `3rd Floor, Vu Studio` |
| Mahaffey / Duke Energy Center | `Mahaffey Theater, St. Pete` |
| ARK Innovation Center | `ARK Innovation Center` |

---

## Step 3 — Select and Copy the Right Template

**Count the events first, then copy only the matching page.**

```
copy-design(
  design_id: "<source design ID>",
  page_numbers: [<page number>]
)
```

This creates a fresh single-page design with exactly the right number of card slots. No unused cards, no cleanup.

| Events | design_id | page_numbers |
|--------|-----------|-------------|
| 1 | `DAHBad02D3k` | `[2]` *(then delete Card 2 text — see Step 5)* |
| 2 | `DAHBad02D3k` | `[2]` |
| 3 | `DAHBad02D3k` | `[3]` |
| 4 | `DAHBad02D3k` | `[12]` |
| 5 | `DAHBad02D3k` | `[1]` |
| 6 | `DAHMAqWcXsw` | `[1]` |

---

## Step 4 — Map Element IDs from the Source Template

**Call `get-design-content` on the source template page (not the copy) to retrieve all richtext element IDs.**

```
get-design-content(
  design_id: "<source design ID>",
  content_types: ["richtexts"],
  pages: [<page number>]
)
```

Use the placeholder text to build a field map before writing any editing operations:

```
Card 1: title → elem_abc | day → elem_def | month → elem_ghi | desc → elem_jkl | location → elem_mno | time → elem_pqr | badge → elem_stu
Card 2: title → elem_... | ...
Header start date → elem_xxx | Header end date → elem_yyy
```

**Then call `start-editing-transaction`** on the newly copied design. Show the thumbnail to confirm the template is correct before making any edits.

---

## Step 5 — Edit the Content

Using the element ID map from Step 4, call `perform-editing-operations` in **one bulk call** with all operations across all cards.

**Fields to update on every slide:**
- Header start date (e.g., "Jun.15")
- Header end date (e.g., "Jun.19")
- Each event card: title, day number, month, speaker/description, location, time, badge text

**Per-card operations by event type** (see "Member vs Public Card Treatment" for details):

| Event type | Operations |
|-----------|-----------|
| MEMBERS | `replace_text` badge → `    MEMBERS `; leave card shape, ribbon, and bolt alone |
| Public | `delete_element` white front card SHAPE (~521.7 wide); `delete_element` bolt (`MAG19Wbu25E`); `replace_text` badge → `""`; `format_text` `#FFFFFF` on title, desc, location, day, month |

**1-event special case:** After populating Card 1, delete all text elements belonging to Card 2 (title, badge, day, month, desc, location, time). The card background shape will remain — tell the user to delete it manually in Canva.

**Font size reduction:** For any title exceeding 22 chars after abbreviation, include `format_text` with `font_size: 28` on that title element in the same bulk call.

---

## Step 6 — Preview & Commit

1. Call `get-design-thumbnail` and show the result to the user
2. **For 1-event slides**, also delete Card 2's two background SHAPE elements with `delete_element` (both the ~521.7-wide front card and the ~514.8-wide back outline) — no manual cleanup needed
3. Once the user approves, call `commit-editing-transaction`
4. Share the edit URL

---

## Tips

- Parse emails, calendar pastes, or Slack messages directly — don't make the user reformat event info
- The design is 16:9, suitable for lobby TV displays, Slack posts, and social sharing
- `start-editing-transaction` returns ALL addressable elements: TEXT and SHAPE elements (with position/dimensions) in `richtexts`, and image fills (with asset IDs and `editable` flag) in `fills`. Shape *colors* are still not readable — color rules live in this skill.
- When creating slides for a full week, do them one at a time: copy → map → edit → commit → share link
- The 6-event template (`DAHMAqWcXsw`) uses a 2-column grid layout — the element naming order may differ from the vertical-list templates. Always re-map element IDs from that template's content before editing.

---

## Template Upgrade Path (one-time, optional — unlocks exact brand-pink public cards)

The current public-event recipe yields a dark outlined card because shape fills can't be recolored via the API. To get the exact pink card (`#E52E71`) automatically, upgrade the templates once by hand in Canva:

1. On each template page (`DAHBad02D3k` pages 1, 2, 3, 12; `DAHMAqWcXsw` page 1), for each card slot: delete the white front card **shape** and replace it with the **image** asset "spARK card background - MEMBERS (white)" (`MAHMTmJnxFQ`) from the asset library, sized 521.7 × 109.6 at the same position, sent backward so it sits behind the card's text but in front of the back outline card.
2. After upgrading, the public-event treatment becomes a single op per card: `update_fill` on that card's background image element → asset `MAHMTsS_E9I` (pink), plus the same text recoloring/badge/bolt ops. Members cards need no change (white asset stays).
3. Detect which template generation you're working with at runtime: upgraded cards appear in the transaction's `fills` array with asset `MAHMTmJnxFQ`; legacy cards appear as SHAPE elements. Use the matching recipe.

Do NOT try to do this upgrade via the API: `insert_fill` always lands on top of text, so the background image must be placed and layered manually in the Canva editor.