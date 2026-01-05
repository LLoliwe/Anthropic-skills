# Pryntor Landing Page - Premium Governance-First Upgrade

**Version:** 2.0
**Date:** January 5, 2026
**Status:** Production-ready (pending [TODO] placeholders)

---

## Overview

Premium, governance-first landing page for Pryntor (Pty) Ltd. Designed to feel inevitable and premium within 5 seconds, increase desire without hype, and ship as clean, auditable code with strong UX, accessibility, and POPIA compliance.

**Key Features:**
- Distinctive design system (teal governance palette, IBM Plex Sans typography, control line motif)
- POPIA-compliant legal pages (Privacy Notice, Terms, Cookie Notice)
- Claim-safe copy with before/after contrast formula
- WCAG 2.1 AA accessibility compliance
- Zero dependencies (vanilla JS, static HTML)
- Three hero variants for A/B testing

---

## Project Structure

```
pryntor-landing/
├── public/                    # Website files (deploy this folder)
│   ├── index.html            # Main landing page
│   ├── privacy.html          # POPIA Privacy Notice
│   ├── terms.html            # Terms and Conditions
│   ├── cookies.html          # Cookie Notice
│   ├── styles.css            # Complete design system (1,200 lines)
│   └── app.js                # Interactions and animations (240 lines)
├── docs/                      # Documentation
│   ├── EXECUTIVE_DIFF.md     # High-level summary of changes
│   ├── BASELINE_REPORT.md    # Analysis of before/after state
│   ├── HERO_VARIANTS.md      # 3 A/B testing headline variants
│   ├── COPY_DECK_v2.md       # Complete copy inventory
│   ├── QA_CHECKLIST.md       # Pre-deployment verification
│   └── HANDOFF_EXTRACTED.md  # Original handoff documentation
├── artifacts/
│   └── screenshots/          # UI test screenshots (run test_screenshots.py)
├── DESIGN_TOKENS.json        # Design system tokens
├── test_screenshots.py       # Playwright testing script
└── README.md                 # This file
```

---

## Quick Start

### 1. Local Development

```bash
# Navigate to public directory
cd pryntor-landing/public

# Start local server
python3 -m http.server 8000

# Open in browser
open http://localhost:8000
```

### 2. Testing

```bash
# Install Playwright (if not installed)
pip3 install playwright
playwright install chromium

# Run screenshot tests
cd pryntor-landing
python3 test_screenshots.py

# Screenshots will be saved to: artifacts/screenshots/
```

### 3. Pre-Deployment Checklist

**Critical: Replace [TODO] placeholders before launch**

Search for `[TODO]` in the following files and replace with actual details:
- `public/privacy.html` - Company registration, address, Information Officer
- `public/terms.html` - Domain URL, company registration, address
- `public/cookies.html` - Information Officer details

Complete full QA checklist:
```bash
# Review the checklist
cat docs/QA_CHECKLIST.md

# Verify all items before deploying
```

---

## Deployment

### Netlify (Recommended)

1. **Connect Repository**
   ```
   Build command: (none, static site)
   Publish directory: public
   ```

2. **Configure Netlify Forms**
   - Forms are already configured with `data-netlify="true"`
   - No additional setup needed

3. **Environment**
   - Enable HTTPS (automatic with Netlify)
   - Configure custom domain
   - Set up email forwarding (lebo@pryntor.co.za)

### Alternative: Vercel, GitHub Pages, or any static host

- Deploy the `public/` folder
- Ensure HTTPS is enabled
- Configure form handling (Formspree, etc.)

---

## Design System

### Color Palette

```css
/* Governance-specific colors */
--color-primary: #0D9488;        /* Teal - trust, precision, regulated */
--color-primary-hover: #0F766E;
--color-accent: #F59E0B;         /* Amber - alerts, highlights */
--color-bg: #050505;             /* Near-black */
--color-fg: #E0E0E0;             /* Light grey */
```

### Typography

```css
/* Technical but readable */
--font-sans: 'IBM Plex Sans', sans-serif;
--font-mono: 'JetBrains Mono', monospace;
```

### Signature Elements

1. **Control Line:** 1px animated line at top of page (governance spine metaphor)
2. **Grid Texture:** 32px subtle grid overlay on background (systems metaphor)
3. **Footer Tagline:** "Systems that survive handovers" (brand reinforcement)

---

## Copy Strategy

### Formula: Before/After Contrast

```
Before: [Concrete pain points]
After: [Specific deliverables]
```

**Example:**
```
Before: Fragile approval chains, undocumented automations, unauditable decisions.
After: Codified governance, traceable AI workflows, risk-tiered controls.
```

### Guidelines

1. **No em dashes** (use commas, periods, colons)
2. **No invented proof** (no fake metrics, logos, testimonials)
3. **Specificity over hype** ("AES-256" > "secure")
4. **Deliverable outcomes only** (every claim must be implementable)
5. **Technical precision** ("30-day retention" > "temporary storage")

See `docs/COPY_DECK_v2.md` for complete copy inventory.

---

## Hero Variants (A/B Testing)

Three variants optimized for different buyer personas:

### Variant 1: Technical Operator (Current Live)
**Headline:** Governance as Operating System.
**Subhead:** Before/After contrast with technical specificity

### Variant 2: Founder/SME Buyer
**Headline:** Your processes break when you grow. Ours compound.
**Subhead:** Empathy for scaling pain points

### Variant 3: Regulated Environment Buyer
**Headline:** Governance-first infrastructure for regulated operations.
**Subhead:** Auditor-friendly language

See `docs/HERO_VARIANTS.md` for full variants and implementation strategy.

---

## Legal Compliance (POPIA)

### Privacy Notice
- Full POPIA compliance (16 sections)
- Cross-border transfer safeguards
- Retention periods (30 days default)
- Information Regulator complaint path
- **Status:** [TODO] placeholders for company details

### Terms and Conditions
- South African law and jurisdiction
- Liability limitations
- Waitlist/beta service disclosures
- **Status:** [TODO] placeholders for company details

### Cookie Notice
- Essential cookies only (no analytics by default)
- DNT (Do Not Track) respect
- Clear opt-out instructions
- **Status:** [TODO] placeholders for Information Officer

---

## Accessibility (WCAG 2.1 AA)

✅ **Compliant Features:**
- Skip link for keyboard users
- Semantic HTML (nav, main, footer)
- ARIA labels for all interactive elements
- Focus indicators (2px outline, 4px offset)
- Contrast ratios verified (4.5:1 minimum)
- Keyboard navigation for all features
- Screen reader tested
- `prefers-reduced-motion` respect

---

## Performance

**Predicted Metrics:**
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s

**Optimization:**
- Zero dependencies (vanilla JS only)
- CSS-only animations (no libraries)
- Font preconnect for faster loading
- Minimal bundle (< 50kb CSS, < 20kb JS)

---

## Form Features

### Dual-Mode Forms
- **Waitlist Mode:** Request access to services
- **Contact Mode:** General inquiries

### POPIA Compliance
- Required consent checkbox (links to Terms and Privacy)
- Optional marketing consent (unchecked by default)
- Clear data collection disclosure

### Spam Protection
- Honeypot field (invisible to humans)
- Rate limiting ready (server-side)

### Validation
- Inline error messages
- Keyboard accessible
- Success confirmation

---

## Browser Support

### Tested & Supported
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile Safari (iOS)
- Chrome Mobile (Android)

### Graceful Degradation
- Works without JavaScript (forms still submit)
- CSS Grid fallbacks for older browsers
- No-JS message displays if disabled

---

## Maintenance

### Updating Copy
1. Edit `docs/COPY_DECK_v2.md` first (source of truth)
2. Update HTML files to match
3. Follow copy guidelines (no em dashes, claim-safe, specific)

### Updating Design Tokens
1. Edit `DESIGN_TOKENS.json`
2. Update corresponding CSS variables in `styles.css`
3. Test across all breakpoints

### Adding New Sections
1. Follow semantic HTML structure
2. Add fade-in animation class: `fade-in-section`
3. Update sitemap (when adding new pages)

---

## Testing

### Manual Testing
```bash
# Start local server
cd public && python3 -m http.server 8000

# Test checklist (see docs/QA_CHECKLIST.md):
- All links work
- Forms validate and submit
- Animations respect prefers-reduced-motion
- Keyboard navigation works
- Mobile responsive
```

### Automated Testing
```bash
# Screenshot testing
python3 test_screenshots.py

# Accessibility audit (use browser DevTools)
# Lighthouse audit (use browser DevTools)
# HTML validator: https://validator.w3.org
```

---

## Troubleshooting

### Forms Not Submitting
- Check Netlify Forms configuration
- Verify `data-netlify="true"` attribute is present
- Check honeypot field is hidden (not removed)

### Fonts Not Loading
- Verify Google Fonts preconnect links
- Check network tab for CORS errors
- Consider self-hosting fonts for better performance

### Animations Not Working
- Check JavaScript console for errors
- Verify Intersection Observer is supported (modern browsers)
- Check `prefers-reduced-motion` setting

### Legal Pages Have [TODO]
- These must be replaced before deployment
- Never guess company details
- Get actual information from legal/compliance team

---

## Support & Contact

**Project Owner:** Pryntor (Pty) Ltd
**Email:** lebo@pryntor.co.za

**Technical Questions:**
- Review `docs/EXECUTIVE_DIFF.md` for high-level overview
- Review `docs/QA_CHECKLIST.md` for deployment verification
- Review `docs/COPY_DECK_v2.md` for all copy

---

## License & Usage

**Copyright:** © 2026 Pryntor (Pty) Ltd. All rights reserved.

This is proprietary code for Pryntor (Pty) Ltd. Unauthorized reproduction, distribution, or use is prohibited.

---

## Changelog

### Version 2.0 (January 5, 2026)
- Premium design system (teal palette, IBM Plex Sans)
- Signature control line and grid texture
- POPIA-compliant legal pages
- Hero variants for A/B testing
- Accessibility compliance (WCAG 2.1 AA)
- Zero-dependency implementation
- Complete documentation suite

---

**Ready to deploy.** Complete [TODO] replacements first.
