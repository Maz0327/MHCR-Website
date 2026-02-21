# Modern Service Website Design Standards Research
## 2024–2026 Reference Guide for Home Remodeling Contractor Websites

> **Purpose:** This document provides specific, measurable design standards derived from award-winning service business websites, Nielsen Norman Group research, Smashing Magazine, Baymard Institute, Refactoring UI, and WCAG guidelines. Every recommendation includes a specific number or measurement. Use this as a checklist when auditing and improving the MHCR website.

---

## 1. TYPOGRAPHY SYSTEM

### Font Size Scale (Desktop)

| Element        | Size (rem) | Size (px equiv) | Notes                                      |
|----------------|-----------|-----------------|---------------------------------------------|
| Display / H1   | 3.5–5rem  | 56–80px         | Hero headline; use upper end sparingly      |
| H1 (interior)  | 2.5–3rem  | 40–48px         | Page titles, section heroes                 |
| H2             | 1.75–2rem | 28–32px         | Section headings                            |
| H3             | 1.25–1.5rem | 20–24px       | Sub-sections, card titles                   |
| H4             | 1.125rem  | 18px            | Minor headings, sidebar labels              |
| Body           | 1rem      | 16px            | Standard body copy (absolute minimum)       |
| Body Large     | 1.125rem  | 18px            | Lead paragraphs, introductory text          |
| Caption / Small | 0.875rem | 14px            | Labels, footnotes, legal text               |
| Micro          | 0.75rem   | 12px            | Tags, badges (never for body copy)          |

> **Rule:** Never use body text below 16px on desktop or 14px on mobile. The Smashing Magazine standard is 16px minimum, with 18px preferred for long-form reading.

### Fluid Type Scale (CSS clamp — Mobile 375px → Desktop 1280px)

```css
/* Display headline */
--text-display: clamp(2.5rem, 1.5rem + 4vw, 5rem);       /* 40px → 80px */

/* H1 */
--text-h1: clamp(2rem, 1.2rem + 3.2vw, 3.5rem);           /* 32px → 56px */

/* H2 */
--text-h2: clamp(1.5rem, 1rem + 2vw, 2.25rem);            /* 24px → 36px */

/* H3 */
--text-h3: clamp(1.125rem, 0.9rem + 0.9vw, 1.5rem);       /* 18px → 24px */

/* Body */
--text-body: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);     /* 16px → 18px */

/* Caption */
--text-sm: clamp(0.8125rem, 0.8rem + 0.05vw, 0.875rem);   /* 13px → 14px */
```

**Formula used:** `clamp(min, preferred, max)` where preferred = `(100vw − min-viewport) / (max-viewport − min-viewport) × (max-size − min-size) + min-size`

> **Accessibility note (Smashing Magazine 2023):** Use `rem` not `px` in clamp values to respect browser font-size user preferences. A user who sets their browser to 20px base will then see proportionally larger type.

### Line Height

| Element          | Line Height | Rationale                                      |
|------------------|-------------|------------------------------------------------|
| Display / H1     | 1.05–1.15   | Tight; large text needs less leading           |
| H2               | 1.2–1.3     | Slightly looser than display                   |
| H3               | 1.3–1.4     | Mid-range heading                              |
| Body paragraph   | 1.5–1.65    | WCAG 1.4.12 requires at least 1.5             |
| Captions / small | 1.4–1.5     | Slightly tighter than body                     |
| Navigation links | 1.0–1.2     | Single-line; no extra leading needed           |

> **Standard:** WCAG 1.4.12 (Text Spacing) mandates line-height of at least 1.5× the font size for body text. Best-in-class service sites use **1.6** for body paragraphs.

### Letter Spacing (Tracking)

| Element       | Value             | CSS                               |
|---------------|-------------------|-----------------------------------|
| Display / H1  | −0.03em to −0.04em | `letter-spacing: -0.03em`        |
| H2            | −0.02em to −0.03em | `letter-spacing: -0.02em`        |
| H3            | −0.01em to −0.02em | `letter-spacing: -0.01em`        |
| Body          | 0 to +0.01em      | `letter-spacing: 0`               |
| Uppercase labels / tags | +0.08em to +0.12em | `letter-spacing: 0.1em`  |
| Button text   | +0.02em to +0.04em | `letter-spacing: 0.03em`         |

> **Rationale:** Large type has naturally wider optical spacing between letters. Negative tracking for headings above 32px closes these gaps and creates a more premium, "set" feel. Source: Pimp My Type, Adam Wright Design.

### Maximum Reading Width (Characters Per Line)

- **Optimal body text:** 50–75 characters per line (CPL)
- **Absolute maximum:** 80 CPL (Baymard Institute)
- **Sweet spot:** 60–65 CPL
- **CSS implementation:** `max-width: 65ch` on body text containers
- **In pixels (at 16px):** approximately 520–600px wide
- **At 18px:** approximately 585–675px wide

> Source: Baymard Institute, UXPin, Wikipedia Line Length article. Setting `max-width: 65ch` on `p` and prose containers automatically adapts to the font size.

### Font Pairings (2024–2026 Trends for Service/Contractor Sites)

**Tier 1 — Premium Serif Display + Clean Sans (Most Authoritative)**
- Fraunces / Inter
- Playfair Display / DM Sans
- Cormorant Garamond / Jost
- Freight Display / Source Sans 3

**Tier 2 — Strong Sans Headline + Neutral Sans Body (Modern/Professional)**
- Neue Haas Grotesk / Inter
- Syne / Karla
- Space Grotesk / Lato
- Clash Display / Satoshi

**Tier 3 — Variable Weight Single Family (Increasingly Trendy)**
- Inter (variable) alone — weights 300–800
- Plus Jakarta Sans (variable) alone
- Cabinet Grotesk / Archivo

**For home remodeling / contractor context:**
- Best choice: a serif display (Playfair Display, Fraunces, or Libre Baskerville) for H1/H2 headlines paired with Inter or DM Sans for body. This communicates craftsmanship + modernity.
- Avoid: Script fonts, overly decorative typefaces, Comic Sans, Papyrus.

---

## 2. SPACING & LAYOUT SYSTEM

### Base Grid: 8pt / 8px System

The industry standard (Google Material Design, Apple HIG, Tailwind CSS default) is an **8px base grid**:
- `4px` — micro spacing (icon-to-label gap, small badge padding)
- `8px` — tight spacing (related inline elements)
- `12px` — compact spacing (dense UI, tags, chips)
- `16px` — standard spacing (paragraph margins, form element gaps)
- `24px` — comfortable spacing (card padding, section sub-elements)
- `32px` — medium spacing (between grouped elements)
- `48px` — large spacing (between sections within a block)
- `64px` — section separator
- `80px` — section padding on tablet
- `96px` — generous section padding on desktop
- `120px` — large section breathing room on wide desktop
- `160px` — maximum used on premium brand sites

> **Internal ≤ External rule (Cieden):** Spacing inside a component must always be less than spacing between components. E.g., 24px padding inside a card, 40px gap between cards.

### Section Padding (Top & Bottom)

| Breakpoint     | Section Padding | Example                              |
|----------------|-----------------|--------------------------------------|
| Mobile (< 768px)  | 48–64px      | `padding-block: 48px`                |
| Tablet (768–1024px) | 64–80px    | `padding-block: 80px`                |
| Desktop (1024–1280px) | 80–96px  | `padding-block: 96px`                |
| Wide (1280px+)   | 96–120px      | `padding-block: 120px`               |

**Fluid implementation:**
```css
.section {
  padding-block: clamp(48px, 5vw + 24px, 120px);
}
```

### Container Max-Widths & Gutters

| Purpose           | Max-Width | Side Gutter (px) | Side Gutter (%) |
|-------------------|-----------|------------------|-----------------|
| Full-width layout | 1440px    | 80px             | ~5.5%           |
| Standard content  | 1280px    | 80px             | ~6.25%          |
| Comfortable reading | 1200px  | 48–64px          | 4–5%            |
| Prose / article   | 760px     | 24px             | 3.15%           |
| Narrow content    | 640px     | 20px             | —               |

**At each breakpoint:**

| Viewport   | Container Max-Width | Side Gutter | Total Gutter |
|------------|---------------------|-------------|--------------|
| 375px      | 100%                | 16–20px     | 32–40px      |
| 576px      | 100%                | 24px        | 48px         |
| 768px      | 720px or 100%       | 32px        | 64px         |
| 1024px     | 960–1000px          | 48px        | 96px         |
| 1280px     | 1200px              | 80px        | 160px        |
| 1440px     | 1280px              | 80–160px    | 160–320px    |

**Source:** Figma community standard: 1280px frame with 80px margins = **1120px content width**. Or 1440px frame with 160px margins = same **1120px content width**.

### Card Padding

| Card Size  | Padding          | Use Case                          |
|------------|------------------|-----------------------------------|
| Small      | 16px / 12px 16px | Compact tiles, stats, badges      |
| Medium     | 24px             | Service cards, blog thumbnails    |
| Large      | 32px / 24px 32px | Feature cards, testimonials       |
| XL         | 40–48px          | Hero cards, pricing cards         |

### Golden Ratio in Layouts

- **1:1.618** — Use for splitting two-column layouts (e.g., hero text: ~61.8% / image: ~38.2%)
- **3:5 and 5:8** — Practical approximations for column proportions
- In a 12-column grid: **5 columns content + 7 columns** or **7 + 5**
- Sidebar ratio: main content **62%** / sidebar **38%** on desktop

---

## 3. NAVIGATION & HEADER

### Header Heights

| Breakpoint         | Height       | Notes                                      |
|--------------------|-------------|---------------------------------------------|
| Mobile (< 768px)   | 56–64px     | Never exceed 15% of viewport height        |
| Tablet (768–1024px) | 64–72px    | —                                           |
| Desktop (> 1024px) | 72–96px     | Sweet spot: 80px (Divimode)                |
| Desktop (premium brand) | 80–120px | With thick visual treatment              |

> **Rule:** On mobile, never use a sticky header taller than 56px. User satisfaction drops when more than 20–30% of screen is occupied by a sticky element (New Target research).

### Logo Sizing

| Context  | Height (px) | Max Width     | Notes                                  |
|----------|-------------|---------------|----------------------------------------|
| Desktop  | 36–48px     | 180–220px     | Most professional service sites       |
| Mobile   | 28–36px     | 120–160px     | Scale down from desktop                |
| Footer   | 40–60px     | 200–240px     | Can be slightly larger                 |

- **Aspect ratio:** Never distort. Always `object-fit: contain` or SVG.
- **Clear space:** Maintain at least 1× logo height as clear space on all sides.

### Navigation Link Spacing

| Context      | Gap Between Links | Notes                               |
|--------------|-------------------|--------------------------------------|
| Desktop nav  | 24–40px           | Tailwind: `gap-8` (32px) is standard |
| With icons   | 20–28px           | Tighter when icons present           |
| Mobile menu  | 0px gap; 16–20px padding per item | Touch-friendly              |

**Nav link font size:**
- Desktop: 14–16px, weight 500–600
- Mobile menu items: 18–24px, weight 500–600

### Sticky vs. Scroll-Away

- **Sticky header wins:** A sticky/fixed menu is **22% faster to navigate** and **100% of users preferred it** in desktop usability testing (Robert Marshall / UX research).
- **Recommendation for service sites:** Always use a sticky header on desktop. On mobile, use a sticky header but ensure it shrinks to 56px or hides after scrolling 50px past the fold.
- **Scroll-shrink pattern:** Header starts at 96px, shrinks to 64px after 80px of scroll. Implement with a CSS transition on `height` and `padding`.

**CSS pattern:**
```css
.header {
  height: 96px;
  transition: height 0.3s ease, box-shadow 0.3s ease;
}
.header.scrolled {
  height: 64px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.08);
}
```

### CTA in Header

- **One primary CTA button** in the top-right corner of the header — always visible
- Button size: 40–44px height on desktop, full-width on mobile menu
- Phone number should be visible in header on desktop for service businesses (clickable tel: link)
- Phone number font size: 16–18px, font-weight: 600–700
- CTA button position: rightmost element after navigation links

### Mobile Hamburger Menu

- **Touch target minimum:** 44×44px (Apple HIG) / 48×48px (Google Material)
- Three-line hamburger is universally recognized; consider X icon for close state
- Menu items: minimum 48px tall touch targets, 18–20px font
- Transition: slide-in from right (250–300ms) or fade+scale (200ms)
- Always include CTA and phone number in mobile menu

---

## 4. HERO SECTIONS

### Hero Heights

| Device   | Height          | CSS                                  |
|----------|-----------------|---------------------------------------|
| Desktop  | 75–100vh        | `min-height: 80vh` (most common)     |
| Tablet   | 65–80vh         | `min-height: 70vh`                   |
| Mobile   | 60–75vh         | `min-height: 60vh` or `auto`         |

> **Warning:** Never use `height: 100vh` on mobile without `svh` or `dvh` fallback — iOS Safari includes the URL bar in `vh`, causing content to be cut off. Use `min-height: 100svh` (small viewport height) on modern browsers, with `100vh` as fallback.

```css
.hero {
  min-height: 100vh;        /* fallback */
  min-height: 100svh;       /* modern — excludes browser chrome */
}
```

### Text Alignment

| Alignment     | When to Use                                  | Performance            |
|---------------|----------------------------------------------|------------------------|
| Left-aligned  | When text is next to an image (split layout) | Higher scannability    |
| Centered      | Full-bleed background image/video heroes     | More dramatic, brand-focused |
| Left on left-panel | Split hero (text left / image right)   | **Best for service sites** — creates natural flow to content below |

> **Recommendation for contractor sites:** Left-aligned text on a split or overlay hero. Users scan in F-pattern (left to right, top to bottom). Left-aligned text aligns with natural reading direction and gets more engagement.

### Headline Length

- **Optimal hero headline:** 4–12 words
- **Character limit:** 30–60 characters
- **Rule:** If the headline wraps more than 3 lines on mobile, it's too long
- **Subheadline/subtext:** 1–2 sentences, 12–25 words, 80–150 characters

### CTA Presentation in Hero

- **Primary CTA:** Largest button, highest contrast, action-oriented verb ("Get Your Free Quote", "See Our Work", "Call Now")
- **Secondary CTA:** Ghost/outline button or text link, 8–16px to the right of or below primary
- **Gap between primary and secondary:** 12–16px (same row) or 8–12px (stacked on mobile)
- **Above the fold:** Both CTAs must be fully visible without any scrolling on any device
- CTA uplift data: repositioning CTA from mid-page to above the fold = **+28% conversion** (AlfDesignGroup case study)

### Background Treatment

| Treatment              | Best For                           | Implementation                            |
|------------------------|------------------------------------|-------------------------------------------|
| Full-bleed photography | Showcasing finished work           | `background-size: cover`, 40–60% opacity overlay |
| Color overlay on photo | Any service site                   | `linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.4))` over image |
| Split (image + color)  | Modern/premium feel                | CSS Grid 60/40 split or Flexbox           |
| Gradient background    | Tech-forward; avoid for trades     | Use sparingly                             |
| Video background       | Premium brands                     | Autoplay, muted, loop; always have poster fallback; max 3–5 seconds |

**Image overlay opacity:** 35–55% black overlay for text legibility. Test: white text on the overlay must achieve ≥ 4.5:1 contrast ratio against the darkened image.

---

## 5. BUTTONS & CTAs

### Button Heights

| Size     | Height   | Use Case                                    |
|----------|---------|----------------------------------------------|
| Small    | 32–36px | Compact UI, table actions, inline forms      |
| Medium   | 40–44px | Default buttons, secondary actions          |
| Large    | 48–52px | Primary CTAs, hero buttons                   |
| XL       | 56–64px | Landing page hero CTAs, full-width mobile    |

> **WCAG minimum:** 44×44px (Apple), 48×48px (Google). Use **48px** as your default primary button height. Never go below 44px for any interactive element.

### Button Padding

| Height  | Horizontal Padding | Vertical Padding | Padding shorthand  |
|---------|-------------------|------------------|--------------------|
| 32px    | 16px              | 6px              | `6px 16px`         |
| 40px    | 20px              | 10px             | `10px 20px`        |
| 48px    | 24px              | 14px             | `14px 24px`        |
| 56px    | 32px              | 18px             | `18px 32px`        |

> **Ratio:** Horizontal padding should be approximately **1.5–2× the vertical padding** for a visually balanced button.

### Border Radius Trends

| Style          | Value      | Feel                              |
|----------------|-----------|----------------------------------|
| Sharp           | 0px        | Corporate, financial, editorial  |
| Subtle          | 4px        | Professional, clean              |
| Rounded         | 6–8px      | Modern standard (**most common**)|
| More rounded    | 12px       | Friendly, approachable           |
| Pill            | 9999px     | Trendy, premium SaaS             |

> **For contractor/remodeling sites:** 6–8px border radius reads as professional and modern without being whimsical. Avoid sharp corners (feels outdated) and full pills (feels tech-startup, not trades).

### What Makes a Button Feel Premium

1. **Subtle box-shadow on rest:** `box-shadow: 0 1px 3px rgba(0,0,0,0.15), 0 1px 2px rgba(0,0,0,0.1)`
2. **Smooth hover transition:** 150–200ms, ease-out
3. **Slight scale or lift on hover:** `transform: translateY(-2px)` + deeper shadow
4. **Refined typography:** font-weight 600, letter-spacing 0.02–0.04em, no all-caps unless brand requires
5. **Consistent padding:** Never let the label feel cramped or floating
6. **Color with depth:** Use a background color that has a subtle gradient or adjusts lightness on hover, rather than a flat 2px-old-style look

### Hover States

```css
.btn-primary {
  background: #1a5276;
  color: white;
  transform: translateY(0);
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  transition: transform 150ms ease-out, box-shadow 150ms ease-out, background 150ms ease-out;
}

.btn-primary:hover {
  background: #154360;            /* 10% darker */
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.btn-primary:active {
  transform: translateY(0);
  transition-duration: 80ms;
}
```

> **Cheap feel indicators:** Using `transition: all` (expensive), transitions >400ms (sluggish), color flash without easing, no visual feedback on :active state.

---

## 6. CARDS & COMPONENTS

### Card Padding

| Card Purpose         | Padding (uniform) | Padding (asymmetric)        |
|----------------------|------------------|-----------------------------|
| Blog/news thumbnail  | 20–24px          | —                           |
| Service feature card | 24–32px          | 24px top/bottom, 28px sides |
| Testimonial card     | 28–32px          | —                           |
| Pricing card         | 32–40px          | —                           |
| Stat / number card   | 24px             | —                           |

### Border Radius for Cards

| Style      | Radius   | Use Case                                 |
|------------|---------|------------------------------------------|
| Subtle     | 8px      | Dense grids, small cards                 |
| Standard   | 12px     | Most service site cards (**recommended**)|
| Generous   | 16–20px  | Larger cards, hero-adjacent cards        |
| Rounded    | 24px     | Testimonials, quote cards                |

### Shadow Depth (Elevation System)

Use 3–4 elevation levels, not one flat shadow for everything:

```css
/* Level 0 — No shadow (flat, on white surface) */
--shadow-0: none;

/* Level 1 — Subtle lift (resting state of interactive cards) */
--shadow-1: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);

/* Level 2 — Hover state */
--shadow-2: 0 4px 16px rgba(0,0,0,0.10), 0 2px 4px rgba(0,0,0,0.06);

/* Level 3 — Modals, dropdowns */
--shadow-3: 0 12px 40px rgba(0,0,0,0.15), 0 4px 8px rgba(0,0,0,0.08);

/* Level 4 — Overlays, drawers */
--shadow-4: 0 24px 80px rgba(0,0,0,0.25);
```

> **Source:** Refactoring UI principle — use ambient (large, blurry, low-opacity) + direct (small, tight, moderate opacity) shadows together for realism.

### Card Hover Effects

| Effect                 | CSS                                           | Duration  |
|------------------------|-----------------------------------------------|-----------|
| Lift (most common)     | `transform: translateY(-4px)` + shadow-2      | 200ms     |
| Scale                  | `transform: scale(1.02)`                      | 200ms     |
| Border reveal          | `border-color: var(--accent)`                 | 150ms     |
| Background shift       | Background lightens or darkens by ~3%          | 200ms     |
| Image zoom (inside)    | `transform: scale(1.05)` on inner img         | 400ms     |

> **Recommendation:** Combine lift + shadow elevation change for service cards. Image zoom inside the card frame for project/portfolio cards.

---

## 7. COLORS & CONTRAST

### WCAG Contrast Standards

| Level | Text Type           | Minimum Ratio | Notes                              |
|-------|---------------------|---------------|------------------------------------|
| AA    | Normal text (< 18px bold, < 24px) | **4.5:1** | Legal minimum for most sites |
| AA    | Large text (≥ 18px, or ≥ 14px bold) | **3:1** | —                         |
| AA    | UI components, graphical objects | **3:1** | Borders, icons, input outlines |
| AAA   | Normal text         | **7:1**       | Enhanced; target for body text     |
| AAA   | Large text          | **4.5:1**     | Enhanced large text                |

**Target for service sites: AA compliance at minimum, AAA for primary body text.**

Example passing combinations:
- `#1A1A1A` on `#FFFFFF` → 16.1:1 (AAA ✓)
- `#333333` on `#F0F0F0` → 11.5:1 (AAA ✓)
- `#E5E5E5` on `#1A1A1A` → 12.8:1 (AAA ✓) — dark mode
- `#B3B3B3` on `#1A1A1A` → 7.7:1 (AAA ✓) — dark mode secondary

**Check your combinations:** https://webaim.org/resources/contrastchecker/

### Dark Mode Background Colors

| Purpose           | Recommended Value | Notes                                |
|-------------------|-------------------|---------------------------------------|
| Page background   | `#111111` or `#0f0f0f` | NOT pure `#000000` — too harsh  |
| Surface (cards)   | `#1a1a1a` or `#161616` | 2–3% lighter than background    |
| Elevated surface  | `#222222` or `#202020` | For dropdowns, modals             |
| Border / divider  | `#2a2a2a` or `#333333` | Subtle; don't use pure white      |
| Primary text      | `#f0f0f0` or `#e5e5e5` | NOT pure `#FFFFFF` — too harsh   |
| Secondary text    | `#999999` or `#a0a0a0` | Check contrast ≥ 4.5:1           |

> **Source:** TestParty.ai, AllAccessible.org. Pure black (`#000000`) and pure white (`#FFFFFF`) together cause halation (visual vibration) and are avoided by every premium dark-mode implementation.

### Accent Color Usage: 60-30-10 Rule

| Role     | Proportion | Typical Colors                          |
|----------|-----------|------------------------------------------|
| Dominant / Neutral | **60%** | White, off-white, light gray, cream  |
| Secondary         | **30%** | Muted brand color, dark navy, charcoal |
| Accent / Action   | **10%** | Bright brand color; all CTAs, links, highlights |

> **Contractor sites:** Common premium palette — 60% warm white/cream backgrounds, 30% deep navy or charcoal (text, headers, footer), 10% a single accent (amber, forest green, rust, or brand blue) used exclusively for CTAs and key callouts.

### Surface Elevation (Light Mode)

Use 3–4 surface tiers to create visual depth:
- **Tier 0** (base): `#FFFFFF`
- **Tier 1** (slight elevation): `#F8F8F8` or `#FAFAFA`
- **Tier 2** (cards, panels): `#F3F4F6` or `#F0F2F5`
- **Tier 3** (elevated cards, modals): `#FFFFFF` with shadow-2 or shadow-3

---

## 8. IMAGERY & VISUAL HIERARCHY

### Image Aspect Ratios

| Context              | Ratio   | Pixels Example      | Notes                         |
|----------------------|---------|---------------------|-------------------------------|
| Hero (full-bleed)    | 16:9    | 1920×1080           | Standard desktop hero         |
| Hero (crop/portrait) | 4:3     | 1600×1200           | Tighter, more dramatic        |
| Card thumbnail       | 3:2     | 600×400             | Most versatile for portfolios |
| Square card          | 1:1     | 600×600             | For uniform grid layouts      |
| Blog header          | 2:1     | 1200×600            | Wide, shallow; reads as banner|
| Team photo           | 1:1 or 3:4 | 400×400 or 400×533 | Portrait framing             |
| Service icon         | 1:1     | 80×80 or 100×100    | SVG preferred                 |

### Hero Image Treatment

**Full-bleed overlay (most common for service sites):**
```css
.hero {
  background-image:
    linear-gradient(
      135deg,
      rgba(0, 0, 0, 0.65) 0%,
      rgba(0, 0, 0, 0.35) 100%
    ),
    url('hero.jpg');
  background-size: cover;
  background-position: center;
}
```

**Split layout (text left / image right) — premium approach:**
```css
.hero-split {
  display: grid;
  grid-template-columns: 1fr 1fr;   /* or 55fr / 45fr */
}
/* Image fills right half, object-fit: cover */
```

> **Split heroes** convert well for contractor/service sites because: (1) the headline isn't fighting against a complex background, (2) users see the work/craftsmanship immediately, (3) clear visual separation reduces cognitive load.

### Missing Image Handling

- Always provide a `loading="lazy"` attribute on below-the-fold images
- Provide `width` and `height` attributes to prevent layout shift (Core Web Vitals)
- For cards: use an `aspect-ratio` CSS container so layout doesn't jump
- Default placeholder: a subtle gradient in brand colors (e.g., `linear-gradient(135deg, #f0f0f0, #e0e0e0)`)
- Always provide meaningful `alt` text; empty `alt=""` only for purely decorative images

---

## 9. FOOTER DESIGN

### Required Footer Content (Service Business)

A premium footer for a home remodeling contractor must include:

**Column 1 — Brand**
- Logo (40–60px height)
- 1–2 sentence brand description / tagline
- Social media icons (LinkedIn, Facebook, Instagram, Houzz)
- License number (required by law in many states)

**Column 2 — Services**
- 5–8 primary services as navigation links
- Keep copy concise (e.g., "Kitchen Remodeling", "Bathroom Renovation")

**Column 3 — Company**
- About Us
- Our Process or How It Works
- Portfolio / Gallery
- Blog / Resources
- Careers (if applicable)

**Column 4 — Contact / CTA**
- Phone number (large, 18–20px, bold, clickable `tel:` link)
- Email address (clickable `mailto:` link)
- Physical address (linked to Google Maps)
- Service area list or link to service areas page
- "Get a Free Quote" CTA button

**Bottom bar (sub-footer):**
- Copyright © 2025 [Company Name]
- Privacy Policy link
- Terms of Service link
- Sitemap link
- Designed by / Developed by (optional)
- Any certifications or association badges (BBB, NARI, NAHB, etc.)

### Footer Layout Patterns

| Pattern       | Columns | Description                                  |
|---------------|---------|----------------------------------------------|
| 4-column grid | 4       | Most common for service businesses           |
| 3-column + wide brand | 3 | Brand takes ~35%, other two split 65%  |
| 2-column + CTA band | 2 + full-width bottom | Full-width CTA section above footer |

**Footer background:** Dark (navy, charcoal, or black) with light text creates clear separation from page body. Use your 30% secondary brand color here.

**Footer padding:** Top: 64–96px, Bottom (above sub-footer): 48–64px, Sub-footer padding: 20–24px top/bottom.

---

## 10. MICRO-INTERACTIONS & ANIMATION

### Standard Premium Animations

| Animation             | Duration | Timing Function                   | When to Use                  |
|-----------------------|----------|-----------------------------------|-------------------------------|
| Button hover          | 150–200ms | `ease-out`                       | All interactive buttons       |
| Card hover lift       | 200ms    | `ease-out`                        | Project/service cards         |
| Navigation link       | 150ms    | `ease`                            | Underline, color change       |
| Dropdown open         | 200ms    | `cubic-bezier(0.16, 1, 0.3, 1)`  | Navigation menus              |
| Modal open            | 250–300ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Dialogs, overlays             |
| Page fade-in          | 300ms    | `ease-out`                        | Page transitions              |
| Scroll reveal (fade up)| 400–600ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Section reveals on scroll    |
| Image zoom            | 400ms    | `ease-out`                        | Gallery hover, card image     |
| Counter / number      | 1000–2000ms | `ease-out`                     | Stat counters on scroll       |

### Transition Timing Functions (Named)

```css
:root {
  --ease-smooth:      cubic-bezier(0.4, 0, 0.2, 1);     /* Material standard */
  --ease-spring:      cubic-bezier(0.16, 1, 0.3, 1);    /* Springy, premium */
  --ease-decelerate:  cubic-bezier(0, 0, 0.2, 1);       /* Enters fast, slows */
  --ease-accelerate:  cubic-bezier(0.4, 0, 1, 1);       /* Starts slow, exits fast */
  --ease-out-expo:    cubic-bezier(0.19, 1, 0.22, 1);   /* Dramatic deceleration */
}
```

### Scroll-Triggered Animation Best Practices

1. **Fade + translate up:** The most universal and premium scroll reveal. `opacity: 0 → 1` combined with `translateY(24px → 0)`. Duration: 500ms with `ease-out`.
2. **Stagger delay for lists/grids:** Each card reveals 80–100ms after the previous one. Max 5 staggered items before the delay becomes noticeable.
3. **Threshold:** Trigger at 15–20% visibility (IntersectionObserver threshold: 0.15). Don't fire until the element is meaningfully on-screen.
4. **Never animate on mobile unless duration is ≤ 300ms** — mobile CPUs and attention spans are shorter.
5. **Always implement `prefers-reduced-motion`:**

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Premium vs. Cheap Animation Signals

| Premium                                    | Cheap                                   |
|--------------------------------------------|------------------------------------------|
| `ease-out` or spring curve                 | `linear` (robotic feel)                 |
| 150–300ms for interactions                 | >500ms for simple hover                 |
| Single property transition (transform)     | `transition: all` (jerky compositing)  |
| Subtle (4–8px movement)                    | Dramatic bouncing, spinning             |
| Consistent across the site                 | Different durations per section         |
| Always respects `prefers-reduced-motion`   | Ignores accessibility preference        |

> **GPU-only transitions:** Only animate `transform` and `opacity` for 60fps performance. Never animate `width`, `height`, `top`, `left`, `margin`, or `padding` — these cause layout recalculation (reflow) and janky animations.

---

## 11. CONVERSION OPTIMIZATION

### CTA Placement Throughout a Page

**Minimum CTA placements on a homepage:**

1. **Header** — Always visible; primary action button (top-right)
2. **Hero section** — Primary + secondary CTA, above the fold
3. **After services overview** — "Get a Quote for [Service]" or "View All Services"
4. **After social proof / testimonials** — "Join Our Happy Customers" + CTA
5. **Mid-page floating bar** (optional) — Appears after 50% scroll, less aggressive than sticky
6. **Before footer** — Full-width CTA band: "Ready to Start Your Project?" + button + phone
7. **Footer** — Phone number + "Get a Free Quote" button

> **Source:** TiltStack (2025): *"Repeat your primary CTA in at least three key places: header, mid-page, and footer."*

### Trust Signals That Convert for Contractors

**Tier 1 (highest impact):**
- Star ratings + review count from Google (e.g., "★★★★★ 4.9 / 5 (147 Reviews)")
- Before/after project photos (real work evidence)
- Named testimonials with photo + first name + city
- Video testimonials

**Tier 2 (strong support):**
- Years in business (e.g., "Serving Families Since 2008")
- Number of projects completed (e.g., "1,200+ Homes Transformed")
- License and insurance badges (state contractor license number)
- BBB Accreditation badge
- NARI / NAHB / HBA membership badge

**Tier 3 (credibility reinforcement):**
- Manufacturer certifications (GAF Master Elite, Pella Certified, etc.)
- "Featured in" press logos
- Warranty / workmanship guarantee badge
- Money-back / satisfaction guarantee

### Phone Number Visibility

- **Must appear in the header** on every page
- Must be a clickable `tel:` link (critical for mobile users)
- Font size: 16–20px, weight: 600–700
- Color: High contrast; never lighter than 3:1 against background
- On mobile: consider floating "Call Now" button in bottom-right corner
- Repeat in footer
- Include on every service page above the fold

### Form Best Practices

| Principle                       | Specific Standard                                    |
|---------------------------------|------------------------------------------------------|
| Minimum fields                  | 3 fields = 25% guaranteed conversion rate (Quicksprout) |
| Optimal field count             | 3–5 fields; 6+ fields reduces conversions significantly |
| Required fields for service sites | Name, Phone or Email, Message / Project Description  |
| Label placement                 | Above the field (not inside; placeholder is not a label) |
| Field height                    | 44–52px (min. 44px for accessibility)                |
| Submit button                   | Full-width on mobile; descriptive text ("Get My Free Quote", not "Submit") |
| Success state                   | Clear confirmation message; no page reload            |
| Error state                     | Inline validation, red border + icon, specific message |
| Privacy reassurance             | "We never sell your information." under the submit button |

---

## 12. MOBILE-FIRST DESIGN

### Standard Breakpoints (2025)

```css
/* Mobile-first base styles (320px–575px) */
/* No media query needed — base styles apply here */

/* Large mobile / phablets (≥ 480px) */
@media (min-width: 480px) { }

/* Tablets portrait (≥ 768px) */
@media (min-width: 768px) { }

/* Tablets landscape / small desktop (≥ 1024px) */
@media (min-width: 1024px) { }

/* Standard desktop (≥ 1280px) */
@media (min-width: 1280px) { }

/* Wide desktop (≥ 1440px) */
@media (min-width: 1440px) { }
```

**Market share context (2025):**
- 375×812 (iPhone) — ~16.79% North America
- 390×844 (iPhone 14) — ~13.72%
- 360–430px range covers the vast majority of mobile devices
- Design primary for 390px width; test at 375px and 414px

### What Changes Between Mobile and Desktop

| Element              | Mobile                              | Desktop                             |
|----------------------|-------------------------------------|-------------------------------------|
| Font size (body)     | 16px                               | 16–18px                             |
| H1 size              | 32–40px                            | 48–80px                             |
| Section padding      | 48–64px                            | 80–120px                            |
| Container gutter     | 16–20px each side                  | 80px each side                      |
| Navigation           | Hamburger menu                      | Horizontal nav with all links       |
| Grid columns         | 1 col (most content) / 2 col (cards)| 3–4 col grids                       |
| Button size          | Full-width or large (56px)          | Inline, auto-width (48px)           |
| Hero layout          | Stacked (text above image)          | Split or full-bleed                 |
| Card stack           | Single column                       | 2–3 column grid                     |
| Sidebar              | Hidden or collapsed below content   | Visible at 30–38% width             |
| Image sizes          | Portrait or square friendly         | Landscape (16:9, 3:2)               |
| Hover states         | Not applicable (touch)              | Full hover animations               |
| Font weight          | +100 heavier (bolder) than desktop  | Normal weight reads well at size    |

### Touch Target Minimum Sizes

| Standard          | Minimum Size    | Recommended  |
|-------------------|-----------------|--------------|
| WCAG 2.1 (AA)     | 44×44px         | 44×44px      |
| Apple HIG         | 44×44px         | 44×44px      |
| Google Material   | 48×48px         | 48×48px      |
| WCAG 2.5.8 (2.2)  | 24×24px         | 44×44px (guidance) |

> **Practical rule:** Every tappable element — buttons, links, hamburger icon, phone number — must have a minimum **44×44px clickable area** even if the visual element is smaller. Use `padding` to increase the touch target without changing visual size.

```css
/* Make a small icon link have 44px touch target */
.icon-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
}
```

### Mobile-Specific Performance Targets

- **Largest Contentful Paint (LCP):** < 2.5 seconds (Good), < 4.0s (Needs Improvement)
- **Cumulative Layout Shift (CLS):** < 0.1 (Good)
- **First Input Delay (FID) / INP:** < 200ms (Good)
- **Total Blocking Time (TBT):** < 200ms
- **Hero image:** Serve WebP/AVIF, max 150–200KB for mobile (800px wide max)
- **Body images:** Lazy load below the fold; `loading="lazy"` attribute
- **Font loading:** Use `font-display: swap` on all custom fonts

---

## QUICK-REFERENCE SUMMARY CARD

```
TYPOGRAPHY
├── Body: 16–18px / line-height 1.6 / max-width 65ch
├── H1 (hero): clamp(32px, 4vw + 16px, 64px)
├── H2: clamp(24px, 2vw + 12px, 36px)
├── Letter-spacing: headings −0.02em / caps +0.08em
└── Pairing: Serif display (Playfair/Fraunces) + Sans body (Inter/DM Sans)

SPACING
├── Base: 8px grid (all values multiples of 8 or 4)
├── Section padding: clamp(48px, 5vw + 24px, 120px)
├── Container max: 1280px / gutters 80px each side
├── Card padding: 24–32px / Gap between cards: 24–32px
└── Internal ≤ External rule: inside spacing < outside spacing

NAVIGATION
├── Header height: 80px desktop / 56–64px mobile
├── Logo: 36–48px tall / max 200px wide
├── Sticky header: YES — 22% faster navigation
└── CTA in header: always top-right, 44–48px height

HERO
├── Height: min-height: 80vh (use min-height: 100svh for full)
├── Headline: 4–12 words / 30–60 characters
├── Both CTAs above the fold / primary left-aligned
└── Overlay: rgba(0,0,0,0.4–0.55) on photo backgrounds

BUTTONS
├── Primary height: 48px / padding: 14px 24px
├── Border radius: 6–8px
├── Hover: translateY(-2px) + deeper shadow / 150–200ms
└── Min touch: 44×44px (WCAG) / 48×48px (Material)

COLORS
├── Contrast: ≥ 4.5:1 (AA) / ≥ 7:1 (AAA) for body text
├── 60-30-10: 60% neutral / 30% secondary / 10% accent
├── Dark mode bg: #111111 or #0f0f0f (NOT pure black)
└── Surface elevation: 3–4 tiers (white / F8F8F8 / F0F2F5)

CARDS
├── Padding: 24–32px
├── Border radius: 12px
├── Shadow: Level 1 at rest / Level 2 on hover
└── Hover: translateY(-4px) + shadow elevation / 200ms

CONVERSION
├── CTAs: Header + Hero + After social proof + Before footer + Footer
├── Trust: Google stars + photo testimonials + license badges + years in biz
├── Phone: header + footer + all service pages / clickable tel:
└── Form: 3–5 fields / descriptive submit / privacy note

MOBILE
├── Breakpoints: 480 / 768 / 1024 / 1280 / 1440px
├── Touch targets: min 44×44px on all interactive elements
├── Hero: stacked layout / min-height: 60vh
└── Font: never below 16px body / never below 14px caption
```

---

## SOURCES & REFERENCES

- **Smashing Magazine** — Fluid Typography with CSS Clamp (2022, 2023): https://www.smashingmagazine.com/2022/01/modern-fluid-typography-css-clamp/
- **Baymard Institute** — Line Length Readability: https://baymard.com/blog/line-length-readability
- **Nielsen Norman Group** — Sticky Headers: https://www.nngroup.com/articles/sticky-headers/
- **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **WCAG 2.1 — Text Spacing (1.4.12)**: https://www.w3.org/WAI/WCAG21/Understanding/text-spacing.html
- **Google Material Design 3** — Spacing & Typography
- **Apple Human Interface Guidelines** — Touch targets, navigation
- **Refactoring UI** (Adam Wathan & Steve Schoger) — Shadows, spacing, color systems
- **BrowserStack** — Responsive Breakpoints 2025: https://www.browserstack.com/guide/responsive-design-breakpoints
- **TestParty.ai** — Dark Mode Color Contrast: https://testparty.ai/blog/color-contrast-requirements
- **TiltStack** — Web Design for Service Businesses 2025: https://www.tiltstack.com/blog/web-design-for-service-businesses-2025/
- **Cieden Design Book** — Spacing Best Practices: https://cieden.com/book/sub-atomic/spacing/
- **8pt Grid (Prototypr)**: https://blog.prototypr.io/the-8pt-grid-consistent-spacing-in-ui-design-with-sketch-577e4f0fd520
- **Divimode** — Header Sizing Guide: https://divimode.com/header-sizes-for-websites/
- **AlfDesignGroup** — Hero CTA Case Study (+28% conversion): https://www.alfdesigngroup.com/post/saas-hero-section-best-practices
- **WPForms Research** — Form Conversion: https://wpforms.com/research-based-tips-to-improve-contact-form-conversions/
- **Robert Marshall** — Sticky Navigation Study (22% faster): https://robertmarshall.dev/blog/to-sticky-or-not-to-sticky/

---

*Document generated: February 2026 | For MHCR Website Audit & Redesign*
