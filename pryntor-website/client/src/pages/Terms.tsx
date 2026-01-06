import Layout from "@/components/Layout";

export default function Terms() {
  return (
    <Layout>
      <div className="container max-w-3xl py-16 md:py-24">
        <h1 className="text-4xl font-bold mb-8">Terms and Conditions</h1>
        <p className="text-muted-foreground mb-8">Last updated: January 5, 2026</p>

        <div className="space-y-8 text-sm leading-relaxed">
          <section>
            <h2 className="text-lg font-bold mb-4">1. Acceptance of Terms</h2>
            <p className="text-muted-foreground">
              By accessing and using the website of Pryntor (Pty) Ltd ("Pryntor"), you agree to be bound by these Terms and Conditions. If you do not agree, please do not use our website.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">2. Permitted Use</h2>
            <p className="text-muted-foreground">
              You may use our website for lawful purposes only. You agree not to use the website in any way that violates any applicable local, national, or international law or regulation.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">3. Intellectual Property</h2>
            <p className="text-muted-foreground">
              All content, trademarks, and data on this website, including but not limited to software, databases, text, graphics, icons, and hyperlinks, are the property of or licensed to Pryntor and are protected by law. Unauthorized use is prohibited.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">4. User Submissions</h2>
            <p className="text-muted-foreground">
              Any information you submit through our forms must be accurate and complete. You are responsible for maintaining the confidentiality of your information.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">5. Disclaimers</h2>
            <p className="text-muted-foreground">
              This website is provided "as is" without any warranties, express or implied. Pryntor does not warrant that the website will be uninterrupted or error-free.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">6. Limitation of Liability</h2>
            <p className="text-muted-foreground">
              To the fullest extent permitted by law, Pryntor shall not be liable for any direct, indirect, incidental, special, or consequential damages arising out of or in connection with your use of this website.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">7. Indemnity</h2>
            <p className="text-muted-foreground">
              You agree to indemnify and hold Pryntor harmless from any claims, losses, liability, and expenses arising from your use of the website or violation of these Terms.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">8. Third-Party Links</h2>
            <p className="text-muted-foreground">
              Our website may contain links to third-party websites. We are not responsible for the content or practices of such websites.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">9. Waitlist and Beta Services</h2>
            <p className="text-muted-foreground">
              Joining our waitlist does not guarantee access to our services. Any beta services provided are for testing purposes and may be subject to change without notice. No pricing or timelines are guaranteed.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">10. Changes to Terms</h2>
            <p className="text-muted-foreground">
              We reserve the right to modify these Terms at any time. Your continued use of the website constitutes acceptance of the updated Terms.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">11. Governing Law</h2>
            <p className="text-muted-foreground">
              These Terms are governed by the laws of the Republic of South Africa. Any disputes shall be subject to the exclusive jurisdiction of the South African courts.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">12. Contact</h2>
            <p className="text-muted-foreground">
              For any questions regarding these Terms, please contact us at lebo@pryntor.co.za.
            </p>
          </section>
        </div>
      </div>
    </Layout>
  );
}
