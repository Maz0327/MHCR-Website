# MHCR Placeholder Image Guide

All placeholder images are in `/images/placeholders/`. When real images are ready, replace each placeholder using this guide.

---

## HOW TO REPLACE A PLACEHOLDER

1. Drop your final image into the specified location in `/images/`
2. Update the `src` or CSS `url()` reference to point to your new file
3. Delete the placeholder from `/images/placeholders/`
4. Check off the item in this list

---

## PLACEHOLDER CHECKLIST

### 🔴 TIER 1 — Highest Priority (Visible on Homepage Above the Fold)

| # | Placeholder File | Replace With | Location in Code | Final Dimensions | Notes |
|---|-----------------|--------------|-----------------|-----------------|-------|
| 1 | `placeholders/hero-bg.svg` | `images/hero-bg.jpg` or `hero-bg.webp` | `index.html` hero section `<img>` tag + CSS `.hero-background` | 1920×1080px min | **Single most important image.** Use best completed kitchen or whole-room shot. Dark-toned. Dramatic lighting. |
| 2 | `placeholders/why-us-photo.svg` | `images/why-us-photo.jpg` | `index.html` Why Choose Us section | 600×500px | Before/after split image or team at work. High quality. |

---

### 🟠 TIER 2 — High Priority (Gallery + Testimonials)

| # | Placeholder File | Replace With | Location in Code | Final Dimensions | Notes |
|---|-----------------|--------------|-----------------|-----------------|-------|
| 3 | `placeholders/avatar-placeholder.svg` | `images/testimonials/sarah-m.jpg` | `index.html` first testimonial | 56×56px (round) | Real photo of customer OR tasteful initials monogram. |
| 4 | `placeholders/avatar-placeholder.svg` | `images/testimonials/david-t.jpg` | `index.html` second testimonial | 56×56px (round) | Same as above. |
| 5 | `placeholders/avatar-placeholder.svg` | `images/testimonials/mike-r.jpg` | `index.html` third testimonial | 56×56px (round) | Same as above. |
| 6 | `placeholders/project-kitchen-1.svg` | `images/gallery/kitchen-1.jpg` | `gallery.html` | 800×600px | Best kitchen project. Ideally with island, custom cabinets. |
| 7 | `placeholders/project-bathroom-1.svg` | `images/gallery/bathroom-1.jpg` | `gallery.html` | 800×600px | Best bathroom project. Walk-in shower or freestanding tub. |
| 8 | `placeholders/project-basement-1.svg` | `images/gallery/basement-1.jpg` | `gallery.html` | 800×600px | Best basement. Entertainment room or home office. |

---

### 🟡 TIER 3 — Important (Service Pages + About)

| # | Placeholder File | Replace With | Location in Code | Final Dimensions | Notes |
|---|-----------------|--------------|-----------------|-----------------|-------|
| 9 | `placeholders/project-kitchen-1.svg` | `images/gallery/kitchen-2.jpg` | `gallery.html` | 800×600px | Second kitchen project angle or different style. |
| 10 | `placeholders/project-bathroom-1.svg` | `images/gallery/bathroom-2.jpg` | `gallery.html` | 800×600px | Second bathroom — different style than first. |
| 11 | `placeholders/project-basement-1.svg` | `images/gallery/living-room-1.jpg` | `gallery.html` | 800×600px | Living room remodel. |
| 12 | *(service page hero bg)* | `images/services/kitchen-hero.jpg` | `services/kitchen-remodeling.html` | 1920×600px | Header/banner for kitchen service page. |
| 13 | *(service page hero bg)* | `images/services/bathroom-hero.jpg` | `services/bathroom-remodeling.html` | 1920×600px | Header/banner for bathroom service page. |
| 14 | *(service page hero bg)* | `images/services/basement-hero.jpg` | `services/basement-finishing.html` | 1920×600px | Header/banner for basement service page. |
| 15 | *(about page)* | `images/team/team-photo.jpg` | `about.html` | 800×600px | Team photo — professional, on a job site or showroom. |
| 16 | *(about page)* | `images/team/owner-headshot.jpg` | `about.html` | 400×500px | Owner headshot — professional, friendly. |

---

## PHOTOGRAPHY GUIDELINES

### What Makes a Great Remodeling Photo

**For Hero (1920×1080):**
- Shot in good natural light or professional staging
- Dark/moody atmosphere or dramatic lighting (works with our dark overlay)
- Show craftsmanship detail — clean lines, quality finishes
- Horizontal/landscape orientation required
- Avoid empty rooms — staging with minimal props preferred
- Best subjects: custom kitchen, luxury master bath, finished basement lounge

**For Gallery (800×600):**
- Clean, straight-on or slight angle shots
- Show the "wow" moment of the remodel
- Before/after pairs are powerful if available
- Consistent color grading across all gallery images

**For Testimonial Avatars (56×56 round):**
- Professional headshots only
- If customer permission not granted, use initials-based monogram instead
- Consistent style across all three

---

## FILE FORMAT RECOMMENDATIONS

| Use Case | Recommended Format | Why |
|----------|-------------------|-----|
| Hero background | `.webp` (with `.jpg` fallback) | Smaller file size, modern browsers |
| Gallery images | `.jpg` at 80% quality | Good balance of size/quality |
| Team photos | `.jpg` at 85% quality | Faces need higher quality |
| Small avatars | `.jpg` or `.webp` | Tiny file, format doesn't matter much |

---

## CSS BACKGROUND IMAGES TO UPDATE

When hero photography is ready, update `css/style.css`:

```css
/* Find this section and update the src: */
.hero-background img {
    /* Update src attribute in HTML: images/hero-bg.jpg */
}
```

The hero uses an `<img>` tag inside `.hero-background` div for better LCP performance.

---

## ICON REPLACEMENTS

The site uses inline SVG icons throughout. These do NOT need image files. However, if you want to replace any icon with a custom branded icon:

| Icon | Location | Current | Replacement Action |
|------|----------|---------|-------------------|
| Phone icon | Top bar, header, footer | Inline SVG | Update SVG path or swap for custom icon SVG |
| Shield (Licensed) | Trust bar | Inline SVG | Optional: replace with MHCR branded credential badge |
| Star (5-Star) | Trust bar | Inline SVG | Optional: replace with actual review platform logo |
| Logo `.png` | All pages — `<img src="/images/logo.png">` | `/images/logo.png` | **Replace with final logo file** — recommended: `logo.svg` for crisp scaling, or `logo.png` at 2× resolution (120×100px for 60×50 display) |

---

## LOGO REPLACEMENT

The logo file at `/images/logo.png` is referenced on every page. When the final logo is ready:

1. Drop the new file as `/images/logo.png` (PNG with transparency) OR `/images/logo.svg`
2. Update the `src` attribute on every page that has: `<img src="/images/logo.png" ...>`
3. If using SVG, update to `<img src="/images/logo.svg" ...>`
4. Recommended display size: `height: 44px` (already set in CSS)
5. File should be 2× resolution: provide at 88px height for retina clarity

---

*Last updated: Feb 2026 | Design Overhaul v2*
