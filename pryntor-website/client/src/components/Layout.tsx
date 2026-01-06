import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { Link, useLocation } from "wouter";

export default function Layout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();
  const isHome = location === "/";

  const scrollToForm = () => {
    if (isHome) {
      document.getElementById("contact-form")?.scrollIntoView({ behavior: "smooth" });
    } else {
      window.location.href = "/#contact-form";
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground font-sans selection:bg-primary selection:text-primary-foreground flex flex-col">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-md">
        <div className="container flex h-16 items-center justify-between">
          <Link href="/" className="font-bold text-xl tracking-tight cursor-pointer">PRYNTOR</Link>
          <div className="flex items-center gap-6">
            <Link href="/#how-we-work" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors hidden md:block">
              How we work
            </Link>
            <Button 
              onClick={scrollToForm}
              className="font-medium rounded-none border border-primary bg-primary/10 text-primary hover:bg-primary hover:text-primary-foreground transition-all"
            >
              Request access
            </Button>
          </div>
        </div>
      </nav>

      <main className="flex-1 relative">
        {children}
      </main>

      {/* Footer */}
      <footer className="py-12 border-t border-border/50 bg-background">
        <div className="container flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="text-sm text-muted-foreground">
            <div className="font-bold text-foreground mb-1">PRYNTOR (Pty) Ltd</div>
            &copy; {new Date().getFullYear()} All rights reserved.
          </div>
          <div className="flex gap-6 text-sm">
            <Link href="/privacy" className="text-muted-foreground hover:text-foreground">Privacy</Link>
            <Link href="/terms" className="text-muted-foreground hover:text-foreground">Terms</Link>
            <Link href="/cookies" className="text-muted-foreground hover:text-foreground">Cookies</Link>
            <a href="mailto:lebo@pryntor.co.za" className="text-muted-foreground hover:text-foreground">lebo@pryntor.co.za</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
