import Layout from "@/components/Layout";

export default function Privacy() {
  return (
    <Layout>
      <div className="container max-w-3xl py-16 md:py-24">
        <h1 className="text-4xl font-bold mb-8">Privacy Notice</h1>
        <p className="text-muted-foreground mb-8">Last updated: January 5, 2026</p>

        <div className="space-y-8 text-sm leading-relaxed">
          <section>
            <h2 className="text-lg font-bold mb-4">1. Introduction</h2>
            <p className="text-muted-foreground">
              Pryntor (Pty) Ltd ("we", "us", "our") is committed to protecting your privacy. This Privacy Notice explains how we collect, use, disclose, and safeguard your information when you visit our website or engage with our services, in compliance with the Protection of Personal Information Act (POPIA).
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">2. Responsible Party</h2>
            <p className="text-muted-foreground">
              Pryntor (Pty) Ltd is the Responsible Party for your personal information.<br />
              Email: lebo@pryntor.co.za<br />
              Address: Available on request
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">3. Information We Collect</h2>
            <p className="text-muted-foreground mb-2">We may collect the following personal information:</p>
            <ul className="list-disc pl-5 space-y-1 text-muted-foreground">
              <li><strong>Identity Data:</strong> Name, job title, company name.</li>
              <li><strong>Contact Data:</strong> Email address, phone number.</li>
              <li><strong>Technical Data:</strong> IP address, browser type, operating system (via cookies).</li>
              <li><strong>Usage Data:</strong> Information about how you use our website.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">4. Source of Information</h2>
            <p className="text-muted-foreground">
              We collect information directly from you when you fill out forms on our website or communicate with us via email. We also collect technical data automatically as you interact with our website.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">5. Purpose of Collection</h2>
            <p className="text-muted-foreground mb-2">We use your information for the following purposes:</p>
            <ul className="list-disc pl-5 space-y-1 text-muted-foreground">
              <li>To provide and manage our services.</li>
              <li>To communicate with you regarding your inquiries or waitlist status.</li>
              <li>To improve our website and services.</li>
              <li>To comply with legal obligations.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">6. Voluntary Supply and Consequences</h2>
            <p className="text-muted-foreground">
              Providing your personal information is voluntary. However, if you do not provide the requested information, we may be unable to respond to your inquiries or provide you with access to our services.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">7. Sharing of Information</h2>
            <p className="text-muted-foreground mb-2">We do not sell your personal information. We may share your information with:</p>
            <ul className="list-disc pl-5 space-y-1 text-muted-foreground">
              <li><strong>Service Providers:</strong> Third-party vendors who assist with our operations (e.g., hosting, email delivery).</li>
              <li><strong>Legal Authorities:</strong> If required by law or to protect our rights.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">8. Cross-Border Transfers</h2>
            <p className="text-muted-foreground">
              We may transfer your information to service providers located outside of South Africa. We ensure that such transfers are subject to appropriate safeguards as required by POPIA.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">9. Security</h2>
            <p className="text-muted-foreground">
              We implement reasonable technical and organizational measures to protect your personal information from unauthorized access, loss, or misuse.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">10. Retention</h2>
            <p className="text-muted-foreground">
              We retain your personal information only for as long as necessary to fulfill the purposes for which it was collected, or as required by law.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">11. Your Rights</h2>
            <p className="text-muted-foreground mb-2">You have the right to:</p>
            <ul className="list-disc pl-5 space-y-1 text-muted-foreground">
              <li><strong>Access:</strong> Request a copy of the personal information we hold about you.</li>
              <li><strong>Correction:</strong> Request correction of inaccurate or incomplete information.</li>
              <li><strong>Objection:</strong> Object to the processing of your personal information.</li>
              <li><strong>Deletion:</strong> Request deletion of your personal information, subject to legal retention requirements.</li>
            </ul>
            <p className="text-muted-foreground mt-2">To exercise these rights, please contact us at lebo@pryntor.co.za.</p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">12. Direct Marketing</h2>
            <p className="text-muted-foreground">
              We will only send you direct marketing communications if you have consented to receive them or if you are an existing client. You may opt-out of marketing communications at any time by clicking the "unsubscribe" link in our emails or contacting us.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">13. Complaints</h2>
            <p className="text-muted-foreground">
              You have the right to lodge a complaint with the Information Regulator (South Africa).<br />
              Website: https://inforegulator.org.za/<br />
              Email: POPIAComplaints@inforegulator.org.za
            </p>
          </section>
        </div>
      </div>
    </Layout>
  );
}
