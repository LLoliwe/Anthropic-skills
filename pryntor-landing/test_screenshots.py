#!/usr/bin/env python3
"""
Pryntor Landing Page - Screenshot Testing
Captures screenshots at desktop, tablet, and mobile viewports
"""

from playwright.sync_api import sync_playwright
import sys

# Viewport configurations
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "tablet": {"width": 834, "height": 1112},
    "mobile": {"width": 390, "height": 844},
}

def capture_screenshots(base_url="http://localhost:8000"):
    """Capture screenshots of the Pryntor landing page at different viewports"""

    print(f"Starting screenshot capture from {base_url}")

    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)

        for viewport_name, viewport_size in VIEWPORTS.items():
            print(f"\n📸 Capturing {viewport_name} view ({viewport_size['width']}x{viewport_size['height']})")

            # Create new page with specific viewport
            page = browser.new_page(viewport=viewport_size)

            try:
                # Navigate to the page
                page.goto(f"{base_url}/index.html", wait_until="networkidle")

                # Wait a bit for animations to settle
                page.wait_for_timeout(1000)

                # Capture full-page screenshot
                screenshot_path = f"artifacts/screenshots/{viewport_name}_full.png"
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"  ✓ Saved full-page screenshot: {screenshot_path}")

                # Capture above-the-fold screenshot
                screenshot_path_atf = f"artifacts/screenshots/{viewport_name}_hero.png"
                page.screenshot(path=screenshot_path_atf, full_page=False)
                print(f"  ✓ Saved hero screenshot: {screenshot_path_atf}")

                # Test form mode switching
                if viewport_name == "desktop":
                    print(f"  Testing form mode toggle...")
                    page.click('button[data-mode="contact"]')
                    page.wait_for_timeout(500)
                    screenshot_path_contact = f"artifacts/screenshots/desktop_contact_form.png"
                    page.screenshot(path=screenshot_path_contact, full_page=False,
                                   clip={'x': 0, 'y': 3000, 'width': viewport_size['width'], 'height': 800})
                    print(f"  ✓ Saved contact form screenshot: {screenshot_path_contact}")

                # Check console errors
                errors = []
                page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)

                if errors:
                    print(f"  ⚠️  Console errors detected:")
                    for error in errors:
                        print(f"     - {error}")

            except Exception as e:
                print(f"  ❌ Error capturing {viewport_name}: {e}")

            finally:
                page.close()

        browser.close()

    print("\n✅ Screenshot capture complete!")
    print("   Screenshots saved to: artifacts/screenshots/")

def main():
    # Check if custom URL provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    print("""
╔══════════════════════════════════════════════════════════════╗
║  PRYNTOR LANDING PAGE - SCREENSHOT TESTING                   ║
╚══════════════════════════════════════════════════════════════╝

Prerequisites:
1. Start local server:
   cd pryntor-landing/public && python3 -m http.server 8000

2. Install Playwright browsers (if not done):
   playwright install chromium

""")

    try:
        capture_screenshots(base_url)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure local server is running: python3 -m http.server 8000")
        print("  2. Ensure Playwright is installed: pip install playwright")
        print("  3. Ensure browser is installed: playwright install chromium")
        sys.exit(1)

if __name__ == "__main__":
    main()
