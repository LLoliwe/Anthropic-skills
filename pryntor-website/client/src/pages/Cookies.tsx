import Layout from "@/components/Layout";

export default function Cookies() {
  return (
    <Layout>
      <div className="container max-w-3xl py-16 md:py-24">
        <h1 className="text-4xl font-bold mb-8">Cookie Notice</h1>
        <p className="text-muted-foreground mb-8">Last updated: January 5, 2026</p>

        <div className="space-y-8 text-sm leading-relaxed">
          <section>
            <h2 className="text-lg font-bold mb-4">1. What are Cookies?</h2>
            <p className="text-muted-foreground">
              Cookies are small text files that are placed on your device when you visit a website. They are widely used to make websites work more efficiently and to provide information to the owners of the site.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">2. How We Use Cookies</h2>
            <p className="text-muted-foreground mb-2">We use cookies for the following purposes:</p>
            <ul className="list-disc pl-5 space-y-1 text-muted-foreground">
              <li><strong>Essential Cookies:</strong> These are necessary for the website to function properly.</li>
              <li><strong>Analytics Cookies:</strong> We use these cookies to understand how visitors interact with our website.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">3. Your Choices</h2>
            <p className="text-muted-foreground">
              You can choose to accept or decline cookies. Most web browsers automatically accept cookies, but you can usually modify your browser setting to decline cookies if you prefer. Note that blocking cookies may affect the functionality of this website.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">4. Contact</h2>
            <p className="text-muted-foreground">
              If you have questions about our use of cookies, please contact us at lebo@pryntor.co.za.
            </p>
          </section>
        </div>
      </div>
    </Layout>
  );
}
