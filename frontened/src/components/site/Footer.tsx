import { Link } from "@tanstack/react-router";
import { Wrench, Twitter, Facebook, Instagram, Linkedin } from "lucide-react";

const cols = [
  {
    title: "Product",
    links: [
      { to: "/services", label: "Services" },
      { to: "/how-it-works", label: "How it works" },
      { to: "/pricing", label: "Pricing" },
      { to: "/download", label: "Download app" },
    ],
  },
  {
    title: "For mechanics",
    links: [
      { to: "/for-mechanics", label: "Become a mechanic" },
      { to: "/for-mechanics", label: "Earnings" },
      { to: "/for-mechanics", label: "Requirements" },
    ],
  },
  {
    title: "Company",
    links: [
      { to: "/about", label: "About" },
      { to: "/contact", label: "Contact" },
      { to: "/faq", label: "FAQ" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="border-t border-border bg-surface">
      <div className="container-page grid gap-10 py-14 md:grid-cols-5">
        <div className="md:col-span-2">
          <Link to="/" className="flex items-center gap-2 font-display text-lg font-bold">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-primary text-primary-foreground shadow-glow">
              <Wrench className="h-4 w-4" />
            </span>
            MobileMechanic
          </Link>
          <p className="mt-4 max-w-sm text-sm text-muted-foreground">
            Premium on-demand car care. Certified mechanics at your driveway in minutes — track them live, pay securely, drive happy.
          </p>
          <div className="mt-5 flex items-center gap-2">
            {[Twitter, Facebook, Instagram, Linkedin].map((Icon, i) => (
              <a
                key={i}
                href="#"
                className="grid h-9 w-9 place-items-center rounded-full border border-border bg-surface-elevated text-muted-foreground transition-colors hover:text-foreground"
                aria-label="social"
              >
                <Icon className="h-4 w-4" />
              </a>
            ))}
          </div>
        </div>

        {cols.map((c) => (
          <div key={c.title}>
            <div className="text-sm font-semibold text-foreground">{c.title}</div>
            <ul className="mt-4 space-y-2">
              {c.links.map((l) => (
                <li key={l.label}>
                  <Link to={l.to} className="text-sm text-muted-foreground transition-colors hover:text-foreground">
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t border-border">
        <div className="container-page flex flex-col items-center justify-between gap-3 py-5 text-xs text-muted-foreground md:flex-row">
          <div>© {new Date().getFullYear()} MobileMechanic. All rights reserved.</div>
          <div className="flex items-center gap-4">
            <a href="#" className="hover:text-foreground">Privacy</a>
            <a href="#" className="hover:text-foreground">Terms</a>
            <a href="#" className="hover:text-foreground">Security</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
