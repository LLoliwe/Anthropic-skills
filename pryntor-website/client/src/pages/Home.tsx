import Layout from "@/components/Layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowRight, Check, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link } from "wouter";
import { z } from "zod";

// --- Schema Definitions ---

const waitlistSchema = z.object({
  fullName: z.string().min(2, "Name is required"),
  email: z.string().email("Invalid email address"),
  company: z.string().min(1, "Company is required"),
  role: z.string().optional(),
  goal: z.string().min(1, "Please select a primary goal"),
  notes: z.string().max(300, "Notes must be under 300 characters").optional(),
  consent: z.boolean().refine((val) => val === true, {
    message: "You must agree to the terms",
  }),
});

const contactSchema = z.object({
  fullName: z.string().min(2, "Name is required"),
  email: z.string().email("Invalid email address"),
  company: z.string().optional(),
  message: z.string().min(10, "Message is too short").max(1000, "Message too long"),
  consent: z.boolean().refine((val) => val === true, {
    message: "You must agree to the terms",
  }),
  capabilities: z.boolean().optional(),
});

// --- Components ---

const SectionDivider = () => (
  <div className="w-full h-px bg-border/50 my-0" />
);

const GridBackground = () => (
  <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
    <div 
      className="absolute inset-0 opacity-[0.15]"
      style={{
        backgroundImage: `linear-gradient(to right, #333 1px, transparent 1px),
                          linear-gradient(to bottom, #333 1px, transparent 1px)`,
        backgroundSize: '40px 40px'
      }}
    />
    <div className="absolute inset-0 bg-gradient-to-b from-background via-transparent to-background" />
  </div>
);

export default function Home() {
  const [mode, setMode] = useState<"waitlist" | "contact">("waitlist");
  const [isSubmitted, setIsSubmitted] = useState(false);

  const waitlistForm = useForm<z.infer<typeof waitlistSchema>>({
    resolver: zodResolver(waitlistSchema),
    defaultValues: {
      fullName: "",
      email: "",
      company: "",
      role: "",
      goal: "",
      notes: "",
      consent: false,
    },
  });

  const contactForm = useForm<z.infer<typeof contactSchema>>({
    resolver: zodResolver(contactSchema),
    defaultValues: {
      fullName: "",
      email: "",
      company: "",
      message: "",
      consent: false,
      capabilities: false,
    },
  });

  const onWaitlistSubmit = (data: z.infer<typeof waitlistSchema>) => {
    console.log("Waitlist Data:", data);
    setIsSubmitted(true);
  };

  const onContactSubmit = (data: z.infer<typeof contactSchema>) => {
    console.log("Contact Data:", data);
    setIsSubmitted(true);
  };

  const scrollToForm = () => {
    document.getElementById("contact-form")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative py-24 md:py-32 overflow-hidden border-b border-border/50">
        <GridBackground />
        <div className="container relative z-10">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 mb-8 border border-primary/30 bg-primary/5 text-primary text-xs font-mono uppercase tracking-wider">
              <span className="w-2 h-2 bg-primary rounded-full animate-pulse" />
              System Status: Operational
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-[1.1] mb-6">
              Governance as <br />
              <span className="text-muted-foreground">Operating System.</span>
            </h1>
            
            <p className="text-xl text-muted-foreground max-w-2xl mb-10 leading-relaxed">
              We build governance-first systems for automation, measurement, and decision support. 
              Replace fragile processes with audit-ready infrastructure.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 mb-16">
              <Button 
                size="lg" 
                onClick={scrollToForm}
                className="rounded-none text-base px-8 h-12 bg-primary hover:bg-primary/90 text-primary-foreground"
              >
                {mode === "waitlist" ? "Request access" : "Request a call"}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
              <Button 
                variant="outline" 
                size="lg" 
                asChild
                className="rounded-none text-base px-8 h-12 border-border hover:bg-muted/50"
              >
                <a href="mailto:lebo@pryntor.co.za">Email lebo@pryntor.co.za</a>
              </Button>
            </div>

            <div className="flex flex-wrap gap-x-8 gap-y-4 text-sm font-mono text-muted-foreground border-t border-border/50 pt-8">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-primary" />
                Audit-grade decisions
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-primary" />
                Modular systems
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-primary" />
                Privacy-first by default
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* What We Build */}
      <section className="py-24 bg-muted/5">
        <div className="container">
          <div className="mb-12">
            <h2 className="text-sm font-mono uppercase tracking-widest text-muted-foreground mb-2">Capabilities</h2>
            <h3 className="text-3xl font-bold">Core Infrastructure</h3>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                title: "Governance-as-code",
                desc: "Codified rules for AI and automation workflows.",
                bullets: ["Policy enforcement", "Risk guardrails"]
              },
              {
                title: "Growth OS",
                desc: "Systems-based marketing and growth infrastructure.",
                bullets: ["Unified data layer", "Campaign automation"]
              },
              {
                title: "Automation Workflows",
                desc: "Resilient data pipelines and process automation.",
                bullets: ["Error handling", "Self-healing flows"]
              },
              {
                title: "Decision Support",
                desc: "High-fidelity surfaces for strategic oversight.",
                bullets: ["Real-time metrics", "Audit trails"]
              }
            ].map((card, i) => (
              <Card key={i} className="bg-card border-border/50 rounded-none hover:border-primary/50 transition-colors duration-300">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold">{card.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground text-sm mb-4">{card.desc}</p>
                  <ul className="space-y-2">
                    {card.bullets.map((bullet, j) => (
                      <li key={j} className="text-xs font-mono text-muted-foreground flex items-center gap-2">
                        <span className="w-1 h-1 bg-primary" />
                        {bullet}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* Differentiator */}
      <section className="py-24">
        <div className="container grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-3xl font-bold mb-6">Governance First.</h2>
            <p className="text-lg text-muted-foreground mb-8 leading-relaxed">
              We prioritize evidence gating, traceability, and risk tiers. Our documentation is designed to survive handovers, ensuring your systems remain resilient long after deployment.
            </p>
            <ul className="space-y-4">
              {[
                "Clear operating rules",
                "Automation that can be audited",
                "Measurement tied to decisions",
                "Documentation that survives handovers",
                "Systems that compound over time"
              ].map((item, i) => (
                <li key={i} className="flex items-center gap-3">
                  <div className="flex-shrink-0 w-5 h-5 rounded-none border border-primary/50 flex items-center justify-center text-primary">
                    <Check className="w-3 h-3" />
                  </div>
                  <span className="text-foreground">{item}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="relative aspect-square lg:aspect-video bg-muted/10 border border-border/50 p-8 flex items-center justify-center">
            <div className="absolute inset-0 bg-[url('/images/hero-grid.png')] bg-cover opacity-20 mix-blend-overlay" />
            <div className="relative z-10 font-mono text-sm text-primary/80">
              {`{
"system": "active",
"governance": {
  "audit_log": true,
  "risk_tier": "low",
  "compliance": "POPIA"
},
"status": "optimized"
}`}
            </div>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* How We Work */}
      <section id="how-we-work" className="py-24 bg-muted/5">
        <div className="container">
          <div className="mb-16 text-center">
            <h2 className="text-sm font-mono uppercase tracking-widest text-muted-foreground mb-2">Methodology</h2>
            <h3 className="text-3xl font-bold">The Process</h3>
          </div>

          <div className="grid md:grid-cols-3 gap-8 relative">
            {/* Connecting Line (Desktop) */}
            <div className="hidden md:block absolute top-8 left-0 w-full h-px bg-border/50 -z-10" />
            
            {[
              { step: "01", title: "Diagnose", desc: "Deep dive into current bottlenecks and risk factors." },
              { step: "02", title: "Build the spine", desc: "Establish core governance and data infrastructure." },
              { step: "03", title: "Ship and harden", desc: "Deploy, monitor, and refine for resilience." }
            ].map((item, i) => (
              <div key={i} className="bg-background border border-border/50 p-8 relative group hover:border-primary/50 transition-colors">
                <div className="text-4xl font-mono font-bold text-muted-foreground/20 mb-6 group-hover:text-primary/20 transition-colors">
                  {item.step}
                </div>
                <h4 className="text-xl font-bold mb-3">{item.title}</h4>
                <p className="text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Who It's For */}
      <section className="py-24">
        <div className="container">
          <h2 className="text-3xl font-bold mb-12 text-center">Built for Operators</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {[
              "Founders", "Ops Leaders", "Marketing Operators",
              "Regulated Environments", "SMEs Scaling Delivery", "Teams tired of fragile processes"
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-center p-6 border border-border/50 bg-muted/5 text-center font-medium hover:bg-muted/10 transition-colors">
                {item}
              </div>
            ))}
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* Form Section */}
      <section id="contact-form" className="py-24 bg-muted/5">
        <div className="container max-w-2xl">
          <div className="flex justify-center mb-12">
            <div className="inline-flex border border-border bg-background p-1">
              <button
                onClick={() => { setMode("waitlist"); setIsSubmitted(false); }}
                className={`px-6 py-2 text-sm font-medium transition-colors ${
                  mode === "waitlist" 
                    ? "bg-primary text-primary-foreground" 
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Waitlist
              </button>
              <button
                onClick={() => { setMode("contact"); setIsSubmitted(false); }}
                className={`px-6 py-2 text-sm font-medium transition-colors ${
                  mode === "contact" 
                    ? "bg-primary text-primary-foreground" 
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Contact
              </button>
            </div>
          </div>

          <Card className="border-border rounded-none shadow-none bg-background">
            <CardHeader>
              <CardTitle className="text-2xl text-center">
                {mode === "waitlist" ? "Request Access" : "Send a Message"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isSubmitted ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto mb-6">
                    <Check className="w-8 h-8" />
                  </div>
                  <h3 className="text-xl font-bold mb-2">
                    {mode === "waitlist" ? "Request Received" : "Message Sent"}
                  </h3>
                  <p className="text-muted-foreground">
                    {mode === "waitlist" 
                      ? "If it's a fit, we will reply with next steps." 
                      : "We will reply via email shortly."}
                  </p>
                  <Button 
                    variant="link" 
                    onClick={() => setIsSubmitted(false)}
                    className="mt-6"
                  >
                    Reset form
                  </Button>
                </div>
              ) : (
                mode === "waitlist" ? (
                  <Form {...waitlistForm}>
                    <form onSubmit={waitlistForm.handleSubmit(onWaitlistSubmit)} className="space-y-6">
                      <FormField
                        control={waitlistForm.control}
                        name="fullName"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Full Name</FormLabel>
                            <FormControl>
                              <Input placeholder="Jane Doe" {...field} className="rounded-none bg-muted/5" />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={waitlistForm.control}
                        name="email"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Email</FormLabel>
                            <FormControl>
                              <Input placeholder="jane@company.com" {...field} className="rounded-none bg-muted/5" />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <div className="grid grid-cols-2 gap-4">
                        <FormField
                          control={waitlistForm.control}
                          name="company"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Company</FormLabel>
                              <FormControl>
                                <Input placeholder="Acme Inc." {...field} className="rounded-none bg-muted/5" />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={waitlistForm.control}
                          name="role"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Role (Optional)</FormLabel>
                              <FormControl>
                                <Input placeholder="CTO" {...field} className="rounded-none bg-muted/5" />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                      <FormField
                        control={waitlistForm.control}
                        name="goal"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Primary Goal</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger className="rounded-none bg-muted/5">
                                  <SelectValue placeholder="Select a goal" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectItem value="governance">Governance and risk</SelectItem>
                                <SelectItem value="automation">Automation</SelectItem>
                                <SelectItem value="growth">Growth and marketing OS</SelectItem>
                                <SelectItem value="dashboards">Decision dashboards</SelectItem>
                                <SelectItem value="unsure">Not sure yet</SelectItem>
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={waitlistForm.control}
                        name="notes"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Notes (Optional)</FormLabel>
                            <FormControl>
                              <Textarea 
                                placeholder="Tell us about your needs..." 
                                className="resize-none rounded-none bg-muted/5" 
                                {...field} 
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={waitlistForm.control}
                        name="consent"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-none border p-4">
                            <FormControl>
                              <Checkbox
                                checked={field.value}
                                onCheckedChange={field.onChange}
                              />
                            </FormControl>
                            <div className="space-y-1 leading-none">
                              <FormLabel>
                                I agree to the <Link href="/terms" className="underline hover:text-primary">Terms</Link> and acknowledge the <Link href="/privacy" className="underline hover:text-primary">Privacy Notice</Link>.
                              </FormLabel>
                              <FormMessage />
                            </div>
                          </FormItem>
                        )}
                      />
                      <Button type="submit" className="w-full rounded-none h-12 text-base">
                        Request Access
                      </Button>
                    </form>
                  </Form>
                ) : (
                  <Form {...contactForm}>
                    <form onSubmit={contactForm.handleSubmit(onContactSubmit)} className="space-y-6">
                      <FormField
                        control={contactForm.control}
                        name="fullName"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Full Name</FormLabel>
                            <FormControl>
                              <Input placeholder="Jane Doe" {...field} className="rounded-none bg-muted/5" />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={contactForm.control}
                        name="email"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Email</FormLabel>
                            <FormControl>
                              <Input placeholder="jane@company.com" {...field} className="rounded-none bg-muted/5" />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={contactForm.control}
                        name="company"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Company (Optional)</FormLabel>
                            <FormControl>
                              <Input placeholder="Acme Inc." {...field} className="rounded-none bg-muted/5" />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={contactForm.control}
                        name="message"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Message</FormLabel>
                            <FormControl>
                              <Textarea 
                                placeholder="How can we help?" 
                                className="min-h-[120px] resize-none rounded-none bg-muted/5" 
                                {...field} 
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={contactForm.control}
                        name="consent"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-none border p-4">
                            <FormControl>
                              <Checkbox
                                checked={field.value}
                                onCheckedChange={field.onChange}
                              />
                            </FormControl>
                            <div className="space-y-1 leading-none">
                              <FormLabel>
                                I agree to the <Link href="/terms" className="underline hover:text-primary">Terms</Link> and acknowledge the <Link href="/privacy" className="underline hover:text-primary">Privacy Notice</Link>.
                              </FormLabel>
                              <FormMessage />
                            </div>
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={contactForm.control}
                        name="capabilities"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                            <FormControl>
                              <Checkbox
                                checked={field.value}
                                onCheckedChange={field.onChange}
                              />
                            </FormControl>
                            <div className="space-y-1 leading-none">
                              <FormLabel>
                                Send me the capabilities one-pager.
                              </FormLabel>
                            </div>
                          </FormItem>
                        )}
                      />
                      <Button type="submit" className="w-full rounded-none h-12 text-base">
                        Send Message
                      </Button>
                    </form>
                  </Form>
                )
              )}
            </CardContent>
          </Card>
        </div>
      </section>

      <SectionDivider />

      {/* Trust & Privacy */}
      <section className="py-16">
        <div className="container max-w-4xl text-center">
          <h3 className="text-lg font-bold mb-6">Trust & Privacy</h3>
          <div className="flex flex-wrap justify-center gap-8 mb-8 text-sm text-muted-foreground">
            <span className="flex items-center gap-2"><ShieldCheck className="w-4 h-4" /> Data minimisation</span>
            <span className="flex items-center gap-2"><ShieldCheck className="w-4 h-4" /> POPIA-aligned handling</span>
            <span className="flex items-center gap-2"><ShieldCheck className="w-4 h-4" /> No resale of personal data</span>
            <span className="flex items-center gap-2"><ShieldCheck className="w-4 h-4" /> Opt-out anytime</span>
          </div>
          <p className="text-sm text-muted-foreground max-w-2xl mx-auto">
            We collect only what is necessary to communicate with you. Your data is stored securely, never sold, and retained only as long as required for our business relationship. You may request deletion at any time.
          </p>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-24 bg-muted/5">
        <div className="container max-w-3xl">
          <h2 className="text-3xl font-bold mb-12 text-center">FAQ</h2>
          <div className="space-y-8">
            {[
              { q: "What exactly do you deliver?", a: "We deliver fully documented, audit-ready automated systems and governance frameworks. Case examples available on request." },
              { q: "Do you build with our existing tools?", a: "Yes. We integrate with your existing stack to ensure continuity and minimize friction." },
              { q: "How do you handle confidentiality?", a: "We operate under strict NDAs and data minimization principles. Your intellectual property remains yours." },
              { q: "What industries do you work with?", a: "We focus on regulated environments, high-growth tech, and operations-heavy sectors." },
              { q: "How fast can we start?", a: "We typically begin with a diagnosis phase within 1-2 weeks of initial engagement." }
            ].map((item, i) => (
              <div key={i} className="border-b border-border/50 pb-6 last:border-0">
                <h4 className="font-bold mb-2">{item.q}</h4>
                <p className="text-muted-foreground">{item.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </Layout>
  );
}
