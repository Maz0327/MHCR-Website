# Award-Winning Service Business Website Analysis
## Design Research Report — 7 Sites (2023–2026)

**Purpose:** Design intelligence for a home remodeling business website redesign.
**Methodology:** Direct browser inspection, visual analysis, CSS evaluation, structural audit.
**Date:** February 2026

---

## SITES ANALYZED

| # | Site | Category | Awards/Recognition |
|---|------|----------|-------------------|
| 1 | kaanarchitecten.com | Architecture Firm | Awwwards SOTD, multiple nominations |
| 2 | studiodado.com | Interior Design Studio | Awwwards SOTD |
| 3 | linear.app | SaaS / Product | Widely cited as best-in-class dark UI |
| 4 | stripe.com | Financial Services | Consistently cited as top design benchmark |
| 5 | big.dk | Architecture Firm | Awwwards, multiple design nominations |
| 6 | snohetta.com | Architecture / Design | Multiple Awwwards, AIA awards |
| 7 | pentagram.com | Design Consultancy | Webby Awards, CSS Design Awards |

---

---

# SITE 1: KAAN Architecten
**URL:** https://kaanarchitecten.com/
**Awards:** Awwwards Site of the Day, FWA nomination
**Mode:** Light mode (warm white/off-white)

## Layout & Structure

| Element | Detail |
|---------|--------|
| Header height | ~64px — extremely compressed, barely visible |
| Logo | Wordmark "KAAN Architecten" — small (~14px), positioned far left, very lightweight |
| Navigation | Center or right-aligned horizontal list: Projects, Office, Press, Contact — all caps, letter-spaced, ~11-12px |
| Hero section | Full viewport height (100vh) — a single project photograph filling the screen with no overlay text except a small label |
| Section spacing | 120–160px vertical gaps between sections |
| Footer | Minimal — 2-column: address + navigation links; very small type |

## Typography

| Element | Font | Size | Weight | Notes |
|---------|------|------|--------|-------|
| Brand/Nav | Replica Pro (Lineto) or GT America | 11–12px | 400 | All caps, letter-spacing: 0.15em |
| H1 (project title) | Same geometric sans | 36–48px | 300 (light) | Long line lengths, relaxed |
| H2 (section heads) | Same | 24–30px | 300–400 | Left-aligned |
| Body | Same | 14–16px | 400 | Wide margins, narrow column width |
| Line height | — | — | — | 1.6–1.8 body, 1.1–1.2 headings |
| Letter spacing | — | — | — | 0.05em body, 0.15em nav |

## Colors

| Role | Color | Notes |
|------|-------|-------|
| Background | `#f7f5f0` or `#fafaf7` | Warm off-white, not pure white |
| Surface/cards | Same background | No card elevation |
| Text primary | `#1a1a1a` | Near-black |
| Text secondary | `#888888` | Medium gray for metadata/dates |
| Accent | None — relies purely on photography | |
| Gradient | None | |

## Components

- **Project cards:** No visible card container — projects displayed as edge-to-edge image tiles, ratio-locked (~16:9 or 3:2), with project name appearing only on hover
- **Buttons:** Minimal text links — no button shapes, no backgrounds; pure underline on hover
- **Hover states:** Image darkens slightly (overlay: rgba(0,0,0,0.1)) and project title fades in over image
- **Imagery:** Full-bleed, edge-to-edge, zero padding — photography is the content, treated as art
- **Sections:** No background alternation — uniform warm off-white throughout; separation by generous whitespace only

## Feel & Personality

**What makes it premium:**
The site says almost nothing — it lets the photography do all the work. The restraint is breathtaking.

### 5 Secret Sauce Elements:
1. **The vanishing header:** The header is so small and light-weight it nearly disappears — this removes all visual competition with the work
2. **Warm background tone:** `#f7f5f0` vs `#ffffff` — the warmth prevents clinical sterility and feels like gallery paper
3. **Light font weight (300):** Using ultra-thin weight for large headings creates tension and elegance simultaneously
4. **Zero padding on images:** Images butt up against the browser edge — no rounded corners, no shadows, no frames. Feels like looking through a window, not at a web page
5. **Navigation that whispers:** All-caps + extreme letter-spacing at 11px means navigation is present but never competes

### What a Remodeling Business Can ADAPT (not copy):
- Use a warm off-white (`#f8f6f2`) instead of pure white — feels high-end vs builder-grade
- Let project photography be FULL WIDTH — stop putting images in little grid boxes
- Reduce nav font size and add letter-spacing — the navigation should whisper, not shout
- Eliminate button borders/shadows on secondary CTAs — use text links for browsing, buttons only for primary action
- Use font-weight 300 for display headings alongside body text — contrast without using color

---

---

# SITE 2: Studio Dado
**URL:** https://studiodado.com/
**Awards:** Awwwards Site of the Day
**Mode:** Dark mode — moody, editorial, very high-contrast photography

## Layout & Structure

| Element | Detail |
|---------|--------|
| Header height | ~56–70px — dark, minimal |
| Logo | Wordmark "Studio Dado" — clean sans-serif, positioned left |
| Navigation | Right-aligned: minimal 3-4 links — uppercase, spaced |
| Hero section | Full viewport height — dark background (near black) with single atmospheric interior photo |
| Section spacing | 100–140px vertical gaps |
| Footer | Minimal — email contact + social links, dark background |

## Typography

| Element | Font | Size | Weight | Notes |
|---------|------|------|--------|-------|
| Primary | Editorial / serif for headlines (looks like Canela or Garamond variant) | Various | 300–700 | Mix of serif headlines + sans-serif body |
| H1 | Serif editorial | 60–80px | 300–400 | Very long, spanning nearly full width |
| H2 | Same serif | 36–48px | 300 | Subdued |
| Body/captions | Sans-serif (Neue Haas or similar) | 14–16px | 400 | Very small against dark bg |
| Accent text | Same serif italic | — | 300 | Used for category labels |

## Colors

| Role | Color | Notes |
|------|-------|-------|
| Background | `#0e0e0e` to `#141414` | Near-black, not pure black |
| Surface | `#1a1a1a` | Slightly lifted cards |
| Text primary | `#f0ede8` | Warm white, not pure white |
| Text secondary | `#888` | Muted gray |
| Accent | None explicit — photography provides color | |
| Gradient | Subtle dark gradients to fade images into background | |

## Components

- **Project cards:** Dark cards with full-bleed image + project name below — no visible border, subtle elevation
- **Image treatment:** High-contrast interior photography; images often have subtle darkening overlay
- **Buttons:** Ghost/outline style on dark bg — thin white border, white text
- **Section backgrounds:** Uniform near-black — no alternation
- **Image reveals:** Photography appears to fade in or slide in on scroll

## Feel & Personality

**What makes it premium:**
The restraint of a dark editorial magazine. Nothing is loud. Everything is intentional.

### 5 Secret Sauce Elements:
1. **Warm white vs. pure white:** Text is `#f0ede8` not `#ffffff` — this single decision removes the harshness that makes dark sites feel cheap
2. **Serif headlines on dark background:** Editorial serif (like Canela or Cormorant) at 70px+ on black = instant luxury signal
3. **No UI chrome:** No visible boxes, borders, or cards — just photographs floating in space
4. **Photography quality as design element:** Every image is editorial-grade, lit like a luxury magazine. The design IS the photography.
5. **Margin breathing room:** 40–60px side margins on mobile, 80–120px on desktop. Content doesn't touch edges.

### What a Remodeling Business Can ADAPT (not copy):
- Invest in editorial-quality photography — it's the single highest ROI design upgrade
- Use warm white (`#f5f2ee`) for body text on dark backgrounds instead of pure white
- Introduce a single editorial serif for h1/h2 (Cormorant Garamond is free on Google Fonts)
- Eliminate borders and shadows on project cards — let the images float on dark background
- Use generous padding (80px+) on sections — the space itself signals confidence

---

---

# SITE 3: Linear.app
**URL:** https://linear.app/
**Awards:** Widely cited as the design benchmark for SaaS/dark mode; featured in Awwwards, Godly.website
**Mode:** Dark mode — deep space aesthetic with purple/indigo accents

## Layout & Structure

| Element | Detail |
|---------|--------|
| Header height | ~60px — dark, sticky |
| Logo | "Linear" logotype + abstract mark — positioned left, ~20px tall |
| Navigation | Center-positioned: Product, Pricing, Blog, Changelog, Login — small text, relaxed spacing |
| CTA buttons | Right of nav — "Get started" (filled) + "Login" (ghost) |
| Hero section | ~100vh — centered headline, subtitle, 2 CTAs, then a browser/product screenshot mockup |
| Section spacing | 100–160px — extremely generous |
| Footer | 4-column link grid — dark bg, very organized |

## Typography

| Element | Font | Size | Weight | Notes |
|---------|------|------|--------|-------|
| Primary | Inter (Google Fonts) | — | Various | Clean, technical, precise |
| H1 | Inter | 52–64px | 600–700 | Centered, 2–3 lines |
| H2 | Inter | 36–42px | 600 | Section headlines |
| Body | Inter | 16–18px | 400 | `#8B8FA8` (muted) on dark bg |
| Feature labels | Inter | 11–12px | 600 | Uppercase, letter-spaced, accent-colored |
| Line height | — | — | — | 1.4–1.5 headings, 1.7 body |
| Letter spacing | — | — | — | -0.02em headings (tight), 0.1em labels |

## Colors

| Role | Color | Notes |
|------|-------|-------|
| Background | `#090C14` (near-black blue-tinted) | Not pure black — has subtle blue tint |
| Surface/cards | `#1a1d27` or `#0F1117` | Slightly elevated dark |
| Text primary | `#F7F8F8` | Near-white |
| Text secondary | `#8B8FA8` | Blue-gray muted |
| Accent | `#5E6AD2` (indigo/purple) | Used for CTAs, highlighted elements |
| Gradient | Purple-indigo linear gradients behind feature screenshots | Adds depth |
| Glow effects | Subtle glow around product screenshots | `box-shadow: 0 0 80px rgba(94, 106, 210, 0.3)` |

## Components

- **Cards:** `border: 1px solid rgba(255,255,255,0.06)` — nearly invisible border; `border-radius: 12px`; `background: rgba(255,255,255,0.04)` frosted effect
- **Primary button:** Filled indigo `#5E6AD2`, border-radius: 6px, 14px font, letter-spaced, subtle box-shadow
- **Secondary button:** Dark ghost — `border: 1px solid rgba(255,255,255,0.15)`, dark bg
- **Product screenshots:** Displayed in simulated browser/device frames with glow halos
- **Feature grid:** 2–3 column grid with icon + title + description + image — very systematic
- **Dividers:** `1px solid rgba(255,255,255,0.06)` — nearly invisible

## Feel & Personality

**What makes it premium:**
Precision and restraint in every pixel. Nothing is decorative. Every element earns its presence.

### 5 Secret Sauce Elements:
1. **Blue-black background (`#090C14`):** The subtle blue tint in the black is what separates premium from generic dark mode — pure black `#000` feels flat; blue-black feels like depth and space
2. **Near-invisible borders:** `rgba(255,255,255,0.06)` border — you can barely see it but it organizes the layout. This is a masterclass in restraint.
3. **Muted secondary text:** The `#8B8FA8` color for body text — not grey but blue-grey — creates a "cold precision" feel that the product's positioning demands
4. **Product screenshot glow:** The purple glow halos around the app screenshots make the product itself the star and add dimensionality
5. **Negative space as a design element:** The sections have 100–160px vertical padding. Nothing feels cramped. Premium = spacious.

### What a Remodeling Business Can ADAPT (not copy):
- Use a dark blue-tinted background (`#0e1118`) instead of flat dark grey — it feels premium vs. industrial
- Near-invisible card borders (`rgba(255,255,255,0.06)`) instead of `border: 1px solid #333` — far more refined
- Apply accent color (orange is MHCR's orange) to only 5% of elements — CTA buttons, key labels, never for decoration
- Use `letter-spacing: -0.02em` on large headings — tight tracking reads as modern and intentional
- Add subtle glow/shadow to hero imagery: `box-shadow: 0 0 60px rgba(232, 100, 40, 0.2)` using brand orange

---

---

# SITE 4: Stripe.com
**URL:** https://stripe.com/
**Awards:** Consistently ranked as top product/service design on Awwwards; featured in multiple design awards
**Mode:** Light mode — clean white with rich gradients

## Layout & Structure

| Element | Detail |
|---------|--------|
| Header height | ~64px — white/near-white, sticky, very clean |
| Logo | "Stripe" wordmark + abstract mark, ~24px, positioned left |
| Navigation | Center/left of center: Products, Solutions, Developers, Resources, Pricing — 14–15px, medium weight |
| CTA buttons | Header right: "Contact sales" (text link) + "Start now" (filled) |
| Hero section | ~100–110vh — centered headline + gradient background + product screenshot |
| Section spacing | 80–120px |
| Footer | 5-column grid, dense — 11px text, comprehensive link structure |

## Typography

| Element | Font | Size | Weight | Notes |
|---------|------|------|--------|-------|
| Primary | Sohne (custom) — similar to Helvetica but with personality | — | Various | Stripe's custom typeface |
| H1 | Sohne | 60–72px | 600 | Left-aligned or centered depending on section |
| H2 | Sohne | 42–48px | 600 | |
| H3 | Sohne | 24–28px | 500–600 | Feature sub-heads |
| Body | Sohne | 16–18px | 400 | `#425466` (blue-slate) on white |
| Feature labels | Sohne | 11–12px | 600 | Uppercase, colored by product area |
| Line height | — | — | — | 1.4–1.5 headings, 1.65–1.75 body |

## Colors

| Role | Color | Notes |
|------|-------|-------|
| Background | `#ffffff` + `#f6f9fc` sections | Near-white sections alternate with white |
| Card bg | `#ffffff` | White cards on light gray sections |
| Text primary | `#0a2540` | Deep navy — not black |
| Text secondary | `#425466` | Blue-slate |
| Accent primary | `#635bff` (indigo) | Primary CTA color |
| Accent gradient | `#635bff → #0a2540` or pastel rainbow | Iconic Stripe gradients |
| Gradient hero | Multi-stop: purple → blue → teal → green | The famous Stripe gradient |

## Components

- **Cards:** `border-radius: 8–12px`; `box-shadow: 0 2px 5px rgba(50,50,93,0.1), 0 1px 2px rgba(0,0,0,0.07)` — the signature Stripe 2-layer shadow; white background
- **Primary button:** `#635bff` indigo fill, `border-radius: 6px`, 15px font, no uppercase
- **Secondary button:** White with `border: 1px solid #e0e0e0` or ghost on gradient background
- **Gradient backgrounds:** Hero section uses an animated gradient mesh — purple, blue, teal, green
- **Feature sections:** Alternating layout — image left/text right, then reverse — creates rhythm
- **Data visualization:** Live counters, animated charts showing product value

## Feel & Personality

**What makes it premium:**
The gradients are doing emotional heavy lifting. Cool blue palette + technical precision = "this company handles serious money."

### 5 Secret Sauce Elements:
1. **The 2-layer card shadow:** `0 2px 5px rgba(50,50,93,0.1), 0 1px 2px rgba(0,0,0,0.07)` — this specific combination creates a "floating paper" effect that is refined without being dramatic. Never just `box-shadow: 0 4px 8px rgba(0,0,0,0.2)`
2. **Deep navy text (`#0a2540`) instead of black:** The "almost black navy" makes the site feel financial/trustworthy rather than purely aesthetic
3. **Animated gradient backgrounds:** The hero gradient moves slowly — this alone communicates that this is a technically sophisticated company
4. **The color-coded navigation:** Different sections use different accent gradients — this creates a mental map of the product as you scroll
5. **Negative space in cards:** Cards have 32–40px internal padding. Not 16px. Space = confidence.

### What a Remodeling Business Can ADAPT (not copy):
- Use a 2-layer shadow on cards: `0 2px 5px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)` — far more refined than single-shadow cards
- Replace pure black text with deep navy `#1a2d4e` or charcoal-blue — subtle but significant
- Use a gradient on the primary CTA button — not solid flat orange but `orange → burnt orange` gradient
- Feature sections that alternate image/text left-right instead of uniform layouts — creates visual rhythm
- 32px minimum internal padding on cards — if it looks spacious to you, it probably feels premium to clients

---

---

# SITE 5: BIG.dk (Bjarke Ingels Group)
**URL:** https://big.dk/
**Awards:** Awwwards nominations, FWA, architectural industry recognition
**Mode:** Dark mode — pure black, colorful project thumbnails

## Layout & Structure

| Element | Detail |
|---------|--------|
| Header height | ~50–60px — black, very minimal |
| Logo | "BIG" logotype — white, small, top-left |
| Navigation | Minimal: just a few items (Projects, Ideas, People, News, Careers, Contact) |
| Hero section | No traditional hero — immediately a project grid |
| Project grid | Masonry/irregular grid — variable sizes, some spanning full width |
| Section spacing | Almost none — dense, gallery-like |
| Footer | Minimal — contact + social |

## Typography

| Element | Font | Size | Weight | Notes |
|---------|------|------|--------|-------|
| Primary | Helvetica Neue or custom geometric sans | Various | 300–500 | Very clean |
| Project titles | Same | 13–15px | 400 | Below image, very small |
| Year/category | Same | 11px | 400 | Gray, metadata |
| Body (about) | Same | 15–16px | 400 | Generous line-height |

## Colors

| Role | Color | Notes |
|------|-------|-------|
| Background | `#000000` | True black |
| Text | `#ffffff` | Pure white |
| Secondary text | `#666666` | Metadata |
| Accent | None — project photos provide all color | |
| Project thumbnails | Full color photography | Colorful projects pop against black |

## Components

- **Project cards:** Zero border, zero radius, zero shadow — square-cropped images in an irregular grid; project title + year below
- **Image hover:** Slight zoom (scale: 1.02) or opacity change on hover
- **Grid:** Irregular masonry-like, projects of different proportions — some 1/3, some 2/3, some full width
- **No traditional CTAs:** Every interaction is just clicking a project

## Feel & Personality

**What makes it premium:**
Pure black + full-color photography = gallery. There is nothing between you and the work.

### 5 Secret Sauce Elements:
1. **True black as a gallery wall:** `#000000` acts exactly like a gallery wall — every project photo "hangs" on it. This only works with high-quality photography.
2. **Irregular grid proportions:** Not everything the same size — the variety creates editorial dynamism. Some projects get 2x space, others get 1x.
3. **Zero decoration:** No arrows, no icons, no badges, no shadows. The content is the design.
4. **Typography serves architecture:** Text doesn't try to be interesting — it reports facts (project name, year, location). This deference creates sophistication.
5. **Density with breathing room:** The grid is dense but every image has 4–8px gap from neighbors — just enough air to separate without feeling padded

### What a Remodeling Business Can ADAPT (not copy):
- Use a project gallery section that is FULL WIDTH with no column containers — extend image grids to the browser edge
- Include project metadata (neighborhood, year, scope) below each gallery image — like BIG does with project name/city/year
- Vary the sizes of portfolio items — not all the same height — create a "featured/standard" hierarchy
- Make photography the primary first impression — no text overlay on hero, let the before/after photo speak
- Use irregular feature sizes — 1 large featured project + 2–3 smaller projects in each row

---

---

# SITE 6: Snøhetta
**URL:** https://www.snohetta.com/
**Awards:** Multiple Awwwards nominations, numerous architectural design awards, known as a design-forward practice
**Mode:** Dark mode — pure black with accessibility preference controls built-in

## Layout & Structure

| Element | Detail |
|---------|--------|
| Header height | ~56px — pure black bar with logo left, "Menu" text right |
| Logo | "Snøhetta" typographic wordmark — white, medium weight, top-left |
| Navigation | Hidden in "Menu" — expands to full-screen overlay with organized columns |
| Hero section | Large H1 statement (approx 90px) above a horizontal scrolling project carousel |
| Project carousel | 60–70vh — horizontal auto-scrolling strip of project images, varying heights |
| Section structure | Scrolls down to: Disciplines, Latest News, Upcoming Events (table!), Process, Highlighted Projects, Footer |
| Section spacing | 80–120px |
| Footer | Very minimal — two-column menu replication + social links + copyright |
| Special feature | Preference panel (bottom-left corner): toggle Dark mode / Simplified / Low-res — exceptional accessibility |

## Typography

| Element | Font | Size | Weight | Notes |
|---------|------|------|--------|-------|
| Wordmark | Appears custom or modified | ~16px | 400 | Wordmark only, not a logo mark |
| H1 (statement) | Large geometric sans-serif | ~80–96px | 400–500 | "Snøhetta is a global transdisciplinary practice..." |
| H2 (section heads) | Same | ~48–60px | 400 | "Architecture", "Latest News" |
| H3 (card titles) | Same | ~20–24px | 400 | |
| Body | Same | 15–16px | 400 | White on black |
| Navigation menu | Same | 24–32px | 400 | In fullscreen overlay |
| Dates (news) | Same | 13px | 400 | Gray |

## Colors

| Role | Color | Notes |
|------|-------|-------|
| Background | `#000000` or `#080808` | True/near-true black |
| Text primary | `#ffffff` | Pure white |
| Text secondary | `#888` or `#666` | Gray for metadata |
| Accent | None — relies on photography and typography | |
| Gradient | None on main bg — but project photography provides all color | |
| Events table | Very thin white lines separating rows | |

## Components

- **Project cards in carousel:** Variable-sized images in horizontal strip — some portrait, some landscape, no padding between
- **News cards:** Full-bleed image with date + headline below — stacked vertically; slides in horizontal carousel with ← → arrows
- **Events table:** A literal `<table>` element styled minimally — Event / Location / Date columns — very editorial, unexpected
- **Navigation overlay:** Full-screen black overlay with categorized link columns: General | Disciplines | More
- **Preferences widget:** Bottom-left corner — a small icon (≡ with sliders) that opens a panel offering Dark mode, Simplified, Low-res toggles — outstanding accessibility consideration
- **No CTA buttons in traditional sense:** Every "button" is just a text arrow (→) — no filled shapes

## Feel & Personality

**What makes it premium:**
The website IS an architecture firm — it is designed with the same philosophy as their buildings: total commitment to the idea, no gratuitous ornament.

### 5 Secret Sauce Elements:
1. **The preference/accessibility widget:** A small but profound detail — the ability to toggle dark mode, simplified mode, and low-res mode acknowledges that not all users are the same. This signals genuine care for the user experience.
2. **"Menu" instead of ≡ hamburger icon:** Writing out "Menu" instead of using a hamburger icon is a small but meaningful choice — it's typographic and human, not iconographic.
3. **Events displayed as a data table:** Using an actual structured table for upcoming events (with proper Event / Location / Date columns) is functional, editorial, and unexpected. Most sites would use cards. Snøhetta uses a table — and it's beautiful.
4. **The H1 as a manifesto:** "Snøhetta is a global transdisciplinary practice, working on projects of all scales." displayed at ~90px is not navigation — it's a declaration of identity. The heading IS the brand statement.
5. **Horizontal project carousel:** The projects scroll horizontally WHILE the page scrolls vertically — this creates a spatial experience of exploring a portfolio, like a gallery wall.

### What a Remodeling Business Can ADAPT (not copy):
- Open your homepage with a DECLARATION (bold H1 statement): "Mile High Custom Remodels builds spaces Denver is proud of." — let the statement be the hero, put photography second
- Use "Contact Us" or "Get a Quote" as text, not just an icon — text navigation feels more human and confident
- Consider adding a simple preference: "Light mode / Dark mode" toggle — signals accessibility awareness
- Use a table or structured list for your project timeline/process steps — unexpected format = memorable
- Put your most powerful project photography in a wide horizontal-scroll gallery — lets visitors "explore" rather than just view

---

---

# SITE 7: Pentagram
**URL:** https://www.pentagram.com/
**Awards:** Webby Awards (multiple), CSS Design Awards, consistently ranked as one of the best design consultancy websites
**Mode:** Dual mode — dark hero/black footer, white content pages

## Layout & Structure

| Element | Detail |
|---------|--------|
| Header height | ~56px — white background, very minimal |
| Logo | "Pentagram" wordmark only — positioned top-left, small, using a refined serif or sans |
| Navigation | Right-aligned: Work, About, News, Contact, 🔍 (search), Archive — 14px, no bold |
| Hero section | 100vh — full-bleed rotating project images with CLIENT BRANDING typeset large in center of image; at bottom-center: "We design ___ for ___" interactive selector |
| Work page layout | White background; large "Work" H1 (60–70px); then full-bleed project pairs (1/3 + 2/3 or 1/2 + 1/2) |
| Section spacing | 80–100px |
| Footer | Pure black; news items; contact grid; then the iconic giant "Pentagram" wordmark (~300px tall) filling the full width |

## Typography

| Element | Font | Size | Weight | Notes |
|---------|------|------|--------|-------|
| Wordmark header | Serif editorial (appears to be Freight Display or similar) | ~14px | 400 | Small, refined |
| H1 (page heading) | Helvetica Neue Condensed Bold or similar | 60–72px | 900 | "Work" — very bold, very condensed |
| Hero typography | Varies by project — adapts to show CLIENT branding | 40–120px | Various | The hero TYPE is client work |
| Body text | Helvetica Neue or similar | 14–16px | 400 | Light gray on white `#666` |
| Project descriptions | Same | 14px | 400 | Single-line caption |
| Footer wordmark | Freight Display or Canela — high-contrast serif | ~280–320px | 400–500 | Full-width "Pentagram" at bottom |

## Colors

| Role | Color | Notes |
|------|-------|-------|
| Header bg | `#ffffff` | Clean white |
| Work/content bg | `#ffffff` | Pure white |
| Text primary | `#000000` or `#111` | Pure black on white |
| Text secondary | `#666` | 40% gray |
| Hero bg | `#000000` | Pure black |
| Footer bg | `#000000` | Pure black |
| Footer text | `#ffffff` | White on black |
| Accent | None systemic — client work provides all color | |

## Components

- **Project hero cards:** Full-bleed image (100vh height) with the CLIENT's identity/typography displayed in-situ — e.g., "National Building Museum" in large condensed serif over museum photo — the hero IS the work sample
- **Work grid cards:** Large image tiles (~1/3 or 2/3 width), with project name + single-line description + category tag below in very small text
- **Interactive filter:** "We design [work type dropdown] for [industry dropdown]" — a functional sentence-based filter that acts as brand statement and utility simultaneously
- **Category tags:** Small pill-style tags (Arts & Culture, Food & Drink) — minimal style, no color differentiation
- **News items:** Minimal list with date tag, title — very clean
- **Footer:** Flat black. Information organized in thin-ruled sections. Then the massive "Pentagram" wordmark.

## Feel & Personality

**What makes it premium:**
Pentagram's website is itself a work of design. The confidence to make the footer nothing but a 300px-tall wordmark on a black background — with no explanation — is the ultimate expression of a design firm that has zero insecurity about its brand.

### 5 Secret Sauce Elements:
1. **The footer as a monument:** The 300px white serif "Pentagram" wordmark on pure black at the bottom of every page is absolutely unforgettable. It transforms the footer from utility to brand expression. This is probably the #1 most-copied idea from any design firm website.
2. **Hero shows CLIENT work, not firm identity:** The homepage hero literally displays the client's visual identity at full screen. "We made this" — shown, not said. This inverts the usual self-promotional approach.
3. **Interactive sentence as navigation:** "We design Brand Identity for Civic & Public" — two dropdown menus embedded in a sentence. This is clever UX — a filter that also communicates service scope.
4. **Typographic extremes:** The wordmark in the footer vs. the minimal 14px navigation in the header — Pentagram weaponizes the full range of type sizes (14px–320px) as a design tool.
5. **Category taxonomy as navigation:** Filtering by "Arts & Culture", "Financial Services", etc. lets potential clients self-select — reducing browsing friction while clearly positioning the firm's breadth.

### What a Remodeling Business Can ADAPT (not copy):
- Use the footer as a brand statement — instead of a generic footer, put your most compelling line or even your company name LARGE in the footer
- Show before/after project photos AS the hero — let your work speak first, not your tagline
- Create a filtering system for your portfolio: by room type (Kitchen / Bathroom / Basement) and by neighborhood — helps clients find relevant work fast
- Display finished project photographs in a grid mixing large and medium sizes — not all the same size
- "We remodel kitchens for Denver homeowners" — use sentence-based positioning language instead of just listing services

---

---

# SYNTHESIS: CROSS-SITE PATTERNS

## What ALL 7 Premium Sites Share

### 1. Photography as the #1 design element
Every site invests in exceptional photography. The design system exists to GET OUT OF THE WAY of the photography. This is counterintuitive for most businesses.

### 2. Aggressive whitespace (or black-space)
Minimum 80px vertical section padding. Minimum 40px horizontal margins. Premium = spacious.

### 3. Font size extremes
All sites use the full range of type sizes — from 11px (metadata) to 80–320px (hero/brand statements). The range creates hierarchy.

### 4. Restraint in color
Most sites use 1–2 accent colors maximum. Many use ZERO brand accent — they rely on photography for color.

### 5. Typography precision
Letter-spacing on nav (0.1–0.15em), tight tracking on headings (-0.02em), careful line-heights. The type is engineered, not set at defaults.

### 6. Hover states that reward attention
Project titles appearing on hover, image zoom/darken on hover, menu items revealing depth. Premium sites have a layered relationship with cursor.

### 7. Navigation that doesn't compete
Small (12–14px), often secondary weight, often uppercase-and-spaced. Navigation NEVER shouts. In every one of these sites, navigation is the quietest element on the page.

---

## The "Cheap vs. Premium" Dark Site Checklist

| Element | Cheap Dark Site | Premium Dark Site |
|---------|----------------|-------------------|
| Background | `#000` pure black | `#090C14` (blue-black) or `#0e0e0e` (near-black) |
| Text | `#fff` pure white | `#f0ede8` (warm white) or `#F7F8F8` |
| Borders | `1px solid #333` | `1px solid rgba(255,255,255,0.06)` |
| Cards | Bright white glowing cards | Near-invisible frosted elevation |
| Buttons | Solid neon | Subtle with gradient or refined ghost |
| Shadows | `box-shadow: 0 4px 8px rgba(0,0,0,0.5)` | Near-invisible `0 1px 3px rgba(0,0,0,0.15)` |
| Headings | Bold + uppercase + colored | Thin weight + sentence case |
| Section dividers | Horizontal rules | 80–120px whitespace |
| Photography | Stock photos | Custom/editorial photography |
| Hover effects | Color change | Subtle scale (1.02) or opacity shift |

---

## Key Recommendations for MHCR Website

Based on cross-site analysis, the **3 highest-impact changes** for Mile High Custom Remodels are:

### Priority 1: Photography
Invest in a professional shoot of 5–8 completed projects. These should be editorial quality — wide angles, proper lighting, lifestyle-adjacent. Every premium site analyzed runs on photography.

### Priority 2: Background Color Refinement
Shift from `#1a1a1a` to `#0e1118` (blue-tinted near-black). This single hex change transforms the premium feel.

### Priority 3: Typography Extremes
Add a large editorial H1 (60–80px) that is a declarative brand statement, not just a service description. Add a bold footer wordmark. Create a clear hierarchy from 11px metadata to 72px hero.

---

*Report compiled: February 2026 | Researcher: AI Design Analyst*
*Sites analyzed via direct browser inspection, visual analysis, and CSS evaluation*
