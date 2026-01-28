# Pryntor Landing Page - QA Checklist

**Version:** 2.0 (Upgraded)
**Date:** January 5, 2026
**Status:** Pre-deployment verification required

---

## 🎨 Visual Design Quality

### Typography
- [ ] IBM Plex Sans loads correctly (not falling back to Inter or system fonts)
- [ ] JetBrains Mono loads correctly for monospace elements
- [ ] Hero headline is 4.5rem (72px) on desktop, scales down on mobile
- [ ] No orphans or widows in hero subhead
- [ ] All text meets WCAG AA contrast ratios (4.5:1 minimum for body, 3:1 for large text)
- [ ] No em dashes present in any copy (search for "—")

### Color Palette
- [ ] Primary color is teal (#0D9488), not blue (#3B82F6)
- [ ] Accent color (amber #F59E0B) is used sparingly for alerts/highlights only
- [ ] Background grid texture is visible but subtle (rgba(255,255,255,0.02))
- [ ] Control line signature motif is visible at top of page

### Spacing & Rhythm
- [ ] Consistent vertical rhythm (multiples of 8px base unit)
- [ ] Hero section has generous whitespace (min-height: 90vh)
- [ ] Section padding is consistent across all breakpoints
- [ ] No layout shift or jank during page load

### Signature Elements
- [ ] Control line animates subtly on scroll
- [ ] Grid texture overlay visible on body background
- [ ] Footer has 2px teal border-top (brand reinforcement)
- [ ] "Systems that survive handovers" tagline present in footer

---

## ⚡ Interactions & Animations

### Scroll Animations
- [ ] Fade-in sections trigger at correct scroll depth (0.1 threshold)
- [ ] Staggered animation delay works (150ms per section)
- [ ] Animations respect `prefers-reduced-motion` setting
- [ ] No janky or stuttering animations
- [ ] Control line moves subtly on scroll (max 10px)

### Form Interactions
- [ ] Mode toggle switches between Waitlist and Contact forms correctly
- [ ] Active mode toggle button has correct styling
- [ ] Form inputs show focus ring on keyboard focus
- [ ] Form validation shows inline errors on blur
- [ ] Submit button disables during form submission
- [ ] Success message displays after successful submit
- [ ] Success message auto-hides after 5 seconds

### Hover States
- [ ] All capability cards lift on hover (translateY -4px)
- [ ] All buttons lift on hover (translateY -2px)
- [ ] Navigation links change color on hover
- [ ] FAQ items highlight border on hover
- [ ] All transitions are smooth (300ms ease)

### FAQ Accordion
- [ ] Details/summary elements work without JavaScript
- [ ] Plus icon rotates 45deg when FAQ opens
- [ ] Border color changes to primary on open
- [ ] Smooth open/close animation

---

## 📱 Responsive Design

### Desktop (1440px)
- [ ] Max-width container is 1280px, centered
- [ ] Hero headline is 4.5rem, readable in single glance
- [ ] Capabilities grid shows all 4 cards (2x2 with hero spanning 2 cols)
- [ ] Methodology steps show in 3 columns
- [ ] All sections have appropriate padding (24px vertical)

### Tablet (768px - 1023px)
- [ ] Navigation collapses "How we work" link (mobile priority)
- [ ] Capabilities grid stacks to 1 column
- [ ] Hero headline reduces to 3rem
- [ ] Methodology steps stack to 1 column
- [ ] Forms remain single column, readable

### Mobile (390px - 767px)
- [ ] Hero headline reduces to 2.5rem minimum
- [ ] CTA buttons stack vertically
- [ ] All text remains readable (16px minimum)
- [ ] Touch targets are min 44x44px
- [ ] No horizontal scroll
- [ ] Grid texture remains visible but not overwhelming

### Mobile (< 390px)
- [ ] Layout doesn't break
- [ ] Text remains readable
- [ ] Forms remain usable

---

## ♿ Accessibility (WCAG 2.1 AA Compliance)

### Keyboard Navigation
- [ ] Skip link appears on Tab focus
- [ ] All interactive elements are keyboard accessible
- [ ] Focus order is logical (top to bottom, left to right)
- [ ] Focus indicators are visible (2px outline, 4px offset)
- [ ] No keyboard traps
- [ ] FAQ items open/close with Enter/Space

### Screen Reader
- [ ] All images have alt text or aria-label
- [ ] Landmark regions are properly labeled (nav, main, footer)
- [ ] Form labels are associated with inputs
- [ ] Required fields are marked with aria-required
- [ ] Success/error messages have role="alert"
- [ ] Control line has aria-hidden="true"
- [ ] Status badge has proper role="status"

### Color & Contrast
- [ ] Text meets WCAG AA contrast (4.5:1 for normal, 3:1 for large)
- [ ] Primary teal (#0D9488) on black (#050505) passes contrast check
- [ ] Form error states don't rely on color alone
- [ ] Links are underlined or have sufficient visual distinction

### Forms
- [ ] All form inputs have visible labels
- [ ] Required fields are clearly marked with *
- [ ] Error messages are descriptive
- [ ] Honeypot field is hidden from screen readers (aria-hidden)
- [ ] Consent checkboxes are keyboard accessible

---

## 🔒 Security & Privacy

### Form Security
- [ ] Honeypot field is present in both forms
- [ ] Honeypot is invisible (position: absolute, left: -9999px)
- [ ] Forms use POST method, not GET
- [ ] No sensitive data in URL parameters
- [ ] Rate limiting is configured (server-side or Netlify)

### POPIA Compliance
- [ ] Privacy Notice link is present in forms
- [ ] Terms link is present in forms
- [ ] Consent checkbox is required before submission
- [ ] Marketing checkbox is optional and unchecked by default
- [ ] Privacy Notice discloses all data collection
- [ ] All [TODO] placeholders are documented
- [ ] No third-party analytics or tracking by default
- [ ] No cookies except essential (documented in Cookie Notice)

### Legal Pages
- [ ] Privacy Notice is complete and POPIA-aligned
- [ ] Terms and Conditions cover all requirements
- [ ] Cookie Notice explains all cookies used
- [ ] All legal pages use "Last updated" date
- [ ] Information Regulator contact details are correct
- [ ] [TODO] placeholders are clearly marked

---

## 🚀 Performance

### Loading Speed
- [ ] First Contentful Paint (FCP) < 1.5s
- [ ] Largest Contentful Paint (LCP) < 2.5s
- [ ] Time to Interactive (TTI) < 3.5s
- [ ] No render-blocking resources
- [ ] Fonts are preloaded or self-hosted

### Optimization
- [ ] CSS is minified (production)
- [ ] JavaScript is minified (production)
- [ ] No unused CSS rules (audit with coverage tool)
- [ ] Images are optimized (if any added later)
- [ ] Lazy loading for below-fold content (if applicable)

### Bundle Size
- [ ] CSS < 50kb uncompressed
- [ ] JavaScript < 20kb uncompressed
- [ ] No external dependencies (vanilla JS only)
- [ ] Fonts loaded efficiently (preconnect, font-display: swap)

---

## 🌐 Cross-Browser Compatibility

### Desktop Browsers
- [ ] Chrome (latest): All features work
- [ ] Firefox (latest): All features work
- [ ] Safari (latest): All features work
- [ ] Edge (latest): All features work

### Mobile Browsers
- [ ] Chrome Mobile (Android): All features work
- [ ] Safari Mobile (iOS): All features work
- [ ] Samsung Internet: All features work

### Fallbacks
- [ ] Site works without JavaScript (forms submit, no animations)
- [ ] No-JS message displays if JS disabled
- [ ] CSS grid fallback for older browsers (feature query)

---

## 📧 Form Functionality

### Waitlist Form
- [ ] All required fields validate correctly
- [ ] Email validation works (RFC-compliant)
- [ ] Dropdown options are all selectable
- [ ] Honeypot blocks spam bots
- [ ] Form submits to correct endpoint
- [ ] Success message displays on successful submit
- [ ] Form resets after success

### Contact Form
- [ ] All required fields validate correctly
- [ ] Email validation works
- [ ] Textarea allows multi-line input
- [ ] Optional fields are truly optional
- [ ] Capabilities checkbox is optional
- [ ] Form submits correctly
- [ ] Success message displays

### Validation
- [ ] Inline validation on blur
- [ ] Error states clear on input
- [ ] Submit button disabled while sending
- [ ] Error message if submission fails
- [ ] Fallback to "email lebo@pryntor.co.za" on failure

---

## 🔍 SEO & Meta

### Meta Tags
- [ ] Title tag is present and descriptive (< 60 chars)
- [ ] Meta description is present (< 160 chars)
- [ ] Viewport meta tag is set correctly
- [ ] Theme-color meta tag matches brand
- [ ] Canonical URL is set correctly

### Open Graph
- [ ] og:title is set
- [ ] og:description is set
- [ ] og:type is "website"
- [ ] og:url is set (when domain is live)

### Structured Data
- [ ] Consider adding Organization schema (future)
- [ ] Consider adding FAQPage schema (future)

### Sitemap
- [ ] Create sitemap.xml with all 4 pages (future, when deployed)

---

## 📄 Content Quality

### Copy Review
- [ ] No em dashes anywhere (search entire site)
- [ ] No invented proof (no fake testimonials, metrics, logos)
- [ ] No builder branding (Netlify, Vercel logos removed from footer)
- [ ] All copy is claim-safe (deliverable outcomes only)
- [ ] Legal language is precise and accurate
- [ ] All [TODO] placeholders are documented

### Hero Copy
- [ ] Before/After structure is clear
- [ ] Specificity is high (concrete outcomes, not abstractions)
- [ ] Contrast is evident (risk removal obvious)
- [ ] No hype or superlatives

### Technical Accuracy
- [ ] "AES-256" claim is verifiable
- [ ] "30-day retention policy" is documented in internal processes
- [ ] "Zero third-party analytics" is true
- [ ] All technical claims can be audited

---

## 🧪 Testing Checklist

### Manual Testing
- [ ] Test all links (internal and external)
- [ ] Test all buttons and CTAs
- [ ] Test form submission (both modes)
- [ ] Test form validation (empty, invalid, valid)
- [ ] Test on real devices (iOS, Android)
- [ ] Test with screen reader (NVDA or VoiceOver)
- [ ] Test keyboard navigation only
- [ ] Test with JS disabled

### Automated Testing
- [ ] Lighthouse audit score > 90 (all categories)
- [ ] WAVE accessibility audit (0 errors)
- [ ] HTML validator (0 errors)
- [ ] CSS validator (0 errors)
- [ ] Broken link checker (0 broken links)

### Visual Regression
- [ ] Desktop screenshot matches design intent
- [ ] Tablet screenshot matches design intent
- [ ] Mobile screenshot matches design intent
- [ ] Print stylesheet works correctly

---

## 🚢 Pre-Deployment Checklist

### Replace [TODO] Placeholders
- [ ] Company registration number
- [ ] Registered physical address
- [ ] Information Officer name and contact
- [ ] Server/hosting location and jurisdiction
- [ ] Primary domain URL

### Configuration
- [ ] Netlify Forms configured (or alternative)
- [ ] HTTPS/SSL certificate active
- [ ] Domain DNS configured
- [ ] Email forwarding set up (lebo@pryntor.co.za)
- [ ] Redirect rules configured (www to non-www, etc.)

### Legal Verification
- [ ] Legal team reviews Privacy Notice
- [ ] Legal team reviews Terms and Conditions
- [ ] Legal team reviews Cookie Notice
- [ ] Information Officer approves data handling disclosure

### Final Checks
- [ ] Remove console.log statements from JS
- [ ] Minify CSS and JS for production
- [ ] Test form submissions in production environment
- [ ] Set up monitoring (uptime, errors)
- [ ] Create backup of site files

---

## 📊 Success Metrics (Post-Launch)

### Week 1
- [ ] Track bounce rate (target: < 60%)
- [ ] Track time on page (target: > 90 seconds)
- [ ] Track form submission rate (target: > 3%)
- [ ] Track mobile vs desktop traffic

### Week 2
- [ ] A/B test hero variants (if traffic permits)
- [ ] Monitor form drop-off points
- [ ] Check error logs for issues
- [ ] Gather user feedback

### Month 1
- [ ] Conversion rate by source
- [ ] Most engaged section (scroll depth analytics)
- [ ] Device/browser breakdown
- [ ] Legal page view counts

---

**End of QA Checklist**

**Note:** This checklist should be completed before deploying to production. All items marked with [TODO] must be replaced with actual company details before launch.
