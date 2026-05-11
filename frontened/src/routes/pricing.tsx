import { createFileRoute, Link } from "@tanstack/react-router";
import { Check, Sparkles } from "lucide-react";
import { Reveal, SectionHeader } from "@/components/site/Section";

export const Route = createFileRoute("/pricing")({
  head: () => ({
    meta: [
      { title: "Pricing — MobileMechanic" },
      { name: "description", content: "Simple, transparent pricing. Pay-per-service or unlock more with MobilePlus." },
      { property: "og:title", content: "MobileMechanic Pricing" },
      { property: "og:description", content: "Pay-per-service or subscribe for premium perks." },
    ],
  }),
  component: PricingPage,
});

const tiers = [
  {
    name: "Pay as you go",
    price: "Free",
    note: "No subscription. Pay per service.",
    features: ["Standard pricing", "Same-day booking", "In-app payments", "Live tracking"],
    cta: "Get started",
  },
  {
    name: "Mobile Plus",
    price: "₨ 999",
    note: "/month · cancel anytime",
    featured: true,
    features: ["10% off every service", "Priority dispatch", "Free roadside SOS x2/mo", "Family vehicle profiles"],
    cta: "Start Plus",
  },
  {
    name: "Fleet",
    price: "Custom",
    note: "For 5+ vehicles",
    features: ["Dedicated account manager", "Volume discounts", "Monthly invoicing", "Custom SLAs"],
    cta: "Talk to sales",
  },
];

function PricingPage() {
  return (
    <div>
      <section className="bg-gradient-hero">
        <div className="container-page py-16 md:py-24">
          <SectionHeader
            eyebrow="Pricing"
            title={<>Simple. <span className="text-gradient-primary">Transparent.</span> No surprises.</>}
            description="Quotes are upfront, before you book. Pay only for what you use, or unlock perks with Plus."
          />
        </div>
      </section>

      <section className="container-page py-16">
        <div className="grid gap-6 md:grid-cols-3">
          {tiers.map((t) => (
            <Reveal key={t.name}>
              <div
                className={`relative h-full rounded-3xl border p-8 shadow-soft transition-all ${
                  t.featured
                    ? "border-primary bg-gradient-primary text-primary-foreground shadow-glow"
                    : "border-border bg-surface-elevated"
                }`}
              >
                {t.featured && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-background px-3 py-1 text-xs font-semibold text-foreground">
                    <Sparkles className="-mt-0.5 mr-1 inline h-3 w-3 text-primary" /> Most popular
                  </span>
                )}
                <div className={`text-sm font-semibold ${t.featured ? "opacity-90" : "text-muted-foreground"}`}>{t.name}</div>
                <div className="mt-3 flex items-baseline gap-1">
                  <div className="text-4xl font-bold tracking-tight">{t.price}</div>
                  <div className={`text-sm ${t.featured ? "opacity-90" : "text-muted-foreground"}`}>{t.note}</div>
                </div>
                <ul className="mt-6 space-y-3">
                  {t.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm">
                      <Check className={`h-4 w-4 ${t.featured ? "" : "text-primary"}`} /> {f}
                    </li>
                  ))}
                </ul>
                <Link
                  to="/signup"
                  className={`mt-8 inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-semibold ${
                    t.featured ? "bg-background text-foreground hover:opacity-95" : "bg-gradient-primary text-primary-foreground shadow-glow"
                  }`}
                >
                  {t.cta}
                </Link>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      <section className="bg-surface py-16">
        <div className="container-page rounded-3xl border border-border bg-surface-elevated p-8 text-center md:p-12">
          <h3 className="text-2xl font-bold">Have a fleet?</h3>
          <p className="mx-auto mt-2 max-w-xl text-muted-foreground">
            From 5 cars to 5,000 — we'll design a custom maintenance program that keeps your fleet on the road.
          </p>
          <Link to="/contact" className="mt-5 inline-flex items-center gap-2 rounded-full bg-gradient-primary px-5 py-3 text-sm font-semibold text-primary-foreground shadow-glow">
            Talk to sales
          </Link>
        </div>
      </section>
    </div>
  );
}
